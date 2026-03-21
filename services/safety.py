from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    level: str
    label: str
    note: str
    needs_human_support: bool
    matched_keywords: tuple[str, ...]


HIGH_RISK_KEYWORDS = (
    "自杀",
    "自残",
    "伤害自己",
    "结束生命",
    "不想活",
    "活不下去",
    "kill myself",
    "suicide",
    "self-harm",
    "end my life",
)

MEDIUM_RISK_KEYWORDS = (
    "崩溃",
    "绝望",
    "一直哭",
    "连续失眠",
    "失眠",
    "睡不着",
    "吃不下",
    "撑不住",
    "panic",
    "hopeless",
    "can't sleep",
    "cannot sleep",
)


def assess_risk(user_message: str) -> RiskAssessment:
    text = user_message.strip().lower()
    matched_high = tuple(keyword for keyword in HIGH_RISK_KEYWORDS if keyword in text)
    if matched_high:
        return RiskAssessment(
            level="high",
            label="高风险表达",
            note="检测到自伤或结束生命相关表达，当前更适合立即转向现实中的支持系统，而不是继续普通对话。",
            needs_human_support=True,
            matched_keywords=matched_high,
        )

    matched_medium = tuple(keyword for keyword in MEDIUM_RISK_KEYWORDS if keyword in text)
    if matched_medium:
        return RiskAssessment(
            level="medium",
            label="需要额外关注",
            note="检测到持续失眠、崩溃或明显耗竭相关表达，建议在温和建议之外，尽快联系线下支持资源。",
            needs_human_support=True,
            matched_keywords=matched_medium,
        )

    return RiskAssessment(
        level="low",
        label="常规支持场景",
        note="当前未检测到高风险表达，可继续进行常规支持与行动建议。",
        needs_human_support=False,
        matched_keywords=(),
    )


def high_risk_reply() -> str:
    return (
        "你现在提到的内容已经不是普通压力或焦虑的范围了，先不要一个人扛着。\n\n"
        "请先做这 3 件事：\n"
        "1. 立刻联系一个你信任的现实中的人，直接告诉对方你现在需要陪伴和帮助。\n"
        "2. 远离可能伤害自己的物品，不要继续独处。\n"
        "3. 如果你已经觉得自己可能会立即伤害自己，请马上联系当地紧急电话 110 / 120，或直接前往最近的医院急诊。\n\n"
        "如果你愿意，也可以只先做一件事：把“我现在需要你陪我一下”发给一个现实中的人。"
    )


def safety_prompt_extension(assessment: RiskAssessment) -> str:
    if assessment.level == "medium":
        return (
            "用户出现了连续失眠、崩溃或明显耗竭相关表达。"
            "请优先承接情绪、降低刺激感，并明确提醒可以联系学校心理中心、辅导员、家人或可信任的成年人获得线下支持。"
        )
    return ""
