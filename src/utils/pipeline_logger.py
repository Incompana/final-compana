from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
PIPELINE_LOG_FILE = BASE_DIR / "logs" / "pipeline_steps.jsonl"
FAILED_CASE_LOG_FILE = BASE_DIR / "logs" / "failed_cases.jsonl"
ERROR_LOG_FILE = BASE_DIR / "logs" / "pipeline_errors.jsonl"

LOW_CONFIDENCE_THRESHOLD = 0.6


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=True) + "\n")


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_signals(response_payload: Dict[str, Any]) -> Dict[str, Any]:
    confidence = _to_float(response_payload.get("confidence"))

    clarification_needed = None
    if "clarification_needed" in response_payload:
        clarification_needed = bool(response_payload.get("clarification_needed"))

    fallback_triggered = None
    if "fallback_triggered" in response_payload:
        fallback_triggered = bool(response_payload.get("fallback_triggered"))

    status = response_payload.get("status")
    if status is not None:
        status = str(status)

    return {
        "confidence": confidence,
        "clarification_needed": clarification_needed,
        "fallback_triggered": fallback_triggered,
        "status": status,
    }


def _failed_case_reasons(signals: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []

    confidence = signals.get("confidence")
    if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
        reasons.append("low_confidence")

    if signals.get("clarification_needed") is True:
        reasons.append("clarification_needed")

    if signals.get("fallback_triggered") is True:
        reasons.append("fallback_triggered")

    status = signals.get("status")
    if status in {"pending", "need_revision"}:
        reasons.append(f"status_{status}")

    return reasons


def log_pipeline_step(
    step_name: str,
    request_payload: Dict[str, Any],
    response_payload: Dict[str, Any],
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    request_id = request_id or str(uuid.uuid4())
    signals = _extract_signals(response_payload)
    failed_reasons = _failed_case_reasons(signals)

    row = {
        "timestamp_utc": _now_utc_iso(),
        "request_id": request_id,
        "step": step_name,
        "confidence": signals["confidence"],
        "clarification_needed": signals["clarification_needed"],
        "fallback_triggered": signals["fallback_triggered"],
        "status": signals["status"],
        "failed_case": len(failed_reasons) > 0,
        "failed_case_reasons": failed_reasons,
        "request": request_payload,
        "response": response_payload,
    }

    _write_jsonl(PIPELINE_LOG_FILE, row)

    if failed_reasons:
        failed_row = {
            "timestamp_utc": row["timestamp_utc"],
            "request_id": request_id,
            "step": step_name,
            "failed_case_reasons": failed_reasons,
            "confidence": signals["confidence"],
            "clarification_needed": signals["clarification_needed"],
            "status": signals["status"],
            "request": request_payload,
            "response": response_payload,
        }
        _write_jsonl(FAILED_CASE_LOG_FILE, failed_row)

    return row


def log_pipeline_error(
    step_name: str,
    request_payload: Dict[str, Any],
    error: Exception,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    request_id = request_id or str(uuid.uuid4())

    row = {
        "timestamp_utc": _now_utc_iso(),
        "request_id": request_id,
        "step": step_name,
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "request": request_payload,
    }
    _write_jsonl(ERROR_LOG_FILE, row)

    failed_row = {
        "timestamp_utc": row["timestamp_utc"],
        "request_id": request_id,
        "step": step_name,
        "failed_case_reasons": ["exception"],
        "error_type": row["error_type"],
        "error_message": row["error_message"],
        "request": request_payload,
        "response": None,
    }
    _write_jsonl(FAILED_CASE_LOG_FILE, failed_row)

    return row


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows
