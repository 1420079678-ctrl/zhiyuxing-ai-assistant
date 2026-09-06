from __future__ import annotations

from fastapi.testclient import TestClient

from app import app
from services.skills_codex import (
    build_skill_demo_reply,
    format_skill_prompt,
    get_skill,
    list_skills,
)


def test_list_skills_contains_all_protocols():
    skills = list_skills()
    assert len(skills) >= 6
    skill_ids = [s.id for s in skills]
    assert "cbt_restructure" in skill_ids
    assert "swiss_cheese_action" in skill_ids
    assert "vagal_somatic_grounding" in skill_ids
    assert "burnout_boundary_shield" in skill_ids
    assert "imposter_exposure_sandbox" in skill_ids
    assert "stoic_dichotomy_filter" in skill_ids


def test_get_skill_lookup():
    skill = get_skill("cbt_restructure")
    assert skill is not None
    assert "CBT" in skill.name
    assert len(skill.protocol_steps) == 4

    assert get_skill("non_existent_skill") is None


def test_format_skill_prompt():
    prompt = format_skill_prompt("swiss_cheese_action")
    assert "瑞士奶酪破冰术" in prompt
    assert format_skill_prompt(None) == ""
    assert format_skill_prompt("invalid_id") == ""


def test_build_skill_demo_reply():
    skill = get_skill("cbt_restructure")
    assert skill is not None
    reply = build_skill_demo_reply(skill, "我担心明天的项目答辩失败")
    assert "CBT 认知重塑" in reply
    assert "核心自动思维透视" in reply
    assert "微行动实验" in reply


def test_api_skills_endpoint():
    client = TestClient(app)
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 6
    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "clinical_base" in first
    assert "protocol_steps" in first


def test_chat_endpoint_with_skill_id():
    client = TestClient(app)
    payload = {
        "message": "我总觉得领导对我期望过高，我其实是个水货，随时会露馅",
        "skill_id": "imposter_exposure_sandbox",
        "model_target": "demo",
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["skill_id"] == "imposter_exposure_sandbox"
    assert "冒名顶替脱敏沙盒" in res_data["skill_name"]
    assert "冒名顶替" in res_data["reply"]
