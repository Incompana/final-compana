from __future__ import annotations

from src.rule_engine.gap_skill_mapper import map_gap_skills


def _assert_base_shape(payload: dict) -> None:
    assert payload["mapper_version"] == "gap_skill_mapper_rule_v1"
    assert "missing_skills" in payload
    assert "weak_skills" in payload
    assert "prioritized_next_skills" in payload
    assert isinstance(payload["missing_skills"], list)
    assert isinstance(payload["weak_skills"], list)
    assert isinstance(payload["prioritized_next_skills"], list)



def test_frontend_basic_with_partial_evidence() -> None:
    payload = map_gap_skills(
        target_role="frontend",
        current_level="basic",
        assessment_answers={
            "foundation_check": [
                "Saya bisa HTML CSS responsif",
                "Saya paham JavaScript dasar",
            ],
            "notes": "Belum pernah testing UI secara terstruktur",
        },
        detected_skills=["html", "css", "javascript", "react"],
    )
    _assert_base_shape(payload)

    missing_ids = {row["skill_id"] for row in payload["missing_skills"]}
    weak_ids = {row["skill_id"] for row in payload["weak_skills"]}

    assert "api_fetch_state" in missing_ids
    assert "react_component_basics" in weak_ids



def test_cybersecurity_beginner_has_high_priority_missing() -> None:
    payload = map_gap_skills(
        target_role="cybersecurity",
        current_level="zero",
        assessment_answers={"q1": "Saya masih pemula dan belum paham network"},
        detected_skills=[],
    )
    _assert_base_shape(payload)

    missing_ids = [row["skill_id"] for row in payload["missing_skills"]]
    assert "security_fundamentals" in missing_ids
    assert "networking_basics" in missing_ids

    # Priority ordering should put high-priority skills first.
    assert payload["missing_skills"][0]["priority"] in {"high", "medium", "low"}



def test_data_analyst_detects_weak_visualization_skill() -> None:
    payload = map_gap_skills(
        target_role="data_analyst",
        current_level="basic",
        assessment_answers={
            "q_sql": "Saya sudah bisa SQL SELECT dan JOIN dasar",
            "q_visual": "Saya pernah bikin chart dashboard sederhana",
            "q_metric": "Saya masih bingung definisi metrik",
        },
        detected_skills=["sql", "excel"],
    )
    _assert_base_shape(payload)

    weak_ids = {row["skill_id"] for row in payload["weak_skills"]}
    missing_ids = {row["skill_id"] for row in payload["missing_skills"]}

    assert "visualization_storytelling" in weak_ids
    assert "metric_definition" in missing_ids



def test_backend_intermediate_with_strong_evidence_has_limited_gaps() -> None:
    payload = map_gap_skills(
        target_role="backend",
        current_level="intermediate",
        assessment_answers={
            "q_http": "Saya sudah paham HTTP request response dan REST API",
            "q_crud": "Saya pernah buat endpoint CRUD dan query database",
            "q_validation": "Saya sudah pakai validation dan auth JWT",
            "q_logs": "Saya mampu logging error handling dasar",
        },
        detected_skills=["backend", "api", "database", "sql"],
    )
    _assert_base_shape(payload)

    assert len(payload["missing_skills"]) <= 2
    assert payload["confidence"] >= 0.6



def test_unclear_role_returns_safe_response() -> None:
    payload = map_gap_skills(
        target_role="unclear",
        current_level="unclear",
        assessment_answers={"q": "Aku masih bingung role mana"},
        detected_skills=["react", "sql"],
    )
    _assert_base_shape(payload)

    assert payload["clarification_needed"] is True
    assert payload["fallback_triggered"] is True
    assert payload["safe_next_action"] == "ask_user_to_confirm_single_target_role"
    assert payload["missing_skills"] == []
    assert payload["prioritized_next_skills"] == []



def test_gap_mapping_is_deterministic_for_same_input() -> None:
    first = map_gap_skills(
        target_role="uiux",
        current_level="basic",
        assessment_answers={"q": "Saya pernah bikin wireframe dan prototype clickable"},
        detected_skills=["figma", "wireframe"],
    )
    second = map_gap_skills(
        target_role="uiux",
        current_level="basic",
        assessment_answers={"q": "Saya pernah bikin wireframe dan prototype clickable"},
        detected_skills=["figma", "wireframe"],
    )

    assert first == second
