from app import STYLE_LABELS, build_demo_reply, build_messages, detect_demo_topic, normalize_response_style


def test_build_messages_appends_system_hint_and_style() -> None:
    messages = build_messages("最近总拖延。", "给出 3 条具体建议", "structured")

    assert messages[0]["role"] == "system"
    assert "给出 3 条具体建议" in messages[0]["content"]
    assert STYLE_LABELS["structured"]
    assert messages[1]["content"] == "最近总拖延。"


def test_build_demo_reply_returns_structured_advice() -> None:
    reply = build_demo_reply("最近总拖延，学不进去。")

    assert "1." in reply
    assert "2." in reply
    assert "3." in reply


def test_build_demo_reply_respects_response_style() -> None:
    reply = build_demo_reply("最近总拖延，学不进去。", response_style="brief")

    assert "先做这 3 件事" in reply


def test_detect_demo_topic_distinguishes_common_scenarios() -> None:
    assert detect_demo_topic("我马上要面试了，特别紧张。") == "interview_anxiety"
    assert detect_demo_topic("期末考试快到了，我复习不进去。") == "exam_anxiety"
    assert detect_demo_topic("最近总失眠，白天也很累。") == "sleep_exhaustion"


def test_build_demo_reply_changes_with_question_topic() -> None:
    interview_reply = build_demo_reply("我最近实习面试很紧张，总怕答不上来。")
    future_reply = build_demo_reply("我对未来很迷茫，不知道以后该做什么。")

    assert "面试" in interview_reply
    assert "方向" in future_reply or "未来" in future_reply or "探索" in future_reply


def test_normalize_response_style_supports_hint_fallback() -> None:
    style = normalize_response_style(None, "更鼓励一点")

    assert style == "encouraging"


def test_demo_reply_factual_and_continuation_matching() -> None:
    # 1. Jiaxing university inquiry
    uni_reply = build_demo_reply("嘉兴大学你知道吗")
    assert "嘉兴大学" in uni_reply
    assert "痛点" not in uni_reply
    assert "困惑或想寻找更好的解法是极其自然的反应" not in uni_reply

    # 2. Emotion definition inquiry
    emo_reply = build_demo_reply("你知道情绪是什么吗")
    assert "情绪" in emo_reply
    assert "主观体验" in emo_reply or "生理唤醒" in emo_reply
    assert "痛点" not in emo_reply

    # 3. Continuation with previous emotion context
    history_emo = [{"role": "user", "content": "你知道情绪是什么吗"}, {"role": "assistant", "content": "情绪是..."}]
    cont_emo = build_demo_reply("继续", conversation_history=history_emo)
    assert "情绪" in cont_emo
    assert "调节" in cont_emo or "杏仁核" in cont_emo or "前额叶" in cont_emo

    # 4. Continuation with previous university context
    history_uni = [{"role": "user", "content": "嘉兴大学你知道吗"}, {"role": "assistant", "content": "嘉兴大学是..."}]
    cont_uni = build_demo_reply("继续", conversation_history=history_uni)
    assert "大学" in cont_uni or "长三角" in cont_uni
    assert "痛点" not in cont_uni

