from __future__ import annotations

from ai_ml_module.engines.evaluation_engine import evaluate_task
from ai_ml_module.engines.skill_gap_engine import generate_skill_gap
from ai_ml_module.utils.loader import load_rubric_feedback_bank, load_task_bank


def test_enriched_task_bank_has_minimum_role_coverage() -> None:
    df = load_task_bank()
    counts = df.groupby("target_role")["task_id"].count().to_dict()

    for role in {
        "frontend_developer",
        "backend_developer",
        "ui_ux_designer",
        "soc_analyst",
        "machine_learning_engineer",
        "data_analyst",
    }:
        assert counts.get(role, 0) >= 8


def test_task_bank_has_no_generic_titles_or_descriptions() -> None:
    df = load_task_bank()
    titles = " ".join(df["task_title"].astype(str).tolist()).lower()
    descriptions = " ".join(df["task_description"].astype(str).tolist()).lower()

    assert "task 6 untuk" not in titles
    assert "task 4 untuk" not in titles
    assert "deskripsi tugas mendalam di sini" not in descriptions
    assert df["task_steps"].astype(str).str.split("|").map(len).min() >= 5
    assert df["assessment_checklist"].astype(str).str.split("|").map(len).min() >= 4


def test_every_task_has_rubric_weight_100() -> None:
    tasks = load_task_bank()
    rubrics = load_rubric_feedback_bank()
    grouped = rubrics.groupby("task_id")["weight"].sum().to_dict()

    for task_id in tasks["task_id"].astype(str):
        assert task_id in grouped
        assert float(grouped[task_id]) == 100.0


def test_skill_gap_returns_reason_evidence_and_next_task() -> None:
    payload = generate_skill_gap(
        "soc_analyst",
        {"networking_fundamental": 1, "linux_basic": 0, "log_analysis": 0},
    )

    assert payload["priority_gap"] in {"log_analysis", "linux_basic"}
    first_missing = payload["missing_skills"][0]
    assert first_missing["status"] == "missing"
    assert first_missing["score"] == 0
    assert first_missing["reason"]
    assert first_missing["evidence"]
    assert first_missing["next_task_id"]


def test_evaluate_task_returns_skill_updates() -> None:
    payload = evaluate_task(
        "T_CYBE_3",
        (
            "Saya membuat sample auth log 12 baris, mengidentifikasi timestamp user source IP status, "
            "menghitung failed login per IP, menandai IP mencurigakan, lalu menulis findings dan rekomendasi."
        ),
        ["log_notes.txt", "screenshot.png"],
    )

    assert payload["status"] in {"passed", "needs_revision", "redo_task"}
    assert payload["validated_skill"] == "log_analysis"
    assert payload["skill_updates"]
    assert payload["skill_updates"][0]["skill_id"] == "log_analysis"
