"""Progress Tracking Engine (Engine 8).

Provides `update_progress(user_id, task_result, previous_progress)` to update user dashboard.
Includes small placeholder clustering functions for learning patterns.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional

from ai_ml_module.utils.loader import load_task_bank, load_role_skill_mapping


def _safe_list(v):
    return list(v) if v else []


def update_progress(user_id: str, task_result: Dict[str, Any], previous_progress: Dict[str, Any]) -> Dict[str, Any]:
    # copy previous progress
    prog = dict(previous_progress or {})
    prog.setdefault("current_path", "")
    prog.setdefault("current_level", "beginner")
    prog.setdefault("completed_tasks", 0)
    prog.setdefault("average_score", 0.0)
    prog.setdefault("validated_skills", [])
    prog.setdefault("weak_skills", [])
    prog.setdefault("passed_task_ids", [])

    # update counts and validated skills if passed
    status = task_result.get("status")
    task_id = task_result.get("task_id")
    score = float(task_result.get("score") or 0)
    validated_skill = task_result.get("validated_skill")
    revision_count = int(task_result.get("revision_count") or 0)

    passed_task_ids = set(_safe_list(prog.get("passed_task_ids")))

    if status == "passed":
        prog["completed_tasks"] = int(prog.get("completed_tasks", 0)) + 1
        if validated_skill:
            vs = _safe_list(prog.get("validated_skills"))
            if validated_skill not in vs:
                vs.append(validated_skill)
            prog["validated_skills"] = vs
        # add passed task id
        if task_id:
            passed_task_ids.add(str(task_id))

    # update average_score
    prev_count = int(prog.get("completed_tasks", 0))
    # Note: prev_count currently includes the increment above; compute previous_count accordingly
    prev_count_minus = max(0, prev_count - (1 if status == "passed" else 0))
    prev_avg = float(prog.get("average_score") or 0.0)
    if status == "passed":
        new_avg = 0.0
        if prev_count_minus + 1 > 0:
            new_avg = (prev_avg * prev_count_minus + score) / (prev_count_minus + 1)
        prog["average_score"] = round(new_avg, 1)

    # revision handling: if revision_count >=3 mark validated_skill as weak
    if revision_count >= 3 and validated_skill:
        ws = _safe_list(prog.get("weak_skills"))
        if validated_skill not in ws:
            ws.append(validated_skill)
        prog["weak_skills"] = ws

    # persist passed_task_ids
    prog["passed_task_ids"] = list(passed_task_ids)

    # Level progression: use task_bank to determine difficulty of passed tasks
    try:
        df_tasks = load_task_bank()
        # count passed tasks by difficulty
        difficulty_counts = {"beginner": 0, "basic": 0, "intermediate": 0, "advanced": 0}
        for tid in passed_task_ids:
            r = df_tasks[df_tasks["task_id"].astype(str) == str(tid)]
            if not r.empty:
                diff = str(r.iloc[0].get("difficulty") or "").lower()
                if diff in difficulty_counts:
                    difficulty_counts[diff] += 1
    except Exception:
        difficulty_counts = {"beginner": 0, "basic": 0, "intermediate": 0, "advanced": 0}

    # Level up rules
    cur_level = prog.get("current_level")
    avg = float(prog.get("average_score") or 0.0)
    # promote beginner -> basic
    if cur_level == "beginner" and difficulty_counts.get("beginner", 0) >= 3 and avg >= 80.0:
        prog["current_level"] = "basic"
    # promote basic -> intermediate
    if cur_level == "basic" and difficulty_counts.get("basic", 0) >= 3 and avg >= 80.0:
        prog["current_level"] = "intermediate"

    # readiness_score: if role available in previous_progress, compute fraction of validated skills
    readiness = None
    target_role = prog.get("target_role")
    if target_role:
        try:
            role_map = load_role_skill_mapping()
            total_skills = len(role_map[role_map["role_id"] == target_role]["required_skill_id"].unique())
            validated = len(prog.get("validated_skills", []))
            if total_skills > 0:
                readiness = round(validated / total_skills, 2)
        except Exception:
            readiness = None
    prog["readiness_score"] = readiness

    # next_action: simple heuristic based on weak_skills or missing skills from previous_progress
    next_action = None
    ws = _safe_list(prog.get("weak_skills"))
    if ws:
        next_action = f"Lanjutkan ke task penguatan untuk {ws[0]}."
    else:
        # check if previous_progress has missing_skills
        missing = _safe_list(prog.get("missing_skills"))
        if missing:
            next_action = f"Kerjakan task prioritas: {missing[0]}."
        else:
            next_action = "Lanjutkan ke task berikutnya yang direkomendasikan."

    prog["next_action"] = next_action

    # optional: placeholder clustering patterns
    prog["learning_pattern"] = _detect_learning_pattern(prog)

    dashboard = {
        "current_path": prog.get("current_path"),
        "current_level": prog.get("current_level"),
        "readiness_score": prog.get("readiness_score"),
        "completed_tasks": prog.get("completed_tasks"),
        "average_score": prog.get("average_score"),
        "validated_skills": prog.get("validated_skills"),
        "weak_skills": prog.get("weak_skills"),
        "next_action": prog.get("next_action"),
    }

    return {"dashboard": dashboard, "internal": prog}


def _detect_learning_pattern(progress: Dict[str, Any]) -> str:
    # Placeholder heuristics for clustering
    completed = int(progress.get("completed_tasks", 0))
    avg = float(progress.get("average_score") or 0)
    revisions = 0
    if progress.get("passed_task_ids"):
        revisions = sum(1 for _ in progress.get("passed_task_ids", []) if True)

    if completed >= 8 and avg >= 85:
        return "fast_finisher"
    if completed >= 3 and avg >= 75 and revisions >= 1:
        return "consistent_but_needs_revision"
    if completed >= 3 and avg >= 85 and revisions == 0:
        return "slow_but_high_quality"
    return "stuck_beginner"

