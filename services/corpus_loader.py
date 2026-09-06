"""
services/corpus_loader.py
心理与临床微行动结构化知识库检索与索引服务。
支持 BM25 稀疏检索 + 稠密矩阵语义投影混合召回。
"""

from __future__ import annotations

import json
import logging
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("zhiyuxing.corpus_loader")


class CorpusItem:
    """标准化的知识库检索单元。"""

    def __init__(
        self,
        item_id: str,
        category: str,
        title: str,
        content: str,
        raw_data: Dict[str, Any],
        keywords: Optional[List[str]] = None,
    ):
        self.item_id = item_id
        self.category = category
        self.title = title
        self.content = content
        self.raw_data = raw_data
        self.keywords = keywords or []
        self.vector: Optional[np.ndarray] = None


class PsychologyCorpusLoader:
    """
    心理知识库加载器与检索索引器。
    从 data/psychology_corpus/ 自动载入所有循证结构化数据。
    """

    def __init__(self, corpus_dir: Optional[Path] = None, embed_dim: int = 128):
        if corpus_dir is None:
            self.corpus_dir = Path(__file__).resolve().parent.parent / "data" / "psychology_corpus"
        else:
            self.corpus_dir = Path(corpus_dir)

        self.embed_dim = embed_dim
        self.items: List[CorpusItem] = []
        self._term_doc_freq: Dict[str, int] = {}
        self._avg_doc_len: float = 0.0
        self._doc_tokens: List[List[str]] = []
        self._projection_matrix: Optional[np.ndarray] = None
        self._dense_matrix: Optional[np.ndarray] = None

        self.load_corpus()

    def _tokenize(self, text: str) -> List[str]:
        """中英文混合轻量分词：支持中文单字/双字 ngram 及英文词条。"""
        text = text.lower()
        # 提取英文单词
        en_words = re.findall(r"[a-z0-9_]+", text)
        # 提取中文字符
        cn_chars = re.findall(r"[\u4e00-\u9fa5]", text)
        # 生成中文双字 bigram
        cn_bigrams = [cn_chars[i] + cn_chars[i + 1] for i in range(len(cn_chars) - 1)] if len(cn_chars) > 1 else []
        return en_words + cn_chars + cn_bigrams

    def load_corpus(self) -> None:
        """加载语料目录下的全部 JSON 数据。"""
        self.items.clear()
        if not self.corpus_dir.exists():
            logger.warning(f"Corpus directory {self.corpus_dir} does not exist.")
            return

        json_files = list(self.corpus_dir.glob("*.json"))
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._parse_file_data(data, file_path.stem)
            except Exception as e:
                logger.error(f"Failed to parse corpus file {file_path}: {e}")

        self._build_sparse_index()
        self._build_dense_index()
        logger.info(f"Loaded {len(self.items)} psychology corpus items from {len(json_files)} files.")

    def _parse_file_data(self, data: Any, file_stem: str) -> None:
        """解析不同结构的心理语料 JSON，兼容列表与字典顶层结构。"""
        if isinstance(data, list):
            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    continue
                # 认知扭曲条目
                if "distortion" in item:
                    d_id = item.get("id", f"CD_{idx}")
                    name = item.get("distortion", "认知偏差")
                    sub_cat = item.get("category", file_stem)
                    content = (
                        f"认知偏差: {name}. 类型: {sub_cat}. "
                        f"触发自动想法: {item.get('trigger_thought', '')}. "
                        f"认知缺陷: {item.get('cognitive_flaw', '')}. "
                        f"客观事实反驳: {' '.join(item.get('counter_evidence', []))}. "
                        f"替代平衡思维: {item.get('balanced_thought', '')}. "
                        f"微实验: {item.get('micro_experiment', '')}"
                    )
                    keywords = [name, sub_cat, "认知扭曲", "思维陷阱"]
                    self.items.append(CorpusItem(d_id, "cbt_distortions", name, content, item, keywords))
                # 临床或职场案例
                elif "clinical_assessment" in item or "symptoms" in item:
                    c_id = item.get("id", f"CASE_{idx}")
                    title = item.get("title", "干预案例")
                    symptoms = " ".join(item.get("symptoms", []))
                    protocol = " ".join(item.get("intervention_protocol", []))
                    content = (
                        f"案例: {title}. 症状表现: {symptoms}. "
                        f"临床评估: {item.get('clinical_assessment', '')}. "
                        f"循证干预方案: {protocol}. "
                        f"沟通话术: {item.get('workplace_scripts', '')}"
                    )
                    keywords = item.get("symptoms", []) + [title, "案例", "应对策略"]
                    self.items.append(CorpusItem(c_id, "workplace_burnout", title, content, item, keywords))
            return

        if not isinstance(data, dict):
            return

        category = data.get("category", file_stem)

        # 1. 认知扭曲 distortions
        if "distortions" in data:
            for item in data["distortions"]:
                d_id = item.get("id", f"DIS_{len(self.items)}")
                name = item.get("name", "认知偏差")
                content = (
                    f"名称: {name} ({item.get('english_name', '')}). "
                    f"定义: {item.get('definition', '')}. "
                    f"触发范例: {' '.join(item.get('trigger_thoughts', []))}. "
                    f"反思提问: {' '.join(item.get('cbt_reframing_questions', []))}. "
                    f"替代平衡思维: {item.get('balanced_alternative_thought', '')}"
                )
                keywords = item.get("keywords", []) + [name]
                self.items.append(CorpusItem(d_id, category, name, content, item, keywords))

        # 2. 案例 cases (工作职场/学业成长)
        elif "cases" in data:
            for item in data["cases"]:
                c_id = item.get("id", f"CASE_{len(self.items)}")
                title = item.get("title", "干预案例")
                content = (
                    f"案例: {title}. 症状: {' '.join(item.get('primary_symptoms', []))}. "
                    f"病理分析: {item.get('root_cause_analysis', '')}. "
                    f"干预策略: {json.dumps(item.get('intervention_strategy', {}), ensure_ascii=False)}. "
                    f"咨询师回应示范: {item.get('counselor_script', '')}"
                )
                keywords = item.get("keywords", []) + [title]
                self.items.append(CorpusItem(c_id, category, title, content, item, keywords))

        # 3. 临床量表 scales
        elif "scales" in data:
            for item in data["scales"]:
                s_id = item.get("scale_id", f"SCALE_{len(self.items)}")
                name = item.get("scale_name", "临床量表")
                content = (
                    f"量表: {name}. 题目数: {item.get('total_items', 0)}. "
                    f"分级标准: {json.dumps(item.get('severity_tiers', []), ensure_ascii=False)}. "
                    f"临床建议: {json.dumps(item.get('clinical_recommendation', ''), ensure_ascii=False)}"
                )
                keywords = [s_id, name, "量表", "测评", "临床诊断"]
                self.items.append(CorpusItem(s_id, category, name, content, item, keywords))

        # 4. 微行动 micro actions
        elif "actions" in data:
            for item in data["actions"]:
                a_id = item.get("id", f"ACT_{len(self.items)}")
                name = item.get("name", "身心微行动")
                content = (
                    f"微行动: {name}. 适应症: {' '.join(item.get('target_symptom', []))}. "
                    f"神经生理学机制: {item.get('neurobiological_mechanism', '')}. "
                    f"执行步骤: {' '.join(item.get('steps', []))}"
                )
                keywords = item.get("target_symptom", []) + [name, item.get("category", "action")]
                self.items.append(CorpusItem(a_id, category, name, content, item, keywords))

    def _build_sparse_index(self) -> None:
        """构建轻量 BM25 词频统计。"""
        self._term_doc_freq.clear()
        self._doc_tokens.clear()
        total_len = 0

        for item in self.items:
            tokens = self._tokenize(item.title + " " + item.content + " " + " ".join(item.keywords))
            self._doc_tokens.append(tokens)
            total_len += len(tokens)
            unique_terms = set(tokens)
            for term in unique_terms:
                self._term_doc_freq[term] = self._term_doc_freq.get(term, 0) + 1

        self._avg_doc_len = total_len / max(len(self.items), 1)

    def _build_dense_index(self) -> None:
        """利用哈希特征与正交随机矩阵构建伪稠密矩阵向量空间，加速向量内积计算。"""
        if not self.items:
            return

        np.random.seed(42)
        vocab_hash_buckets = 512
        # 生成正交投影矩阵: 512 -> embed_dim (128)
        raw_mat = np.random.randn(vocab_hash_buckets, self.embed_dim)
        q, _ = np.linalg.qr(raw_mat)
        self._projection_matrix = q

        vectors = []
        for tokens in self._doc_tokens:
            vec = np.zeros(vocab_hash_buckets, dtype=np.float32)
            for token in tokens:
                bucket = abs(hash(token)) % vocab_hash_buckets
                vec[bucket] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 1e-6:
                vec /= norm
            # 投影到潜向量空间
            projected = vec @ self._projection_matrix
            p_norm = np.linalg.norm(projected)
            if p_norm > 1e-6:
                projected /= p_norm
            vectors.append(projected)

        self._dense_matrix = np.vstack(vectors) if vectors else None
        for idx, item in enumerate(self.items):
            item.vector = self._dense_matrix[idx] if self._dense_matrix is not None else None

    def _bm25_score(self, query_tokens: List[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        """计算单文档 BM25 得分。"""
        doc_tokens = self._doc_tokens[doc_idx]
        doc_len = len(doc_tokens)
        score = 0.0
        total_docs = len(self.items)

        # 统计文档内词频
        doc_counts: Dict[str, int] = {}
        for t in doc_tokens:
            doc_counts[t] = doc_counts.get(t, 0) + 1

        for qt in query_tokens:
            if qt not in self._term_doc_freq:
                continue
            df = self._term_doc_freq[qt]
            idf = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))
            tf = doc_counts.get(qt, 0)
            if tf > 0:
                tf_norm = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (doc_len / max(self._avg_doc_len, 1.0))))
                score += idf * tf_norm
        return score

    def search(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        混合检索：BM25 文本匹配 + 稠密矩阵余弦打分。
        """
        if not self.items:
            return []

        query_tokens = self._tokenize(query)
        bm25_scores = np.zeros(len(self.items), dtype=np.float32)
        for i in range(len(self.items)):
            bm25_scores[i] = self._bm25_score(query_tokens, i)

        # 最大归一化
        max_bm25 = np.max(bm25_scores) if len(bm25_scores) > 0 else 0
        if max_bm25 > 1e-6:
            bm25_scores /= max_bm25

        # 稠密矩阵打分
        dense_scores = np.zeros(len(self.items), dtype=np.float32)
        if self._dense_matrix is not None and self._projection_matrix is not None:
            vocab_hash_buckets = 512
            q_vec = np.zeros(vocab_hash_buckets, dtype=np.float32)
            for token in query_tokens:
                bucket = abs(hash(token)) % vocab_hash_buckets
                q_vec[bucket] += 1.0
            norm = np.linalg.norm(q_vec)
            if norm > 1e-6:
                q_vec /= norm
                q_proj = q_vec @ self._projection_matrix
                p_norm = np.linalg.norm(q_proj)
                if p_norm > 1e-6:
                    q_proj /= p_norm
                    # 矩阵乘法计算所有文档的余弦相似度: (N, d) @ (d,) -> (N,)
                    dense_scores = self._dense_matrix @ q_proj

        # 混合打分: 0.6 * BM25 + 0.4 * 稠密语义
        combined = 0.6 * bm25_scores + 0.4 * np.clip(dense_scores, 0.0, 1.0)

        # 过滤与排序
        candidate_indices = np.argsort(combined)[::-1]
        results = []
        for idx in candidate_indices:
            item = self.items[idx]
            if category_filter and item.category != category_filter:
                continue
            if combined[idx] <= 0.01 and len(results) >= 1:
                break
            results.append({
                "item_id": item.item_id,
                "category": item.category,
                "title": item.title,
                "content": item.content,
                "score": float(round(combined[idx], 4)),
                "raw_data": item.raw_data,
            })
            if len(results) >= top_k:
                break

        return results

    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息。"""
        categories: Dict[str, int] = {}
        for item in self.items:
            categories[item.category] = categories.get(item.category, 0) + 1
        return {
            "total_items": len(self.items),
            "categories": categories,
            "embed_dim": self.embed_dim,
            "sparse_terms_indexed": len(self._term_doc_freq),
        }


# 全局单例
_global_corpus: Optional[PsychologyCorpusLoader] = None


def get_psychology_corpus() -> PsychologyCorpusLoader:
    global _global_corpus
    if _global_corpus is None:
        _global_corpus = PsychologyCorpusLoader()
    return _global_corpus
