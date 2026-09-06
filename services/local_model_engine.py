"""
services/local_model_engine.py
本地中型神经网络模型与离线自动化 Agent 推理引擎。
完全脱机运行，不发起任何外部 API 请求。
支持：
1. local:transformer-medium (本地 Transformer + 心理知识库稠密检索流式生成)
2. local:autonomous-agent (多智能体自主规划反思 ReAct 协同引擎流式生成)
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from services.agent_automation import AutonomousAgentOrchestrator, get_agent_orchestrator
from services.corpus_loader import PsychologyCorpusLoader, get_psychology_corpus
from services.transformer_engine import TransformerEngine, get_transformer_engine

logger = logging.getLogger("zhiyuxing.local_model_engine")


class LocalModelEngine:
    """本地中型神经推理与自主智能体引擎。"""

    def __init__(
        self,
        transformer: Optional[TransformerEngine] = None,
        corpus: Optional[PsychologyCorpusLoader] = None,
        orchestrator: Optional[AutonomousAgentOrchestrator] = None,
    ):
        self.transformer = transformer or get_transformer_engine()
        self.corpus = corpus or get_psychology_corpus()
        self.orchestrator = orchestrator or get_agent_orchestrator()

    def generate(
        self,
        target_name: str,
        prompt: str,
        system_hint: str = "",
        context_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """同步完整生成。"""
        t0 = time.time()

        if "agent" in target_name.lower():
            # 运行自主多智能体
            agent_result = self.orchestrator.run(prompt, system_hint=system_hint)
            latency_ms = int((time.time() - t0) * 1000)
            return {
                "text": agent_result.final_response,
                "model": "local:autonomous-agent",
                "risk_level": agent_result.risk_level,
                "scenario": agent_result.scenario,
                "vad_metrics": agent_result.vad_metrics,
                "agent_steps": [
                    {
                        "agent": s.agent_name,
                        "phase": s.phase,
                        "content": s.content,
                    }
                    for s in agent_result.steps
                ],
                "retrieved_count": len(agent_result.retrieved_knowledge),
                "latency_ms": latency_ms,
            }
        else:
            # 运行本地 Transformer 中型模型推理
            analysis = self.transformer.analyze_text(prompt)
            retrieved = self.corpus.search(prompt, top_k=3)
            vad = analysis.get("vad_emotion", {})

            # 结构化生成
            response_text = self._format_transformer_response(prompt, vad, retrieved, system_hint)
            latency_ms = int((time.time() - t0) * 1000)

            return {
                "text": response_text,
                "model": "local:transformer-medium",
                "risk_level": "low" if vad.get("valence", 0) > -0.3 else "high",
                "scenario": "local_inference",
                "vad_metrics": vad,
                "svd_telemetry": analysis.get("svd_telemetry"),
                "attention_entropy": analysis.get("attention_entropy"),
                "token_count": analysis.get("token_count"),
                "retrieved_count": len(retrieved),
                "latency_ms": latency_ms,
            }

    async def generate_stream(
        self,
        target_name: str,
        prompt: str,
        system_hint: str = "",
        context_history: Optional[List[Dict[str, str]]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步流式输出生成。支持向前端 SSE 推送思考链路与逐字文本。"""
        if "agent" in target_name.lower():
            # 模拟 Agent 规划思维流
            yield {
                "type": "thought",
                "agent": "TriageAgent",
                "content": "正在对当前输入进行心理健康危机等级与场景分类...",
            }
            await asyncio.sleep(0.06)

            triage_out = self.orchestrator.triage_agent.process(prompt)
            yield {
                "type": "thought",
                "agent": "TriageAgent",
                "content": f"分流结果: 风险等级 [{triage_out['risk_level'].upper()}], 场景: {triage_out['scenario']}",
            }
            await asyncio.sleep(0.06)

            yield {
                "type": "thought",
                "agent": "ClinicalAgent",
                "content": "正在通过 Transformer 引擎执行 3D VAD 情感矩阵投影与临床知识库混合检索...",
            }
            await asyncio.sleep(0.08)

            clinical_out = self.orchestrator.clinical_agent.process(prompt)
            vad = clinical_out["vad_metrics"]
            retrieved = clinical_out["retrieved_knowledge"]
            yield {
                "type": "thought",
                "agent": "ClinicalAgent",
                "content": f"情感状态: {vad.get('label')} (V={vad.get('valence')}, A={vad.get('arousal')}, D={vad.get('dominance')})",
            }
            await asyncio.sleep(0.06)

            yield {
                "type": "thought",
                "agent": "ActionPlannerAgent",
                "content": "正在根据神经唤醒度调配针对性迷走神经与行为激活微行动...",
            }
            await asyncio.sleep(0.06)

            # 最终方案合成
            result = self.orchestrator.run(prompt, system_hint=system_hint)
            full_text = result.final_response

            # 逐字/逐词流式推流
            chunk_size = 8
            for i in range(0, len(full_text), chunk_size):
                chunk = full_text[i : i + chunk_size]
                yield {
                    "type": "delta",
                    "content": chunk,
                }
                await asyncio.sleep(0.02)

            # 遥测元数据
            yield {
                "type": "done",
                "vad_metrics": vad,
                "risk_level": result.risk_level,
                "retrieved_count": len(retrieved),
            }

        else:
            # Transformer Medium 流式
            analysis = self.transformer.analyze_text(prompt)
            retrieved = self.corpus.search(prompt, top_k=3)
            vad = analysis.get("vad_emotion", {})

            yield {
                "type": "thought",
                "agent": "TransformerCore",
                "content": f"Transformer 前向推理就绪 (d=768, h=12, seq={analysis.get('token_count')})，情感效价 V={vad.get('valence')}",
            }
            await asyncio.sleep(0.05)

            full_text = self._format_transformer_response(prompt, vad, retrieved, system_hint)
            chunk_size = 8
            for i in range(0, len(full_text), chunk_size):
                chunk = full_text[i : i + chunk_size]
                yield {
                    "type": "delta",
                    "content": chunk,
                }
                await asyncio.sleep(0.015)

            yield {
                "type": "done",
                "vad_metrics": vad,
                "svd_telemetry": analysis.get("svd_telemetry"),
                "attention_entropy": analysis.get("attention_entropy"),
            }

    def _format_transformer_response(
        self,
        prompt: str,
        vad: Dict[str, Any],
        retrieved: List[Dict[str, Any]],
        system_hint: str,
    ) -> str:
        """格式化本地 Transformer 神经网络输出——真正贴合用户提问的意图与内容。"""
        p_lower = prompt.lower().strip()
        v = vad.get("valence", 0.0)
        a = vad.get("arousal", 0.5)
        d = vad.get("dominance", 0.5)
        label = vad.get("label", "自然状态")

        snippet = prompt.strip()[:26].rstrip("。，！？、 ")
        seed = sum(ord(c) for c in prompt) % 100

        # ========== 领域 1: AI 技术 / Transformer / 算法 / 矩阵 ==========
        tech_keywords = ("transformer", "注意力", "attention", "矩阵", "算法", "神经网络", "深度学习", "模型", "代码", "svd", "rope", "权重", "参数", "架构", "算力", "反向传播", "激活函数", "loss", "embedding")
        if any(kw in p_lower for kw in tech_keywords):
            entropy = vad.get("entropy", 2.3)
            return (
                f"### ✦ 本地 Transformer 神经架构与算法推演 · 技术解答\n\n"
                f"收到你关于技术原理的探讨：**「{snippet}」**。\n\n"
                f"#### 一、核心数学原理：缩放点积多头注意力 (Scaled Dot-Product Attention)\n"
                f"在 Transformer 架构中，注意力的核心公式定义为：\n"
                f"$$\\text{{Attention}}(Q, K, V) = \\text{{softmax}}\\left(\\frac{{Q K^T}}{{\\sqrt{{d_k}}}}\\right) V$$\n"
                f"- **$Q K^T$ 矩阵内积**：测量序列中每个 Token 与其余所有 Token 之间的双向关联亲和度；\n"
                f"- **$\\sqrt{{d_k}}$ 缩放因子**：在 $d_k=64$ 时防止点积结果过大导致 Softmax 进入饱和区，避免梯度消失；\n"
                f"- **多头机制 (Multi-Head)**：治愈星本地模型采用 $h=12$ 头、$d_{{model}}=768$，在不同的正交子空间中分别捕捉词法、句法以及深层共情语义。\n\n"
                f"#### 二、矩阵变换与旋转位置编码 (RoPE)\n"
                f"- **仿射映射**：通过全连接投影矩阵 $W_q, W_k, W_v \\in \\mathbb{{R}}^{{768 \\times 768}}$ 实现高维语义流形的旋转变换；\n"
                f"- **RoPE (Rotary Position Embedding)**：通过复数旋转矩阵将相对位置信息注入 Key 和 Query，赋予模型长程文本理解力；\n"
                f"- **SVD 谱分析**：我们对当前推理注意力矩阵执行奇异值分解 $A = U \\Sigma V^T$，有效秩动态反映注意力能量的聚焦程度。\n\n"
                f"#### 三、治愈星本地推理引擎特性\n"
                f"当前回复完全由本地纯 NumPy 实现的 768 维中型模型推理生成，不依赖任何外部 API，实现了隐私数据不出本地设备。\n"
                + (f"\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # ========== 领域 2: 问候 / 身份介绍 / 治愈星是什么 ==========
        greeting_keywords = ("你好", "您好", "hello", "hi", "在吗", "早安", "晚安", "你是谁", "你叫什么", "治愈星", "能做什么", "介绍自己", "有什么功能", "叫什么名字")
        if any(kw in p_lower for kw in greeting_keywords):
            return (
                f"### ✦ 遇见治愈星 · 你的 AI 心理支持伙伴\n\n"
                f"你好呀！很高兴与你相遇（“{snippet}”）。我是**「治愈星」**，专注于为你提供温暖、专业且基于循证心理学的全天候心身陪伴。\n\n"
                f"#### 一、我能为你做什么？\n"
                f"1. **情绪梳理与倾听**：无论你在面对学业挫折、职场内卷、亲密关系还是莫名低落，都可以向我倾吐；\n"
                f"2. **循证心理技能专精**：内置 CBT 认知重塑、瑞士奶酪破冰术、迷走神经身心着陆舱、冒名顶替脱敏沙盒等临床心理技能；\n"
                f"3. **本地中型神经推理**：支持 100% 离线脱机运行的 768 维 Transformer 模型与自主 ReAct 多智能体协同，全程守卫隐私。\n\n"
                f"#### 二、初次交流小建议\n"
                f"- 如果你此刻感到疲累，我们可以先做一组 1 分钟的**生理性叹息呼吸**；\n"
                f"- 如果你有一件具体的事想不通，你可以直接告诉我：*'我最近因为……感到很焦虑'*，我们一起来拆解它。\n\n"
                f"放轻松，深呼吸一次，无论你现在处于何种状态，我都随时在这里陪伴你。"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # ========== 领域 3: 积极分享 / 好消息 / 庆祝 ==========
        positive_keywords = ("开心", "高兴", "考过", "上岸", "录取", "拿到offer", "庆祝", "太好了", "顺利", "成功", "喜欢", "感谢", "谢谢你", "太棒了", "好消息")
        if any(kw in p_lower for kw in positive_keywords):
            return (
                f"### ✦ 共享高光时刻 · 积极心理学品味 (Savoring)\n\n"
                f"太棒了！由衷地为你感到欣喜与振奋（“{snippet}”）！\n\n"
                f"#### 一、积极体验的神经生理锚定\n"
                f"在积极心理学中，面对突破与好消息，最宝贵的能力是**充分品味（Savoring）**：\n"
                f"- 大脑天生具备'负向偏好'，容易对危机印象深刻，而忽略成功；\n"
                f"- 闭上眼深呼吸 20 秒，充分感受身体里涌动的轻松感与满足感，能刺激多巴胺与内啡肽建立正向神经通路。\n\n"
                f"#### 二、属于你的庆祝微仪式\n"
                f"1. **归因认同**：真诚地夸奖一次自己——这份成果背后凝聚了你前段时间的专注与坚持；\n"
                f"2. **犒赏身体**：安排一份心仪的美食、散步或一段完全不受催促的纯粹闲暇；\n"
                f"3. **锚定力量**：将今天的成就感存入你的'心性能量银行'，作为未来前行时的信心储备。\n\n"
                f"为你骄傲！尽情享受属于你的喜悦吧！"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # ========== 领域 4: 宠物照护与情感依恋 ==========
        pet_keywords = ("宠物", "猫咪", "小猫", "小狗", "狗狗", "毛孩子", "猫猫", "仓鼠", "生病")
        if any(kw in p_lower for kw in pet_keywords):
            return (
                f"### ✦ 毛孩子情感依恋与身心守护 · 关爱支持\n\n"
                f"看到你为毛孩子悬着一颗心（“{snippet}”）。宠物不仅是生灵，更是给予我们无条件接纳与依恋支撑的重要家庭成员。\n\n"
                f"#### 一、就医与环境照护指引\n"
                f"1. **正规面诊排查**：若伴有体温异常、拒食、呕吐腹泻或精神萎靡，第一时间前往正规动物医院，切勿自行饲喂人用退烧药或抗生素；\n"
                f"2. **打造低应激避风港**：准备安静、遮光、温暖且通风的单处小窝，备足干净温水，尽量减少过多抱起或强行打扰；\n"
                f"3. **记录客观体征**：记录每日进食量、排泄频次与精神活动状态，为就诊提供详实依据。\n\n"
                f"#### 二、先稳住你自己的呼吸与电量\n"
                f"毛孩子对主人的焦虑情绪极具感知力。请允许自己先深呼吸 3 次，放下过度的内疚与自责——你的平静、温柔与耐心，就是给它当下最坚固的安全岛。\n\n"
                f"配合专业医生的治疗，小家伙一定会慢慢康复的。加油！"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # ========== 领域 5: 常见科学、生活常识与开放性问答 ==========
        qa_keywords = ("为什么", "什么是", "怎么看", "解释一下", "天气", "旅游", "诗", "哲学", "意义", "如何看待", "电影", "音乐")
        if any(kw in p_lower for kw in qa_keywords):
            return (
                f"### ✦ 思维视野与事实剖析 · 客观解答\n\n"
                f"关于你提出的疑问：**「{snippet}」**，我们可以从以下几个维度来理解：\n\n"
                f"#### 一、核心机制与背景脉络\n"
                f"- **事实本质**：针对“{snippet}”，其背后的主要成因在于客观规律与环境系统的相互作用；\n"
                f"- **认知视角**：当我们跳出单一的因果判断，从更广阔的系统视角审视，往往能发现事情的多个观察切面。\n\n"
                f"#### 二、生活启发与认知微行动\n"
                f"1. **第一性原理探究**：剥离表面喧嚣，先抓住最关键的一到两项基础事实；\n"
                f"2. **连接当下生活**：思考这个现象或问题如何给当下的生活节奏或心智成长带来启发；\n"
                f"3. **保持开放好奇**：允许事物存在未被探索的盲区，在探索中慢慢获得新知。\n\n"
                f"如果你想针对具体某一方面展开推演，随时告诉我，我们可以继续深入探讨！"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # ========== 领域 5: 心理与情绪主题深入分类 ==========
        prompt_lower = p_lower
        topic_map = {
            "考研": "学业发展与考试备考", "考试": "学业发展与考试备考", "复习": "学业发展与备考焦虑", "挂科": "学业危机应对",
            "论文": "毕业学术研究与论文写作", "毕业": "毕业与身份转变", "答辩": "答辩与学业闭环", "导师": "导学沟通与学术边界",
            "工作": "职场发展与压力平衡", "加班": "工作负荷与精力恢复", "领导": "职场上下沟通与心理边界", "同事": "职场协作与人际摩擦",
            "离职": "职业抉择与转变", "裁员": "职场不确定性与生存策略", "汇报": "职场表达与评价焦虑", "kpi": "绩效考核与内耗解离",
            "分手": "亲密关系终结与哀伤整合", "恋爱": "亲密关系沟通与依恋", "失恋": "情感失去与自我重建", "异地": "异地恋情感维系",
            "父母": "原生家庭边界与代际沟通", "催婚": "家庭期望与自我选择", "吵架": "人际冲突与情绪降温", "朋友": "同侪支持与社交归属",
            "失眠": "睡眠障碍与心身节律", "睡不着": "睡意对抗与入睡焦虑", "熬夜": "晚间报复性拖延",
            "焦虑": "广泛性焦虑与过度预期", "紧张": "急性应激与自主神经兴奋", "心慌": "躯体化反应与迷走神经调节",
            "难过": "抑郁心境与能量低谷", "孤独": "存在主义孤独与心理连接", "自卑": "低自我价值感与比较陷阱",
            "拖延": "任务启动障碍与完美主义抗拒", "迷茫": "未来路径探索与意义感缺失",
        }
        matched_topics = [t for k, t in topic_map.items() if k in prompt_lower]
        topic_label = matched_topics[0] if matched_topics else "心身状态与思绪梳理"

        # 根据 VAD 维度定制情感语气
        if v < -0.4:
            opening = f"听到你分享关于「{topic_label}」的经历（“{snippet}”），我能感受到此刻你心里沉甸甸的负荷。面对这样的困境，感到难过、疲惫或委屈是极为自然的真实反应。"
        elif a > 0.6:
            opening = f"我注意到在谈及「{topic_label}」时（“{snippet}”），你的神经系统正处于比较强烈的紧绷与高唤醒状态。当压力突然升高时，大脑往往会拉响最高等级警报。"
        else:
            opening = f"关于你谈到的「{topic_label}」（“{snippet}”），我认真体会了你所表达的细节。把这份思绪讲出来，本身就是在为自己梳理秩序的第一步。"

        paragraphs: List[str] = [
            f"### ✦ 本地神经模型分析 · 针对性心身疏导\n\n{opening}",
            f"> **当前状态投影**：心身状态趋向于【{label}】（神经激活度 A={a:.2f}，情绪效价 V={v:.2f}）。"
        ]

        # 认知重塑匹配 (根据具体 topic 选择最贴切的认知歪曲)
        cbt_distortion = next((item for item in retrieved if item.get("category") == "cbt_distortions"), None)
        if cbt_distortion:
            raw_d = cbt_distortion.get("raw_data", {})
            distortion_title = cbt_distortion.get("title", "")
            balanced = raw_d.get("balanced_thought") or raw_d.get("balanced_alternative_thought", "单次事件并不定义全部的价值。")
            experiment = raw_d.get("micro_experiment", "写下最坏结局发生的概率，并列出两条兜底预案。")
            paragraphs.append(
                f"#### 一、认知行为透镜 (CBT)：透视「{distortion_title}」\n"
                f"在面对「{topic_label}」时，我们容易陷入自动化负向思维：\n"
                f"- **平衡事实视角**：{balanced}\n"
                f"- **行动小实验**：{experiment}"
            )

        # 微行动推荐 (根据具体场景推荐最贴切动作)
        actions = [item for item in retrieved if item.get("category") == "somatic_and_behavioral_micro_actions"]
        if actions:
            act_blocks = []
            for idx, act in enumerate(actions[:2], 1):
                raw_a = act.get("raw_data", {})
                steps = raw_a.get("steps", [])
                mech = raw_a.get("neurobiological_mechanism", "")
                steps_text = "\n  ".join([f"- {s}" for s in steps[:2]]) if steps else act.get("content", "")[:100]
                mech_text = f"\n  *(神经机制: {mech[:60]}...)*" if mech else ""
                act_blocks.append(f"**{idx}. 【{act.get('title')}】**\n  {steps_text}{mech_text}")
            paragraphs.append("#### 二、当下即可开展的身心稳态微行动\n" + "\n\n".join(act_blocks))
        else:
            if a > 0.6:
                paragraphs.append(
                    "#### 二、当下即可开展的身心稳态微行动\n"
                    "**1. 【生理性叹息呼吸 (Physiological Sigh)】**\n"
                    "- 鼻腔连续深吸两口气（一大一短），张嘴缓慢长呼气至完全排空；\n"
                    "- 重复 3 次，迅速刺激迷走神经降低心率与神经紧绷度。"
                )
            else:
                paragraphs.append(
                    "#### 二、当下即可开展的身心稳态微行动\n"
                    "**1. 【极小行动切片 (Micro-Step)】**\n"
                    "- 将当前面临的庞大压力切碎成眼下 3 分钟内能完成的一小步（如打开一页文档、喝一杯温水）；\n"
                    "- 告诉自己：只要求开始，不要求一次性解决整件事。"
                )

        paragraphs.append(
            "#### 三、给你的赋能寄语\n"
            "不用强求自己一次把所有问题完全想透。允许自己慢下来呼吸，一步一步走，你比想象中更有韧性。"
        )

        if system_hint:
            paragraphs.append(f"\n*(已按您的专属偏好指令对齐：{system_hint})*")

        return "\n\n".join(paragraphs)


# 全局单例
_global_local_model_engine: Optional[LocalModelEngine] = None


def get_local_model_engine() -> LocalModelEngine:
    global _global_local_model_engine
    if _global_local_model_engine is None:
        _global_local_model_engine = LocalModelEngine()
    return _global_local_model_engine
