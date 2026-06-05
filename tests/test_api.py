from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_analyze_pretext_contract() -> None:
    response = client.post(
        "/analyze-pretext",
        json={
            "pretext_text": "Aku mau jadi frontend, tapi masih bingung mulai dari mana dan sering stuck waktu bikin project.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["target_role"] in {
        "cybersecurity",
        "frontend",
        "backend",
        "data_analyst",
        "uiux",
        "unclear",
    }
    assert payload["problem_category"] in {
        "beginner_lost",
        "direction_confused",
        "skill_gap",
        "overwhelmed",
        "confidence_issue",
        "unclear",
    }
    assert isinstance(payload["clarification_needed"], bool)



def test_generate_assessment_contract() -> None:
    response = client.post(
        "/generate-assessment",
        json={
            "pretext_analysis": {
                "confidence": 0.76,
                "clarification_needed": False,
                "matched_signals": {"roles": {"cybersecurity": ["\\bkeamanan\\s?siber\\b"]}},
            },
            "problem_category": "beginner_lost",
            "target_role": "cybersecurity",
            "current_level": "zero",
            "blocker_type": "no_foundation",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["router_version"] == "question_router_rule_v1"
    assert 3 <= payload["question_count"] <= 5
    assert len(payload["questions"]) == payload["question_count"]



def test_map_gap_skills_contract() -> None:
    response = client.post(
        "/map-gap-skills",
        json={
            "target_role": "frontend",
            "current_level": "basic",
            "assessment_answers": {
                "foundation_check": [
                    "Saya bisa HTML CSS responsif",
                    "Saya paham JavaScript dasar",
                    "Belum pernah testing UI",
                ]
            },
            "detected_skills": ["html", "css", "javascript"],
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["mapper_version"] == "gap_skill_mapper_rule_v1"
    assert "missing_skills" in payload
    assert "weak_skills" in payload
    assert "prioritized_next_skills" in payload



def test_generate_action_plan_contract() -> None:
    response = client.post(
        "/generate-action-plan",
        json={
            "target_role": "frontend",
            "problem_category": "skill_gap",
            "current_level": "basic",
            "blocker_type": "no_portfolio",
            "gap_skills": ["react_component_basics", "api_fetch_state"],
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["planner_version"] == "action_plan_rule_v1"
    assert payload["title"]
    assert 3 <= len(payload["steps"]) <= 6
    assert payload["steps"][0]["order"] == 1
    assert payload["markdown_view"].startswith("# ")



def test_evaluate_task_contract() -> None:
    response = client.post(
        "/evaluate-task",
        json={
            "task_id": "cybersecurity_basic_nmap_explanation",
            "submission_text": (
                "Nmap dipakai untuk scanning host/port. "
                "Contoh: nmap -sV 192.168.1.10 untuk cek service. "
                "Saya hanya scan target lab sendiri dengan izin."
            ),
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] in {"passed", "need_revision", "pending"}
    assert "strengths" in payload and isinstance(payload["strengths"], list)
    assert "weaknesses" in payload and isinstance(payload["weaknesses"], list)
    assert "suggestions" in payload and isinstance(payload["suggestions"], list)



def test_openapi_contains_example_payload() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200

    spec = response.json()
    request_schema_ref = (
        spec["paths"]["/analyze-pretext"]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    )
    schema_name = request_schema_ref.split("/")[-1]
    assert "example" in spec["components"]["schemas"][schema_name]
