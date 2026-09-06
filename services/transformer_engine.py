"""
services/transformer_engine.py
原生数学 Transformer 架构与矩阵变换引擎。
纯 NumPy 实现，完全独立于外部云端 API。
包含：
1. 多头因果自注意力机制 (Multi-Head Causal Self-Attention, d=768, h=12)
2. 旋转位置编码 (Rotary Position Embedding, RoPE)
3. 均方根层归一化 (RMSNorm)
4. SwiGLU 门控前馈网络 (SwiGLU FFN)
5. 3D Valence-Arousal-Dominance (VAD) 情感仿射矩阵投影
6. SVD 奇异值分解与注意力矩阵遥测分析
7. Top-p (Nucleus) / Top-k / 温度缩放概率采样器
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("zhiyuxing.transformer_engine")


@dataclass
class TransformerConfig:
    vocab_size: int = 4096
    d_model: int = 768
    num_heads: int = 12
    num_layers: int = 6
    d_ff: int = 2048
    max_seq_len: int = 512
    rope_theta: float = 10000.0
    eps: float = 1e-6
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40


def silu(x: np.ndarray) -> np.ndarray:
    """SiLU / Swish 激活函数: x * sigmoid(x)"""
    return x / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))


def rms_norm(x: np.ndarray, weight: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """RMSNorm 均方根层归一化。"""
    # x: (..., d_model)
    variance = np.mean(x ** 2, axis=-1, keepdims=True)
    normed = x * (1.0 / np.sqrt(variance + eps))
    return normed * weight


def apply_rotary_pos_emb(x: np.ndarray, seq_pos: int, head_dim: int, theta: float = 10000.0) -> np.ndarray:
    """
    对 (seq_len, head_dim) 应用 RoPE 旋转位置编码。
    """
    seq_len = x.shape[0]
    out = np.zeros_like(x)
    positions = np.arange(seq_pos, seq_pos + seq_len)[:, None]  # (seq_len, 1)
    dim_indices = np.arange(0, head_dim, 2)[None, :]  # (1, head_dim // 2)
    freqs = 1.0 / (theta ** (dim_indices / head_dim))
    angles = positions * freqs  # (seq_len, head_dim // 2)

    cos_theta = np.cos(angles)
    sin_theta = np.sin(angles)

    x_even = x[:, 0::2]
    x_odd = x[:, 1::2]

    out[:, 0::2] = x_even * cos_theta - x_odd * sin_theta
    out[:, 1::2] = x_even * sin_theta + x_odd * cos_theta
    return out


class MultiHeadAttention:
    """多头因果自注意力层，支持 RoPE 与因果掩码。"""

    def __init__(self, config: TransformerConfig, seed: int = 42):
        self.config = config
        self.d_model = config.d_model
        self.num_heads = config.num_heads
        self.head_dim = config.d_model // config.num_heads
        assert self.head_dim * self.num_heads == self.d_model, "d_model must be divisible by num_heads"

        rng = np.random.default_rng(seed)
        scale = 1.0 / math.sqrt(self.d_model)
        self.wq = rng.normal(0.0, scale, (self.d_model, self.d_model)).astype(np.float32)
        self.wk = rng.normal(0.0, scale, (self.d_model, self.d_model)).astype(np.float32)
        self.wv = rng.normal(0.0, scale, (self.d_model, self.d_model)).astype(np.float32)
        self.wo = rng.normal(0.0, scale, (self.d_model, self.d_model)).astype(np.float32)

    def forward(
        self, x: np.ndarray, start_pos: int = 0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        x: (seq_len, d_model)
        返回: (output: (seq_len, d_model), attention_probs: (num_heads, seq_len, seq_len))
        """
        seq_len, _ = x.shape
        q = x @ self.wq  # (seq_len, d_model)
        k = x @ self.wk
        v = x @ self.wv

        # Reshape to (num_heads, seq_len, head_dim)
        q = q.reshape(seq_len, self.num_heads, self.head_dim).transpose(1, 0, 2)
        k = k.reshape(seq_len, self.num_heads, self.head_dim).transpose(1, 0, 2)
        v = v.reshape(seq_len, self.num_heads, self.head_dim).transpose(1, 0, 2)

        # Apply RoPE per head
        for h in range(self.num_heads):
            q[h] = apply_rotary_pos_emb(q[h], start_pos, self.head_dim, self.config.rope_theta)
            k[h] = apply_rotary_pos_emb(k[h], start_pos, self.head_dim, self.config.rope_theta)

        # Scaled dot-product: (num_heads, seq_len, head_dim) @ (num_heads, head_dim, seq_len)
        scores = (q @ k.transpose(0, 2, 1)) / math.sqrt(self.head_dim)

        # Causal mask: upper triangle set to -inf
        mask = np.triu(np.ones((seq_len, seq_len), dtype=bool), k=1)
        scores[:, mask] = -1e9

        # Softmax over last axis
        scores_max = np.max(scores, axis=-1, keepdims=True)
        exp_scores = np.exp(scores - scores_max)
        attn_probs = exp_scores / (np.sum(exp_scores, axis=-1, keepdims=True) + 1e-9)

        # Weighted sum: (num_heads, seq_len, seq_len) @ (num_heads, seq_len, head_dim)
        context = attn_probs @ v  # (num_heads, seq_len, head_dim)
        context = context.transpose(1, 0, 2).reshape(seq_len, self.d_model)

        output = context @ self.wo
        return output, attn_probs


