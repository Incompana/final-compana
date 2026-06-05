"""Evaluation Engine (Engine 7).

Provides rubric-based evaluation for task submissions. Main function:
`evaluate_task(task_id, submission_text, submission_files)`.
"""
from __future__ import annotations

from typing import Dict, Any, List
import math

import pandas as pd

from ai_ml_module.utils.loader import load_rubric_feedback_bank, load_rubric_taxonomy, load_task_bank


def _parse_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in ("1", "true", "yes", "y")


def _match_keywords(text: str, keywords: List[str]) -> bool:
    t = (text or "").lower()
    for k in keywords:
        if not k:
            continue
        if k.lower() in t:
            return True
    return False


def _rubric_from_task_checklist(task_id: str) -> pd.DataFrame:
    df_tasks = load_task_bank()
    row_task = df_tasks[df_tasks["task_id"].astype(str) == str(task_id)]
    if row_task.empty:
        return pd.DataFrame()

    checklist = str(row_task.iloc[0].get("assessment_checklist") or "").strip()
    if not checklist or checklist.lower() == "nan":
        return pd.DataFrame()

    criteria = [item.strip() for item in checklist.split("|") if item.strip()]
    if not criteria:
        return pd.DataFrame()

    weight = round(100.0 / len(criteria), 2)
    rows = []
    for index, item in enumerate(criteria, start=1):
        keywords = "|".join([
            word.strip(".,:;()").lower()
            for word in item.split()
            if len(word.strip(".,:;()")) >= 4
        ][:6])
        rows.append({
            "rubric_id": f"AUTO_{task_id}_{index}",
            "task_id": task_id,
            "criteria": item,
            "weight": weight,
            "required": True,
            "keyword_signal": keywords,
            "feedback_if_missing": f"Lengkapi bagian ini: {item}",
        })
    return pd.DataFrame(rows)


def _task_metadata(task_id: str) -> Dict[str, Any]:
    try:
        df_tasks = load_task_bank()
        row_task = df_tasks[df_tasks["task_id"].astype(str) == str(task_id)]
        if row_task.empty:
            return {}
        return row_task.iloc[0].to_dict()
    except Exception:
        return {}


def _role_score_format(target_role: str, taxonomy: Dict[str, Any]) -> List[Dict[str, Any]]:
    roles = taxonomy.get("roles") or {}
    role_config = roles.get(target_role) or roles.get(taxonomy.get("default_role")) or {}
    return role_config.get("score_format") or [
        {"key": "completion", "label": "Kelengkapan", "weight": 40, "keywords": ["hasil", "output", "link"]},
        {"key": "quality", "label": "Kualitas", "weight": 35, "keywords": ["jelas", "rapi", "struktur"]},
        {"key": "evidence", "label": "Bukti", "weight": 25, "keywords": ["screenshot", "github", "file"]},
    ]


def _infer_dimension(criteria: str, feedback: str, score_format: List[Dict[str, Any]]) -> str:
    text = f"{criteria} {feedback}".lower()
    best_key = score_format[0]["key"] if score_format else "completion"
    best_hits = -1
    for dim in score_format:
        hits = sum(1 for keyword in dim.get("keywords", []) if str(keyword).lower() in text)
        if hits > best_hits:
            best_hits = hits
            best_key = dim.get("key") or best_key
    return best_key


