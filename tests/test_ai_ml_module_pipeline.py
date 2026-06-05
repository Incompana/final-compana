from fastapi.testclient import TestClient

from ai_ml_module.app import app
from ai_ml_module.engines.assessment_selector import generate_assessment
from ai_ml_module.engines.engine1_pretext import analyze_pretext
from ai_ml_module.engines.engine3_assessment import score_answer


def test_assessment_selector_includes_expected_keywords():
    result = generate_assessment(
        {
            "domain_interest": "frontend",
            "target_role": "frontend_developer",
            "current_level": "beginner",
            "blocker_type": "none",
        }
    )

    assert result["questions"]
    assert all("expected_keywords" in question for question in result["questions"])


def test_health_and_readiness_endpoints():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    readiness = client.get("/readiness")
    assert readiness.status_code == 200
    body = readiness.json()
    assert body["status"] == "ready"
    assert body["checks"]["task_rows"] > 0
    assert body["checks"]["rubric_rows"] > 0
    assert body["checks"]["problem_category_model_available"] is True


def test_full_pipeline_demo_api_recommends_and_updates_progress():
    client = TestClient(app)

    response = client.post(
        "/full-pipeline-demo",
        json={
            "user_id": "demo",
            "user_input_text": "I want to become a frontend developer. I know HTML and CSS but not JavaScript.",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["pretext_analysis"]["target_role"] == "frontend_developer"
    assert body["action_plan"]["recommended_tasks"]
    assert body["evaluation"]["status"] == "passed"
    assert body["progress"]["dashboard"]["completed_tasks"] == 1
    assert body["progress"]["dashboard"]["readiness_score"] > 0


def test_generate_skill_gap_api_contract():
    client = TestClient(app)

    response = client.post(
        "/generate-skill-gap",
        json={
            "target_role": "frontend_developer",
            "user_skill_profile": {"html_basic": 2, "css_basic": 1},
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["target_role"] == "frontend_developer"
    assert body["priority_gap"] == "javascript_basic"
    assert body["readiness_score"] > 0


def test_single_choice_answer_uses_answer_skill_mapping():
    result = score_answer(
        {
            "question_id": "Q_WEB__0004",
            "skill_id": "javascript_basic",
            "answer_type": "single_choice",
            "expected_keywords": "belum_paham|paham_dasar|cukup_paham",
        },
        "cukup_paham",
    )

    assert result["scoring_method"] == "answer_skill_mapping"
    assert result["skill_id"] == "javascript_basic"
    assert result["skill_score"] == 2
    assert result["score"] == 100.0
    assert result["status"] == "passed"


def test_submit_assessment_endpoint_builds_real_profile():
    client = TestClient(app)

    response = client.post(
        "/submit-assessment",
        json={
            "user_id": "demo",
            "pretext_analysis": {
                "domain_interest": "frontend",
                "target_role": "frontend_developer",
                "current_level": "beginner",
                "blocker_type": "none",
                "problem_category": "frontend_task",
                "persona_type": "learner",
                "confidence_score": 0.7,
            },
            "questions": [
                {
                    "question_id": "Q_WEB__0004",
                    "skill_id": "javascript_basic",
                    "answer_type": "single_choice",
                    "expected_keywords": "belum_paham|paham_dasar|cukup_paham",
                }
            ],
            "answers": [
                {"question_id": "Q_WEB__0004", "answer_value": "cukup_paham"}
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["scored_answers"][0]["scoring_method"] == "answer_skill_mapping"
    assert body["skill_profile"]["user_skill_profile"]["javascript_basic"] == 2
    assert body["skill_gap"]["target_role"] == "frontend_developer"


def test_pretext_analyzer_supports_capstone_domains():
    cases = [
        (
            "Saya mau belajar AI ML dari nol untuk jadi machine learning engineer.",
            "ai_ml",
            "machine_learning_engineer",
        ),
        (
            "Saya ingin jadi SOC analyst dan belajar cybersecurity linux networking.",
            "cyber_security",
            "soc_analyst",
        ),
        (
            "Saya mau belajar UI UX pakai Figma dan wireframing.",
            "ui_ux",
            "ui_ux_designer",
        ),
        (
            "Saya ingin jadi data analyst belajar SQL pandas dan spreadsheet.",
            "data",
            "data_analyst",
        ),
    ]

    for text, domain, role in cases:
        result = analyze_pretext(text)
        assert result["domain_interest"] == domain
        assert result["target_role"] == role


def test_pretext_analyzer_accepts_capstone_problem_categories_from_model():
    result = analyze_pretext(
        "Saya bingung memilih jalur belajar yang tepat dan terlalu banyak pilihan karier teknologi."
    )

    assert result["problem_category"] in {
        "beginner_lost",
        "confidence_issue",
        "direction_confused",
        "overwhelmed",
    }
