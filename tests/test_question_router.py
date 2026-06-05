from __future__ import annotations

from src.rule_engine.question_router import route_assessment_questions


def _assert_base_contract(payload: dict) -> None:
    assert payload["router_version"] == "question_router_rule_v1"
    assert 3 <= payload["question_count"] <= 5
    assert payload["question_count"] == len(payload["questions"])

    required_goals = {"role_clarity", "foundation_check", "blocker_identification"}
    goals = {question["goal"] for question in payload["questions"]}
    assert required_goals.issubset(goals)

    for question in payload["questions"]:
        assert question["id"]
        assert question["prompt"]
        assert question["answer_type"] in {"single_choice", "multi_choice", "text"}
        assert isinstance(question["options"], list)
        assert question["required"] is True
        assert question["why_asked"]


def test_cybersecurity_beginner_example() -> None:
    result = route_assessment_questions(
        pretext_analysis={"confidence": 0.71, "clarification_needed": False},
        problem_category="beginner_lost",
        target_role="cybersecurity",
        current_level="zero",
        blocker_type="no_foundation",
    )
    _assert_base_contract(result)

    # Role-specific foundation check should reference cybersecurity basics.
    foundation_q = next(question for question in result["questions"] if question["goal"] == "foundation_check")
    options_text = " ".join(foundation_q["options"]).lower()
    assert "cia" in options_text or "linux" in options_text



def test_confused_multi_interest_user_example() -> None:
    result = route_assessment_questions(
        pretext_analysis={
            "confidence": 0.38,
            "clarification_needed": True,
            "matched_signals": {
                "roles": {
                    "frontend": [r"\\bfrontend\\b"],
                    "data_analyst": [r"\\bdata\\s?analyst\\b"],
                }
            },
        },
        problem_category="direction_confused",
        target_role="unclear",
        current_level="unclear",
        blocker_type="too_many_options",
    )
    _assert_base_contract(result)
    assert result["clarification_needed"] is True
    assert any(question["id"] == "role_pick_primary" for question in result["questions"])
    assert any(question["id"] == "role_decision_anchor" for question in result["questions"])



def test_frontend_user_with_basic_skills_example() -> None:
    result = route_assessment_questions(
        pretext_analysis={"confidence": 0.84, "clarification_needed": False},
        problem_category="skill_gap",
        target_role="frontend",
        current_level="basic",
        blocker_type="no_portfolio",
    )
    _assert_base_contract(result)

    assert result["clarification_needed"] is False
    assert any(question["id"] == "portfolio_evidence_state" for question in result["questions"])

    role_q = next(question for question in result["questions"] if question["id"] == "role_commitment_4_weeks")
    assert "frontend" in role_q["prompt"].lower()
