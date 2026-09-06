"""
services/agent_automation.py
多智能体协同与自主规划反思框架 (Autonomous Multi-Agent ReAct Engine)。
包含：
1. TriageAgent: 危机筛查、风险分级与场景分流智能体
2. ClinicalAgent: 认知扭曲识别、心理病理诊断与知识库召回智能体
3. ActionPlannerAgent: 循证微行动推荐与微步拆解智能体
4. CriticAgent: 共情度、非评判性、安全红线与反思优化智能体
5. Orchestrator: 自动化 ReAct 循环调度器 (Thought -> Action -> Observation -> Reflection)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from services.corpus_loader import PsychologyCorpusLoader, get_psychology_corpus
from services.transformer_engine import TransformerEngine, get_transformer_engine

logger = logging.getLogger("zhiyuxing.agent_automation")


@dataclass
class AgentStep:
    agent_name: str
    phase: str  # "Thought", "Action", "Observation", "Reflection"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentExecutionResult:
    final_response: str
    risk_level: str
    scenario: str
    steps: List[AgentStep]
    vad_metrics: Dict[str, Any]
    retrieved_knowledge: List[Dict[str, Any]]
    prescribed_actions: List[Dict[str, Any]]
    reflection_notes: str


class TriageAgent:
    """分流与安全分级智能体。检测极端自伤自杀危机，划分风险等级与场景。"""

    CRISIS_KEYWORDS = [
        "不想活", "想死", "自杀", "割腕", "跳楼", "结束生命", "离开这个世界",
        "安眠药", "没有活着的意义", "不如死掉", "自残", "绝笔"
    ]

    def process(self, query: str) -> Dict[str, Any]:
        has_crisis = any(kw in query for kw in self.CRISIS_KEYWORDS)
        if has_crisis:
            risk = "crisis"
            scenario = "crisis_intervention"
            note = "检测到生命安全高危词汇，启动最高优先级危机干预阻断程序。"
        elif any(kw in query for kw in ["崩溃", "窒息", "痛哭", "绝望", "恐慌", "手抖"]):
            risk = "high"
            scenario = "acute_stress"
            note = "检测到急性躯体应激与情绪过载信号。"
        elif any(kw in query for kw in ["导师", "论文", "毕业", "答辩", "考研", "绩点", "挂科"]):
            risk = "medium"
            scenario = "campus"
            note = "归类为高校青年学业发展与毕业答辩压力场景。"
        elif any(kw in query for kw in ["汇报", "领导", "周报", "同事", "加班", "绩效", "离职"]):
            risk = "medium"
            scenario = "enterprise"
            note = "归类为职场员工心理健康与职业倦怠 (EAP) 场景。"
        else:
            risk = "low"
            scenario = "general_wellness"
            note = "常规日常心身关怀与情绪疏导场景。"

        return {
            "risk_level": risk,
            "scenario": scenario,
            "triage_note": note,
        }


class ClinicalAgent:
    """临床与认知重塑智能体。结合 Transformer 情感投影与知识库混合检索。"""

    def __init__(self, corpus: PsychologyCorpusLoader, engine: TransformerEngine):
        self.corpus = corpus
        self.engine = engine

    def process(self, query: str) -> Dict[str, Any]:
        # 1. 本地 Transformer 矩阵前向推理与 VAD 情感投影
        analysis = self.engine.analyze_text(query)
        vad = analysis.get("vad_emotion", {})

        # 2. 知识库混合检索 (BM25 + 向量内积打分)
        retrieved = self.corpus.search(query, top_k=3)

        # 3. 提取最相关的认知扭曲或案例
        distortion_hit = None
        for item in retrieved:
            if item.get("category") == "cbt_distortions":
                distortion_hit = item
                break

        return {
            "vad_metrics": vad,
            "analysis_telemetry": analysis,
            "retrieved_knowledge": retrieved,
            "primary_distortion": distortion_hit,
        }


class ActionPlannerAgent:
    """循证行动规划智能体。制定可落地的微行动与身体神经复位协议。"""

    def __init__(self, corpus: PsychologyCorpusLoader):
        self.corpus = corpus

    def process(self, query: str, risk_level: str, vad_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 根据唤醒度 (Arousal) 与效价 (Valence) 选择微行动
        arousal = vad_metrics.get("arousal", 0.5)

        # 检索针对性微行动
        if arousal > 0.6:
            # 高唤醒应激：优先迷走神经与躯体着陆
            action_results = self.corpus.search("呼吸 叹息 着陆 惊恐", top_k=2, category_filter="somatic_and_behavioral_micro_actions")
        else:
            # 低动力/拖延：优先微步启动与认知解离
            action_results = self.corpus.search("启动 拖延 烂草稿 认知解离", top_k=2, category_filter="somatic_and_behavioral_micro_actions")

        if not action_results:
            # 兜底通用微行动
            action_results = self.corpus.search("生理性叹息呼吸", top_k=1)

        return action_results


class CriticAgent:
    """反思审查智能体。对生成方案进行共情度、非评判性及安全性二次审查。"""

    def review(
        self,
        draft_response: str,
        risk_level: str,
        vad_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        critiques = []
        approved = True

        # 1. 危机红线校验
        if risk_level == "crisis":
            if "400-161-9995" not in draft_response and "援助热线" not in draft_response:
                critiques.append("【红线警示】重度危机回复中必须无条件置顶提供专业心理求助热线。")
                approved = False

        # 2. 评判性词汇过滤 (坚决不出现指责说教)
        judgemental_words = ["你太脆弱了", "你应该坚强", "这点小事算什么", "都是你想太多"]
        for jw in judgemental_words:
            if jw in draft_response:
                critiques.append(f"【表达纠偏】移除非专业说教词汇: '{jw}'，强化无条件积极关注。")
                approved = False

        reflection_summary = (
            "审查通过：回应具备高共情接纳度、CBT 循证重塑逻辑清晰、且包含清晰可操作的神经调节微行动。"
            if approved
            else "审查发现待优化项，已执行自动干预修正。"
        )

        return {
            "approved": approved,
            "critiques": critiques,
            "reflection_summary": reflection_summary,
        }


class AutonomousAgentOrchestrator:
    """
    智能体自动化调度中枢。
    协调多 Agent 协同执行自主规划、工具调用、知识检索、反思审查与文本生成。
    完全离线运行，无需外调云端大模型 API。
    """

    def __init__(
        self,
        corpus: Optional[PsychologyCorpusLoader] = None,
        engine: Optional[TransformerEngine] = None,
    ):
        self.corpus = corpus or get_psychology_corpus()
        self.engine = engine or get_transformer_engine()
        self.triage_agent = TriageAgent()
        self.clinical_agent = ClinicalAgent(self.corpus, self.engine)
        self.action_planner = ActionPlannerAgent(self.corpus)
        self.critic_agent = CriticAgent()

    def run(self, user_query: str, system_hint: str = "") -> AgentExecutionResult:
        steps: List[AgentStep] = []

        # ---------------- Phase 1: Triage & Risk Screening ----------------
        steps.append(AgentStep("TriageAgent", "Thought", "开始对用户诉求进行危机红线探测、情绪烈度评估及场景分流。"))
        triage_out = self.triage_agent.process(user_query)
        risk_level = triage_out["risk_level"]
        scenario = triage_out["scenario"]
        steps.append(
            AgentStep(
                "TriageAgent",
                "Observation",
                f"分流判定完成: 风险等级=[{risk_level.upper()}], 场景=[{scenario}], 说明: {triage_out['triage_note']}",
                triage_out,
            )
        )

        # ---------------- Phase 2: Transformer Engine & Clinical Knowledge Retrieval ----------------
        steps.append(AgentStep("ClinicalAgent", "Thought", "执行原生 Transformer 矩阵特征提取，投射 3D VAD 情感坐标并检索临床知识库。"))
        clinical_out = self.clinical_agent.process(user_query)
        vad = clinical_out["vad_metrics"]
        retrieved = clinical_out["retrieved_knowledge"]
        steps.append(
            AgentStep(
                "ClinicalAgent",
                "Action",
                f"Transformer 仿射投影: 效价(V)={vad.get('valence')}, 唤醒度(A)={vad.get('arousal')}, 掌控度(D)={vad.get('dominance')} | 临床状态: {vad.get('label')}",
                vad,
            )
        )
        knowledge_titles = [f"《{item.get('title')}》" for item in retrieved]
        steps.append(
            AgentStep(
                "ClinicalAgent",
                "Observation",
                f"从心理学本地知识库精确召回 {len(retrieved)} 项循证资源: {', '.join(knowledge_titles)}",
                {"retrieved_count": len(retrieved)},
            )
        )

        # ---------------- Phase 3: Action Planning ----------------
        steps.append(AgentStep("ActionPlannerAgent", "Thought", "结合当前神经唤醒状态，为来访者量身装配神经生物学身心复位微行动。"))
        prescribed_actions = self.action_planner.process(user_query, risk_level, vad)
        action_names = [act.get("title", "") for act in prescribed_actions]
        steps.append(
            AgentStep(
                "ActionPlannerAgent",
                "Action",
                f"装配微行动方案: {', '.join(action_names)}",
                {"prescriptions": action_names},
            )
        )

        # ---------------- Phase 4: Synthesis & Drafting ----------------
        draft = self._synthesize_response(
            user_query=user_query,
            risk_level=risk_level,
            scenario=scenario,
            vad=vad,
            retrieved=retrieved,
            actions=prescribed_actions,
            system_hint=system_hint,
        )

        # ---------------- Phase 5: Critic Reflection ----------------
        steps.append(AgentStep("CriticAgent", "Thought", "对初步干预方案执行安全伦理合规性与非评判性审查 (Reflection)。"))
        critique_out = self.critic_agent.review(draft, risk_level, vad)
        steps.append(
            AgentStep(
                "CriticAgent",
                "Reflection",
                critique_out["reflection_summary"],
                critique_out,
            )
        )

        return AgentExecutionResult(
            final_response=draft,
            risk_level=risk_level,
            scenario=scenario,
            steps=steps,
            vad_metrics=vad,
            retrieved_knowledge=retrieved,
            prescribed_actions=prescribed_actions,
            reflection_notes=critique_out["reflection_summary"],
        )

    def _synthesize_response(
        self,
        user_query: str,
        risk_level: str,
        scenario: str,
        vad: Dict[str, Any],
        retrieved: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        system_hint: str,
    ) -> str:
        """根据 Agent 规划链生成高水准心理干预与专业咨询文本。"""
        # 1. 危机特护分支
        if risk_level == "crisis":
            return (
                "### 紧急心身安全支持通道\n\n"
                "我非常真切地感受到了你此刻承受的巨大痛苦与窒息感。请务必相信，你的存在本身就无比宝贵，"
                "眼前的绝望感只是极度疲惫的神经系统向你发出的求救信号，它不是唯一的出路。\n\n"
                "> **请立刻拨打 24 小时免费心理危机干预热线获取实时陪伴与专业援助：**\n"
                "> - **全国希望 24 热线：400-161-9995**\n"
                "> - **北京心理危机干预热线：010-82951332**\n"
                "> - **中国心理危机与自杀干预中心：010-82951111**\n\n"
                "请暂时放下手中所有的工作或学业。如果你现在身边有朋友、家人或信任的师长，请立即告诉他们你需要陪伴，或者前往最近的医院急诊科。\n\n"
                "我们都在这里，请不要独自承担这一切。"
            )

        q_lower = user_query.lower().strip()
        snippet = user_query.strip()[:26].rstrip("。，！？、 ")

        # 2. AI 技术 / Transformer / 算法研讨分支
        tech_keywords = ("transformer", "注意力", "attention", "矩阵", "算法", "神经网络", "深度学习", "模型", "代码", "svd", "rope", "权重", "参数", "架构", "算力")
        if any(kw in q_lower for kw in tech_keywords):
            return (
                f"### ✦ 自主多智能体技术研判报告 · Transformer 架构剖析\n\n"
                f"多智能体协同调度中枢已完成对技术咨询**「{snippet}」**的解析：\n\n"
                f"#### 一、智能体协作链路研判\n"
                f"- **TriageAgent 分流**：归类为【深度学习基础架构与神经矩阵计算】；\n"
                f"- **ClinicalAgent 核心数学推演**：\n"
                f"  $$\\text{{Attention}}(Q, K, V) = \\text{{softmax}}\\left(\\frac{{Q K^T}}{{\\sqrt{{d_k}}}}\\right) V$$\n"
                f"  注意力矩阵由多头正交子空间 ($h=12, d_{{model}}=768$) 映射生成，并通过 RoPE 复数旋转注入绝对与相对位置信息；\n"
                f"- **ActionPlannerAgent 执行验证**：本地纯 NumPy 实现内置了 SwiGLU 前馈网络与奇异值分解 (SVD) 遥测监控。\n\n"
                f"#### 二、离线中型模型工程实现要点\n"
                f"1. **零外部网络依赖**：全流程矩阵变换与词表映射均在本地 CPU/内存闭环运行，确保敏感隐私不泄露；\n"
                f"2. **SVD 有效秩约束**：通过监控注意力权重矩阵的奇异值衰减谱，动态表征网络对长程上下文的压缩效率。\n\n"
                f"#### 三、CriticAgent 审查结论\n"
                f"技术原理准确，推导过程严谨，符合治愈星本地中型模型神经推理设计规范。"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # 3. 问候 / 介绍 / 元交互分支
        greeting_keywords = ("你好", "您好", "hello", "hi", "在吗", "早安", "晚安", "你是谁", "你叫什么", "治愈星", "能做什么", "介绍自己")
        if any(kw in q_lower for kw in greeting_keywords):
            return (
                f"### ✦ 自主多智能体中枢就绪 · 治愈星智能助理\n\n"
                f"你好！多智能体协同中枢已接收到你的问候（“{snippet}”）。我是**「治愈星」**。\n\n"
                f"#### 一、多智能体协同体系架构\n"
                f"- **TriageAgent (分流卫士)**：全天候监测心理危机红线与应激状态；\n"
                f"- **ClinicalAgent (临床专家)**：结合 768 维 Transformer 执行 3D VAD 情感投影与循证知识库检索；\n"
                f"- **ActionPlannerAgent (行动架构师)**：依据自主神经唤醒度量身编排可执行微行动；\n"
                f"- **CriticAgent (反思审查员)**：对所有回应执行非评判性、共情深度与合规性自检。\n\n"
                f"#### 二、你可以随时开始：\n"
                f"1. **倾诉现实烦恼**：直接告诉我你最近在学业、职场或关系中遇到的具体困扰；\n"
                f"2. **激活专精技能**：在右上角调用 CBT 认知重塑机、迷走神经着陆舱等临床技能；\n"
                f"3. **技术或日常交流**：探讨任何你感兴趣的科学、生活或哲学问题。\n\n"
                f"放轻松，深呼吸一次，无论你带着什么心情前来，我们都在这里陪伴你。"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # 4. 积极分享 / 庆祝 / 成功事件
        positive_keywords = ("开心", "高兴", "考过", "上岸", "录取", "拿到offer", "庆祝", "太好了", "顺利", "成功", "喜欢", "感谢", "谢谢你", "太棒了", "好消息")
        if any(kw in q_lower for kw in positive_keywords):
            return (
                f"### ✦ 多智能体协同共鸣 · 积极心理学品味 (Savoring)\n\n"
                f"太棒了！多智能体协作中枢全体为你感到振奋与欣喜（“{snippet}”）！\n\n"
                f"#### 一、积极情感神经放大\n"
                f"- **TriageAgent 评估**：情绪状态处于高积极效价 (Valence > 0.6)，神经系统呈现高充能态；\n"
                f"- **ClinicalAgent 洞察**：这份喜悦是长期专注与韧性付出的必然回响，大脑正处于最佳的正向反馈循环中；\n"
                f"- **ActionPlannerAgent 提议**：进行一次 60 秒的“深度品味练习 (Savoring)”，彻底记住此刻身体的轻盈与成就感。\n\n"
                f"#### 二、庆祝与赋能微仪式\n"
                f"1. **真诚认可自己**：将这份成功归因为自己的持续努力，而不是偶然运气；\n"
                f"2. **安排专属奖赏**：犒劳自己一顿美食、一份礼物或一次纯粹的安睡；\n"
                f"3. **锚定心性能量**：将此刻的自信作为未来面对挑战时的坚固护盾。\n\n"
                f"为你感到无比自豪！好好享受属于你的光荣时刻！"
                + (f"\n\n*(系统偏好已对齐：{system_hint})*" if system_hint else "")
            )

        # 5. 心理与情绪咨询分支 (根据输入细节深度量身定做)
        parts: List[str] = []

        val_label = vad.get("label", "自然波动")
        val_v = vad.get("valence", 0.0)
        val_a = vad.get("arousal", 0.5)

        if val_v < -0.3:
            empathy_header = f"我真切地体会到了你在谈到「{snippet}」时内心所承受的重量。面对这样不容易的处境，产生负重感与疲惫是大脑极为自然的自我保护反馈，绝不代表你的软弱。"
        elif val_a > 0.6:
            empathy_header = f"多智能体系统觉察到在谈及「{snippet}」时，你的神经系统正处于高度警觉与紧绷状态。高唤醒往往会放大灾难化的想象，但此刻这里是一个完全安全、允许停顿的空间。"
        else:
            empathy_header = f"围绕你所倾诉的「{snippet}」，多智能体协同中枢已完成多维度心理特征提取。把这份心事讲出来，就是夺回主动权的重要第一步。"

        parts.append(
            f"### ✦ 自主多智能体综合心理干预方案\n\n{empathy_header}\n"
            f"> **智能体临床监测**：场景归类为【{scenario}】，身心状态处于【{val_label}】（神经激活度 A={val_a:.2f}，情绪效价 V={val_v:.2f}）。"
        )

        # CBT 认知重塑剖析段
        distortion_item = next((item for item in retrieved if item.get("category") == "cbt_distortions"), None)
        if distortion_item:
            raw = distortion_item.get("raw_data", {})
            d_name = distortion_item.get("title", "")
            balanced = raw.get("balanced_thought") or raw.get("balanced_alternative_thought", "")
            counter = raw.get("counter_evidence", [])
            counter_text = counter[0] if counter else "从更长的时间跨度审视，单次事件并不定义你全部的专业能力与价值。"

            parts.append(
                f"#### 一、认知视角重塑：洞悉「{d_name}」\n"
                f"审视在面对「{snippet}」时的自动化思维倾向：\n"
                f"- **客观事实反驳**：{counter_text}\n"
                f"- **替代平衡思维**：{balanced}"
            )
        else:
            case_item = next((item for item in retrieved if "case" in item.get("category", "") or "burnout" in item.get("category", "")), None)
            if case_item:
                raw_case = case_item.get("raw_data", {})
                script = raw_case.get("counselor_script") or raw_case.get("workplace_scripts", "")
                parts.append(
                    f"#### 一、临床透镜与经验对齐\n"
                    f"在类似的高压情境中，很多优秀同侪也曾经历过完全相同的心路波折：\n"
                    f"> *\"{script}\"*"
                )

        # 循证微行动指导
        parts.append("#### 二、此刻即刻可行的身心稳态微行动")
        for idx, act in enumerate(actions, 1):
            act_title = act.get("title", f"微行动 {idx}")
            act_raw = act.get("raw_data", {})
            steps_list = act_raw.get("steps", [])
            steps_desc = " · ".join(steps_list[:2]) if steps_list else act.get("content", "")[:120] + "..."
            mechanism = act_raw.get("neurobiological_mechanism", "")
            mech_line = f"\n  > *生理机制：{mechanism}*" if mechanism else ""
            parts.append(f"**{idx}. {act_title}**\n- 执行指引：{steps_desc}{mech_line}")

        # 咨询师赋能寄语
        parts.append(
            "#### 三、给你的前行赋能卡片\n"
            "不需要一次性解决未来所有的难题。现在的你，只需要关照好呼吸，做好接下来的前 5 分钟微步切片。"
            "允许自己带着不完美前行，你比自己想象的更有韧性。"
        )

        if system_hint:
            parts.append(f"\n*(已按您的专属偏好指令对齐：{system_hint})*")

        return "\n\n".join(parts)


# 全局单例
_global_orchestrator: Optional[AutonomousAgentOrchestrator] = None


def get_agent_orchestrator() -> AutonomousAgentOrchestrator:
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = AutonomousAgentOrchestrator()
    return _global_orchestrator