def _dimension_scores(
    criteria_results: List[Dict[str, Any]],
    score_format: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    dimension_weights = {dim["key"]: float(dim.get("weight") or 0) for dim in score_format}
    grouped: Dict[str, Dict[str, float]] = {
        dim["key"]: {"score_weight": 0.0, "total_weight": 0.0}
        for dim in score_format
    }

    for item in criteria_results:
        key = item.get("dimension") or (score_format[0]["key"] if score_format else "completion")
        grouped.setdefault(key, {"score_weight": 0.0, "total_weight": 0.0})
        weight = float(item.get("weight") or 0)
        grouped[key]["total_weight"] += weight
        if item.get("passed"):
            grouped[key]["score_weight"] += weight

    output = []
    for dim in score_format:
        key = dim["key"]
        total = grouped.get(key, {}).get("total_weight", 0.0)
        if total <= 0:
            continue
        score_weight = grouped.get(key, {}).get("score_weight", 0.0)
        score = round((score_weight / total) * 100.0, 1) if total > 0 else 0.0
        output.append({
            "key": key,
            "label": dim.get("label") or key.replace("_", " ").title(),
            "weight": dimension_weights.get(key, 0.0),
            "score": score,
            "passed_criteria": int(sum(1 for item in criteria_results if item.get("dimension") == key and item.get("passed"))),
            "total_criteria": int(sum(1 for item in criteria_results if item.get("dimension") == key)),
        })
    return output


def _skill_updates(target_skill: str, status: str, score: float, criteria_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not target_skill:
        return []

    if status == "passed":
        to_score = 2
        reason = "Task passed; skill target naik menjadi owned/siap dipakai."
    elif status == "needs_revision":
        to_score = 1
        missing = [item.get("criteria") for item in criteria_results if not item.get("passed")]
        reason = "Task perlu revisi; skill target naik/bertahan sebagai weak sampai criteria utama dilengkapi."
        if missing:
            reason += f" Criteria yang belum terpenuhi: {', '.join(str(x) for x in missing[:2])}."
    else:
        to_score = 0
        reason = "Submission belum cukup relevan; skill target tetap missing sampai output bisa dicek."

    return [{
        "skill_id": target_skill,
        "from_score": None,
        "to_score": to_score,
        "status": status,
        "reason": reason,
        "evidence": [
            f"Task evaluation status: {status}",
            f"Task evaluation score: {score}",
        ],
    }]


def evaluate_task(task_id: str, submission_text: str, submission_files: List[str]) -> Dict[str, Any]:
    task_meta = _task_metadata(task_id)
    target_role = str(task_meta.get("target_role") or "")
    target_skill = str(task_meta.get("target_skill_id") or "")
    taxonomy = load_rubric_taxonomy()
    score_format = _role_score_format(target_role, taxonomy)

    df_rub = load_rubric_feedback_bank()
    if df_rub.empty:
        return {"task_id": task_id, "score": None, "status": "no_rubric", "feedback": [], "criteria_results": []}

    # find column referencing task id
    col_candidates = [c for c in df_rub.columns if c.lower() in ("task_id", "id_tugas", "taskid")]
    if not col_candidates:
        return {"task_id": task_id, "score": None, "status": "no_task_ref_in_rubric", "feedback": [], "criteria_results": []}
    ref_col = col_candidates[0]
    rows = df_rub[df_rub[ref_col].astype(str) == str(task_id)]
    if rows.empty:
        rows = _rubric_from_task_checklist(task_id)
        if rows.empty:
            return {"task_id": task_id, "score": None, "status": "no_rubric_for_task", "feedback": [], "criteria_results": []}

    # prepare submission file tokens for file/link checks
    file_tokens = [str(f).lower() for f in (submission_files or [])]

    criteria_results = []
    total_weight = 0.0
    score_weight = 0.0
    missing_feedbacks = []
    positive_feedbacks = []
    required_pass_flags = []

    for _, r in rows.iterrows():
        rubric_id = r.get("rubric_id") or r.get("id") or ""
        criteria = str(r.get("criteria") or "").strip()
        weight = float(r.get("weight") or 0)
        required = _parse_bool(r.get("required"))
        keyword_signal = str(r.get("keyword_signal") or "").strip()
        feedback_if_missing = str(r.get("feedback_if_missing") or "")
        dimension = str(r.get("dimension") or "").strip()
        if not dimension or dimension.lower() == "nan":
            dimension = _infer_dimension(criteria, feedback_if_missing, score_format)

        total_weight += weight

        # parse keyword signals separated by pipe |
        keywords = [k.strip() for k in keyword_signal.split("|") if k.strip()]

        # check pass: keyword found in submission_text OR in submission_files tokens
        passed = False
        if keywords and _match_keywords(submission_text, keywords):
            passed = True
        else:
            # check in submitted files/links
            for k in keywords:
                for ft in file_tokens:
                    if k.lower() in ft:
                        passed = True
                        break
                if passed:
                    break

        if not passed:
            # also fallback: simple substring match of criteria text in submission
            if criteria and criteria.lower() in (submission_text or "").lower():
                passed = True

        if passed:
            score_weight += weight
            positive_feedbacks.append(f"Kriteria terpenuhi: {criteria}")
        else:
            if feedback_if_missing:
                missing_feedbacks.append(feedback_if_missing)

        if required:
            required_pass_flags.append(passed)

        criteria_results.append({
            "rubric_id": rubric_id,
            "criteria": criteria,
            "passed": bool(passed),
            "weight": weight,
            "dimension": dimension,
            "feedback_if_missing": feedback_if_missing,
        })

    score = 0.0
    if total_weight > 0:
        score = round((score_weight / total_weight) * 100.0, 1)

    # determine status per rules
    all_required_passed = all(required_pass_flags) if required_pass_flags else True
    thresholds = taxonomy.get("status_thresholds") or {}
    passed_threshold = float(thresholds.get("passed", 80.0))
    revision_threshold = float(thresholds.get("needs_revision", 60.0))
    if score >= passed_threshold and all_required_passed:
        status = "passed"
    elif revision_threshold <= score < passed_threshold:
        status = "needs_revision"
    else:
        status = "redo_task"

    # if required not passed, cannot be passed
    if not all_required_passed and status == "passed":
        status = "needs_revision"

    feedback: List[str] = [*positive_feedbacks, *missing_feedbacks]
    dimensions = _dimension_scores(criteria_results, score_format)

    return {
        "task_id": task_id,
        "score": score,
        "status": status,
        "feedback": feedback,
        "positive_feedback": positive_feedbacks,
        "revision_feedback": missing_feedbacks,
        "validated_skill": target_skill,
        "target_role": target_role,
        "score_format": [
            {
                "key": item.get("key"),
                "label": item.get("label"),
                "weight": item.get("weight"),
            }
            for item in score_format
        ],
        "dimension_scores": dimensions,
        "criteria_results": criteria_results,
        "skill_updates": _skill_updates(target_skill, status, score, criteria_results),
    }


def evaluate_submission(task_id: str, submission_text: str) -> Dict[str, Any]:
    # backward-compatible shim
    return evaluate_task(task_id, submission_text, [])
