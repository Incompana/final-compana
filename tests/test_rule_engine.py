from __future__ import annotations

from src.rule_engine.pretext import analyze_pretext
from src.rule_engine.skill_mapper import map_gap_skills
from src.rule_engine.task_feedback import evaluate_task_submission
from src.schemas import ProblemCategory


def test_gap_mapping_is_deterministic() -> None:
    first = map_gap_skills("backend_developer", ["api design"])
    second = map_gap_skills("backend_developer", ["api design"])
    assert first.model_dump() == second.model_dump()


def test_short_pretext_triggers_fallback() -> None:
    classification, *_ = analyze_pretext("help")
    assert classification.problem_category == ProblemCategory.UNCLEAR
    assert classification.fallback_triggered is True


def test_task_feedback_short_submission_fallback() -> None:
    result = evaluate_task_submission(
        target_role="data_analyst",
        task_type="portfolio_project",
        submission_text="Did task",
    )
    assert result.fallback_triggered is True
    assert result.confidence <= 0.4
