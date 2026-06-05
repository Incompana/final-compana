from __future__ import annotations

from pathlib import Path

from src.utils import pipeline_logger


def _configure_temp_logs(tmp_path: Path, monkeypatch) -> tuple[Path, Path, Path]:
    pipeline_path = tmp_path / "pipeline_steps.jsonl"
    failed_path = tmp_path / "failed_cases.jsonl"
    error_path = tmp_path / "pipeline_errors.jsonl"

    monkeypatch.setattr(pipeline_logger, "PIPELINE_LOG_FILE", pipeline_path)
    monkeypatch.setattr(pipeline_logger, "FAILED_CASE_LOG_FILE", failed_path)
    monkeypatch.setattr(pipeline_logger, "ERROR_LOG_FILE", error_path)
    return pipeline_path, failed_path, error_path



def test_log_pipeline_step_success_does_not_create_failed_case(tmp_path: Path, monkeypatch) -> None:
    pipeline_path, failed_path, _ = _configure_temp_logs(tmp_path, monkeypatch)

    row = pipeline_logger.log_pipeline_step(
        step_name="generate-action-plan",
        request_payload={"target_role": "frontend"},
        response_payload={"title": "Rencana Aksi", "clarification_needed": False},
        request_id="req-success-1",
    )

    assert row["request_id"] == "req-success-1"
    assert row["failed_case"] is False

    pipeline_rows = pipeline_logger.read_jsonl(pipeline_path)
    assert len(pipeline_rows) == 1
    assert pipeline_rows[0]["step"] == "generate-action-plan"

    assert failed_path.exists() is False



def test_log_pipeline_step_low_confidence_and_clarification_creates_failed_case(tmp_path: Path, monkeypatch) -> None:
    pipeline_path, failed_path, _ = _configure_temp_logs(tmp_path, monkeypatch)

    row = pipeline_logger.log_pipeline_step(
        step_name="analyze-pretext",
        request_payload={"pretext_text": "bingung"},
        response_payload={
            "confidence": 0.41,
            "clarification_needed": True,
            "target_role": "unclear",
            "problem_category": "unclear",
        },
        request_id="req-failed-1",
    )

    assert row["failed_case"] is True
    assert "low_confidence" in row["failed_case_reasons"]
    assert "clarification_needed" in row["failed_case_reasons"]

    pipeline_rows = pipeline_logger.read_jsonl(pipeline_path)
    failed_rows = pipeline_logger.read_jsonl(failed_path)

    assert len(pipeline_rows) == 1
    assert len(failed_rows) == 1
    assert failed_rows[0]["request_id"] == "req-failed-1"
    assert "low_confidence" in failed_rows[0]["failed_case_reasons"]



def test_log_pipeline_step_pending_status_creates_failed_case(tmp_path: Path, monkeypatch) -> None:
    _, failed_path, _ = _configure_temp_logs(tmp_path, monkeypatch)

    row = pipeline_logger.log_pipeline_step(
        step_name="evaluate-task",
        request_payload={"task_id": "cybersecurity_basic_nmap_explanation"},
        response_payload={
            "status": "pending",
            "confidence": 0.25,
            "assistive_note": "Tambahkan detail lagi.",
        },
        request_id="req-pending-1",
    )

    assert row["failed_case"] is True
    assert "status_pending" in row["failed_case_reasons"]

    failed_rows = pipeline_logger.read_jsonl(failed_path)
    assert len(failed_rows) == 1
    assert "status_pending" in failed_rows[0]["failed_case_reasons"]



def test_log_pipeline_error_writes_error_and_failed_case(tmp_path: Path, monkeypatch) -> None:
    _, failed_path, error_path = _configure_temp_logs(tmp_path, monkeypatch)

    error = ValueError("simulated pipeline failure")
    row = pipeline_logger.log_pipeline_error(
        step_name="map-gap-skills",
        request_payload={"target_role": "frontend"},
        error=error,
        request_id="req-error-1",
    )

    assert row["error_type"] == "ValueError"
    assert row["request_id"] == "req-error-1"

    error_rows = pipeline_logger.read_jsonl(error_path)
    failed_rows = pipeline_logger.read_jsonl(failed_path)

    assert len(error_rows) == 1
    assert len(failed_rows) == 1
    assert failed_rows[0]["failed_case_reasons"] == ["exception"]
    assert failed_rows[0]["error_message"] == "simulated pipeline failure"
