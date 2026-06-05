"""Generative AI assistance with deterministic fallback.

This module keeps Compana AI optional. If no Gemini key is configured, the API
still returns structured, useful guidance from task/rubric context.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List

from ai_ml_module.settings import get_settings
from ai_ml_module.utils.loader import load_task_bank, load_rubric_feedback_bank


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def _task_by_id(task_id: str) -> Dict[str, Any]:
    try:
        df = load_task_bank()
        row = df[df["task_id"].astype(str) == str(task_id)]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()
    except Exception:
        return {}


def _rubric_for_task(task_id: str) -> List[Dict[str, Any]]:
    try:
        df = load_rubric_feedback_bank()
        rows = df[df["task_id"].astype(str) == str(task_id)]
        return rows.to_dict(orient="records")
    except Exception:
        return []


def _split_list(value: Any) -> List[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    return [item.strip() for item in text.split("|") if item.strip()]


def _fallback_task_feedback(task: Dict[str, Any], rubric: List[Dict[str, Any]], submission_text: str) -> Dict[str, Any]:
    checklist = _split_list(task.get("assessment_checklist"))
    missing = []
    lowered = (submission_text or "").lower()
    for item in checklist[:4]:
        keywords = [word.strip(".,:;()").lower() for word in item.split() if len(word.strip(".,:;()")) >= 5]
        if keywords and not any(keyword in lowered for keyword in keywords[:4]):
            missing.append(item)

    return {
        "provider": "deterministic_fallback",
        "summary": "Gunakan checklist task sebagai patokan revisi. Fokus pada output yang bisa dicek reviewer.",
        "strengths": [
            "Kamu sudah mulai mengarah ke task yang benar." if submission_text else "Task dan rubric sudah tersedia sebagai panduan kerja."
        ],
        "improvements": missing[:3] or [
            "Tambahkan bukti hasil berupa link, file, screenshot, atau output terminal.",
            "Jelaskan proses singkat: keputusan yang diambil, kendala, dan langkah berikutnya.",
        ],
        "next_steps": _split_list(task.get("task_steps"))[:3],
        "rubric_focus": [str(row.get("criteria")) for row in rubric[:4]],
    }


def _fallback_references(task: Dict[str, Any]) -> Dict[str, Any]:
    refs = _split_list(task.get("reference_keywords"))
    skill = str(task.get("target_skill_id") or "").replace("_", " ")
    return {
        "provider": "deterministic_fallback",
        "references": refs or [f"{skill} official documentation", f"{skill} beginner tutorial"],
        "study_order": [
            "Baca satu referensi utama selama 20-30 menit.",
            "Kerjakan step task sampai menghasilkan output kecil.",
            "Bandingkan output dengan checklist penilaian.",
        ],
    }


def _call_gemini(prompt: str) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return {"available": False, "error": "GEMINI_API_KEY is not configured"}

    url = f"{GEMINI_URL}?key={settings.gemini_api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"},
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"available": False, "error": str(exc)}

    text = (
        body.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "{}")
    )
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {"summary": text}
    parsed["provider"] = "gemini"
    return {"available": True, "result": parsed}


def generate_task_feedback(task_id: str, submission_text: str, submission_files: List[str] | None = None) -> Dict[str, Any]:
    task = _task_by_id(task_id)
    rubric = _rubric_for_task(task_id)
    fallback = _fallback_task_feedback(task, rubric, submission_text)
    prompt = json.dumps({
        "instruction": (
            "Berikan feedback task Compana dalam Bahasa Indonesia. "
            "Return JSON dengan keys: summary, strengths, improvements, next_steps, rubric_focus. "
            "Jangan mengarang skor; fokus pada saran yang actionable."
        ),
        "task": task,
        "rubric": rubric,
        "submission_text": submission_text,
        "submission_files": submission_files or [],
    }, ensure_ascii=False)
    generated = _call_gemini(prompt)
    if generated.get("available"):
        return generated["result"]
    fallback["provider_error"] = generated.get("error")
    return fallback


def generate_learning_references(task_id: str) -> Dict[str, Any]:
    task = _task_by_id(task_id)
    fallback = _fallback_references(task)
    prompt = json.dumps({
        "instruction": (
            "Buat rekomendasi referensi belajar untuk task Compana. "
            "Return JSON dengan keys: references, study_order. "
            "References berupa keyword atau nama dokumentasi resmi, bukan link palsu."
        ),
        "task": task,
    }, ensure_ascii=False)
    generated = _call_gemini(prompt)
    if generated.get("available"):
        return generated["result"]
    fallback["provider_error"] = generated.get("error")
    return fallback


def explain_skill_gap(skill_gap: Dict[str, Any]) -> Dict[str, Any]:
    missing = skill_gap.get("missing_skills") or []
    weak = skill_gap.get("weak_skills") or []
    priority = skill_gap.get("priority_gap")
    fallback = {
        "provider": "deterministic_fallback",
        "summary": f"Fokus pertama adalah {priority or 'task prioritas'} karena berada pada gap paling penting.",
        "focus_order": [
            item.get("skill_name") or item.get("skill_id")
            for item in [*missing, *weak][:5]
        ],
        "reason": [
            item.get("reason")
            for item in [*missing, *weak][:3]
            if item.get("reason")
        ],
    }
    prompt = json.dumps({
        "instruction": (
            "Jelaskan skill gap Compana secara singkat dan actionable. "
            "Return JSON dengan keys: summary, focus_order, reason."
        ),
        "skill_gap": skill_gap,
    }, ensure_ascii=False)
    generated = _call_gemini(prompt)
    if generated.get("available"):
        return generated["result"]
    fallback["provider_error"] = generated.get("error")
    return fallback
