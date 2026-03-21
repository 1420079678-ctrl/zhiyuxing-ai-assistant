from services.safety import assess_risk, high_risk_reply, safety_prompt_extension


def test_assess_risk_detects_high_risk() -> None:
    assessment = assess_risk("我真的不想活了，想结束生命。")

    assert assessment.level == "high"
    assert assessment.needs_human_support is True
    assert assessment.matched_keywords


def test_assess_risk_detects_medium_risk() -> None:
    assessment = assess_risk("最近一直失眠，感觉快崩溃了。")

    assert assessment.level == "medium"
    assert assessment.needs_human_support is True


def test_assess_risk_detects_low_risk() -> None:
    assessment = assess_risk("这周作业有点多，我有些焦虑。")

    assert assessment.level == "low"
    assert assessment.needs_human_support is False


def test_high_risk_reply_contains_immediate_actions() -> None:
    reply = high_risk_reply()

    assert "请先做这 3 件事" in reply
    assert "110 / 120" in reply


def test_safety_prompt_extension_for_medium_risk_is_non_empty() -> None:
    assessment = assess_risk("最近失眠，感觉撑不住了。")

    assert "线下支持" in safety_prompt_extension(assessment)


def test_safety_prompt_extension_for_low_risk_is_empty() -> None:
    assessment = assess_risk("我最近面试有点紧张。")

    assert safety_prompt_extension(assessment) == ""