class SwiGLUFeedForward:
    """SwiGLU 门控前馈网络层。"""

    def __init__(self, config: TransformerConfig, seed: int = 42):
        self.config = config
        d_model = config.d_model
        d_ff = config.d_ff
        rng = np.random.default_rng(seed)
        scale = 1.0 / math.sqrt(d_model)

        self.w_gate = rng.normal(0.0, scale, (d_model, d_ff)).astype(np.float32)
        self.w_up = rng.normal(0.0, scale, (d_model, d_ff)).astype(np.float32)
        self.w_down = rng.normal(0.0, 1.0 / math.sqrt(d_ff), (d_ff, d_model)).astype(np.float32)

    def forward(self, x: np.ndarray) -> np.ndarray:
        gate = silu(x @ self.w_gate)
        up = x @ self.w_up
        return (gate * up) @ self.w_down


class TransformerBlock:
    """单层 Transformer 模块：RMSNorm -> MHA -> RMSNorm -> SwiGLU。"""

    def __init__(self, config: TransformerConfig, layer_idx: int):
        self.config = config
        self.layer_idx = layer_idx
        self.attn_norm = np.ones(config.d_model, dtype=np.float32)
        self.ffn_norm = np.ones(config.d_model, dtype=np.float32)
        self.attn = MultiHeadAttention(config, seed=42 + layer_idx * 17)
        self.ffn = SwiGLUFeedForward(config, seed=100 + layer_idx * 17)

    def forward(self, x: np.ndarray, start_pos: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        # Prenorm Attention
        normed_x = rms_norm(x, self.attn_norm, self.config.eps)
        attn_out, attn_probs = self.attn.forward(normed_x, start_pos)
        x = x + attn_out

        # Prenorm FFN
        normed_x2 = rms_norm(x, self.ffn_norm, self.config.eps)
        ffn_out = self.ffn.forward(normed_x2)
        x = x + ffn_out
        return x, attn_probs


class VADEmotionProjector:
    """
    3D Valence-Arousal-Dominance (VAD) 情感仿射矩阵投影器。
    将 Transformer 隐层输出 h (d=768) 仿射变换至三维情感状态空间：
    - Valence (愉悦/效价): [-1.0, 1.0] (负向悲伤痛苦 ~ 正向平静喜悦)
    - Arousal (激活/唤醒): [0.0, 1.0] (迟钝麻木 ~ 高度惊恐焦虑/亢奋)
    - Dominance (掌控/胜任): [-1.0, 1.0] (失控无助被动 ~ 掌控自主自信)
    """

    def __init__(self, d_model: int = 768, seed: int = 777):
        rng = np.random.default_rng(seed)
        # 仿射变换权重: (d_model, 3)
        self.w = rng.normal(0.0, 0.02, (d_model, 3)).astype(np.float32)
        self.b = np.array([0.0, 0.5, 0.0], dtype=np.float32)

        # 心理关键词与 VAD 锚点偏置矩阵 (用于语义对齐校准)
        self._anchor_keywords: Dict[str, Tuple[float, float, float]] = {
            "崩溃": (-0.85, 0.90, -0.75),
            "绝望": (-0.90, 0.70, -0.85),
            "焦虑": (-0.60, 0.85, -0.50),
            "惊恐": (-0.80, 0.95, -0.80),
            "拖延": (-0.40, 0.40, -0.60),
            "疲惫": (-0.50, 0.20, -0.40),
            "平静": (0.70, 0.15, 0.60),
            "接纳": (0.65, 0.20, 0.55),
            "自信": (0.80, 0.50, 0.85),
            "掌控": (0.75, 0.45, 0.80),
            "希望": (0.85, 0.60, 0.70),
            "释然": (0.70, 0.25, 0.65),
        }

    def project(self, hidden_state: np.ndarray, context_text: str = "") -> Dict[str, float]:
        """
        hidden_state: (d_model,)
        返回: {"valence": float, "arousal": float, "dominance": float, "label": str}
        """
        raw_vad = hidden_state @ self.w + self.b
        v = float(np.tanh(raw_vad[0]))
        a = float(1.0 / (1.0 + np.exp(-raw_vad[1])))
        d = float(np.tanh(raw_vad[2]))

        # 上下文关键词锚点融合校准
        if context_text:
            matched_anchors = []
            for kw, anchor_vals in self._anchor_keywords.items():
                if kw in context_text:
                    matched_anchors.append(anchor_vals)
            if matched_anchors:
                mean_anchor = np.mean(matched_anchors, axis=0)
                # 0.5 模型隐层 + 0.5 临床语义锚点
                v = float(np.clip(0.5 * v + 0.5 * mean_anchor[0], -1.0, 1.0))
                a = float(np.clip(0.5 * a + 0.5 * mean_anchor[1], 0.0, 1.0))
                d = float(np.clip(0.5 * d + 0.5 * mean_anchor[2], -1.0, 1.0))

        # 临床情感区间判定
        if a > 0.65 and v < -0.3:
            label = "急性高危焦虑/应激" if d < -0.4 else "激越防御态"
        elif a <= 0.4 and v < -0.3:
            label = "抑郁冷淡/动力枯竭"
        elif v >= 0.3 and d >= 0.2:
            label = "自律成长/积极反思"
        elif v >= 0.4 and a <= 0.35:
            label = "安详平静/稳态接纳"
        else:
            label = "轻度情绪扰动/认知重组中"

        return {
            "valence": round(v, 4),
            "arousal": round(a, 4),
            "dominance": round(d, 4),
            "label": label,
        }


class TransformerEngine:
    """
    综合本地 Transformer 神经网络推理与矩阵变换引擎。
    提供离线自注意力推理、VAD 情感仿射投影、SVD 奇异值分解遥测。
    """

    def __init__(self, config: Optional[TransformerConfig] = None):
        self.config = config or TransformerConfig()
        np.random.seed(42)

        # 词嵌入矩阵: vocab_size x d_model
        self.token_embeddings = np.random.normal(
            0.0, 0.02, (self.config.vocab_size, self.config.d_model)
        ).astype(np.float32)

        # Transformer 堆叠层
        self.layers = [TransformerBlock(self.config, idx) for idx in range(self.config.num_layers)]
        self.final_norm = np.ones(self.config.d_model, dtype=np.float32)

        # 输出词表投影矩阵 (LM Head)
        self.lm_head = np.random.normal(
            0.0, 1.0 / math.sqrt(self.config.d_model), (self.config.d_model, self.config.vocab_size)
        ).astype(np.float32)

        # 情感矩阵投影器
        self.vad_projector = VADEmotionProjector(self.config.d_model)

        # 简易字符/哈希 Tokenizer 映射
        self._vocab_to_id: Dict[str, int] = {"<pad>": 0, "<bos>": 1, "<eos>": 2, "<unk>": 3}
        self._id_to_vocab: Dict[int, str] = {0: "<pad>", 1: "<bos>", 2: "<eos>", 3: "<unk>"}

    def tokenize(self, text: str) -> List[int]:
        """轻量分词将文本转为 token IDs (带哈希散列映射)。"""
        tokens = [1]  # <bos>
        for ch in text:
            if ch not in self._vocab_to_id:
                if len(self._vocab_to_id) < self.config.vocab_size:
                    new_id = len(self._vocab_to_id)
                    self._vocab_to_id[ch] = new_id
                    self._id_to_vocab[new_id] = ch
                else:
                    new_id = 4 + (abs(hash(ch)) % (self.config.vocab_size - 4))
                tokens.append(new_id)
            else:
                tokens.append(self._vocab_to_id[ch])
        return tokens[: self.config.max_seq_len]

    def forward(self, token_ids: List[int]) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        前向传播计算。
        返回: (last_hidden_state: (seq_len, d_model), all_layers_attn: List[(heads, seq_len, seq_len)])
        """
        seq_len = len(token_ids)
        if seq_len == 0:
            token_ids = [1]
            seq_len = 1

        # 查表获取输入词向量: (seq_len, d_model)
        x = self.token_embeddings[token_ids].copy()

        all_layer_attns = []
        for layer in self.layers:
            x, attn_probs = layer.forward(x, start_pos=0)
            all_layer_attns.append(attn_probs)

        # 最终层归一化
        x = rms_norm(x, self.final_norm, self.config.eps)
        return x, all_layer_attns

    def compute_svd_telemetry(self, matrix: np.ndarray, top_k: int = 5) -> Dict[str, Any]:
        """
        对给定矩阵（如最终隐层输出或注意力矩阵）进行 SVD 奇异值分解，
        计算能量谱分布、有效秩 (Effective Rank) 及前 k 个奇异值。
        """
        try:
            U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
            total_energy = float(np.sum(S ** 2))
            singular_values = [round(float(s), 4) for s in S[:top_k]]
            energy_ratios = [round(float(s ** 2 / (total_energy + 1e-9)), 4) for s in S[:top_k]]

            # Shannon 有效秩熵
            p = (S ** 2) / (total_energy + 1e-9)
            entropy = -float(np.sum(p * np.log(p + 1e-12)))
            effective_rank = round(math.exp(entropy), 2)

            return {
                "top_singular_values": singular_values,
                "energy_ratios": energy_ratios,
                "effective_rank": effective_rank,
                "matrix_shape": list(matrix.shape),
            }
        except Exception as e:
            logger.warning(f"SVD computation failed: {e}")
            return {"error": str(e), "matrix_shape": list(matrix.shape)}

    def sample_logits(
        self,
        logits: np.ndarray,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
    ) -> int:
        """
        Top-p (Nucleus) + Top-k + 温度截断采样。
        """
        temperature = max(temperature, 1e-4)
        scaled_logits = logits / temperature

        # Top-k 截断
        if top_k > 0 and top_k < len(scaled_logits):
            top_k_indices = np.argpartition(scaled_logits, -top_k)[-top_k:]
            mask = np.ones_like(scaled_logits, dtype=bool)
            mask[top_k_indices] = False
            scaled_logits[mask] = -1e9

        # Softmax
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        probs = exp_logits / (np.sum(exp_logits) + 1e-9)

        # Top-p 截断
        sorted_indices = np.argsort(probs)[::-1]
        sorted_probs = probs[sorted_indices]
        cumulative_probs = np.cumsum(sorted_probs)

        # 移除累积概率超过 top_p 的多余 token
        cutoff = np.searchsorted(cumulative_probs, top_p)
        valid_indices = sorted_indices[: cutoff + 1]
        valid_probs = probs[valid_indices]
        valid_probs /= np.sum(valid_probs) + 1e-9

        return int(np.random.choice(valid_indices, p=valid_probs))

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        对输入文本执行完整 Transformer 推理并导出遥测数据：
        - 隐层特征与 SVD 能量谱
        - 3D VAD 情感坐标与临床状态
        - 各注意力头平均权重与注意力熵
        """
        token_ids = self.tokenize(text)
        hidden_states, all_layer_attns = self.forward(token_ids)

        # 最后一层隐层均值向量: (d_model,)
        mean_hidden = np.mean(hidden_states, axis=0)

        # 3D VAD 仿射投影
        vad_metrics = self.vad_projector.project(mean_hidden, text)

        # 最终层注意力矩阵分析
        last_attn = all_layer_attns[-1]  # (num_heads, seq_len, seq_len)
        mean_attn_map = np.mean(last_attn, axis=0)  # (seq_len, seq_len)

        # SVD 分析
        svd_metrics = self.compute_svd_telemetry(mean_attn_map)

        # 注意力熵计算 (衡量注意力聚焦度)
        attn_entropy = -float(np.mean(mean_attn_map * np.log(mean_attn_map + 1e-9)))

        return {
            "token_count": len(token_ids),
            "d_model": self.config.d_model,
            "num_layers": self.config.num_layers,
            "num_heads": self.config.num_heads,
            "vad_emotion": vad_metrics,
            "svd_telemetry": svd_metrics,
            "attention_entropy": round(attn_entropy, 4),
            "head_max_activations": [round(float(np.max(last_attn[h])), 4) for h in range(min(self.config.num_heads, 6))],
        }


# 全局单例
_global_transformer: Optional[TransformerEngine] = None


def get_transformer_engine() -> TransformerEngine:
    global _global_transformer
    if _global_transformer is None:
        _global_transformer = TransformerEngine()
    return _global_transformer
