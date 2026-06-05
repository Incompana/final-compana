from __future__ import annotations

from src.rule_engine.action_plan_generator import generate_action_plan


def _assert_step_contract(step: dict) -> None:
    assert "order" in step
    assert "title" in step and step["title"]
    assert "task_suggestion" in step and step["task_suggestion"]
    assert "expected_output" in step and step["expected_output"]
    assert "success_criteria" in step and step["success_criteria"]


def test_cybersecurity_beginner_plan_contract() -> None:
    payload = generate_action_plan(
        target_role="cybersecurity",
        problem_category="beginner_lost",
        current_level="zero",
        blocker_type="no_foundation",
        gap_skills=["security_fundamentals", "networking_basics"],
    )

    assert payload["planner_version"] == "action_plan_rule_v1"
    assert payload["title"].startswith("Rencana Aksi 4 Minggu")
    assert payload["clarification_needed"] is False
    assert 3 <= len(payload["steps"]) <= 6

    for index, step in enumerate(payload["steps"], start=1):
        _assert_step_contract(step)
        assert step["order"] == index

    assert any("fondasi" in step["title"].lower() for step in payload["steps"])


def test_frontend_no_portfolio_has_portfolio_step() -> None:
    payload = generate_action_plan(
        target_role="frontend",
        problem_category="skill_gap",
        current_level="basic",
        blocker_type="no_portfolio",
        gap_skills=["react_component_basics", "api_fetch_state"],
    )

    titles = [step["title"].lower() for step in payload["steps"]]
    tasks = [step["task_suggestion"].lower() for step in payload["steps"]]

    assert any("portfolio" in title for title in titles)
    assert any("github" in task or "project" in task for task in tasks)
    assert "markdown_view" in payload and payload["markdown_view"].startswith("# ")


def test_overwhelmed_unclear_role_triggers_clarification_safe_plan() -> None:
    payload = generate_action_plan(
        target_role="unclear",
        problem_category="overwhelmed",
        current_level="unclear",
        blocker_type="too_many_options",
        gap_skills=[],
    )

    assert payload["clarification_needed"] is True
    assert payload["title"] == "Rencana Aksi 2 Minggu untuk Menentukan Arah Karier"
    assert payload["steps"][0]["title"] == "Tentukan Satu Role Fokus 4 Minggu"
    assert any("fokus" in step["title"].lower() or "opsi" in step["title"].lower() for step in payload["steps"])


def test_step_count_capped_to_six() -> None:
    payload = generate_action_plan(
        target_role="backend",
        problem_category="skill_gap",
        current_level="basic",
        blocker_type="no_roadmap",
        gap_skills=[
            "http_api_basics",
            "database_crud",
            "input_validation_auth_basics",
            "error_handling_logging",
        ],
    )

    assert len(payload["steps"]) <= 6
    assert payload["steps"][-1]["title"] == "Review Progres dan Tetapkan Langkah Lanjut"


def test_markdown_view_contains_all_step_numbers() -> None:
    payload = generate_action_plan(
        target_role="data_analyst",
        problem_category="skill_gap",
        current_level="basic",
        blocker_type="no_roadmap",
        gap_skills=["data_cleaning"],
    )

    markdown_view = payload["markdown_view"]
    assert payload["title"] in markdown_view
    for step in payload["steps"]:
        assert f"{step['order']}. **{step['title']}**" in markdown_view
