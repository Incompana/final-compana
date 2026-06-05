"""Action Plan Recommender (Engine 6).

Implements generate_action_plan(skill_gap_result, current_level, owned_skills) -> dict
using the official `task_bank.csv` contract.
"""
from __future__ import annotations

from typing import Dict, Any, List

import pandas as pd

from ai_ml_module.utils.loader import load_task_bank


LEVEL_RANK = {"beginner": 0, "basic": 1, "intermediate": 2, "advanced": 3}


def _level_match(task_level: str, user_level: str) -> float:
    # exact match => 1.0, one step above => 0.5, otherwise 0.0
    tl = LEVEL_RANK.get(str(task_level).lower(), 1)
    ul = LEVEL_RANK.get(str(user_level).lower(), 1)
    if tl == ul:
        return 1.0
    if tl == ul + 1:
        return 0.5
    return 0.0


def _clean_cell(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def generate_action_plan(skill_gap_result: Dict[str, Any], current_level: str, owned_skills: List[str], max_recommend: int = 3) -> Dict[str, Any]:
    """Generate recommended tasks based on skill gaps and task bank.

    Rules implemented per spec.
    """
    # load task bank
    task_df = load_task_bank()
    target_role = skill_gap_result.get("target_role")
    blocker_type = skill_gap_result.get("blocker_type")
    priority_gap = skill_gap_result.get("priority_gap")
    missing_skills = [s if isinstance(s, str) else s.get("skill_id") for s in skill_gap_result.get("missing_skills", [])]
    weak_skills = [s if isinstance(s, str) else s.get("skill_id") for s in skill_gap_result.get("weak_skills", [])]

    if task_df.empty:
        return {"recommended_tasks": _fallback_tasks(target_role, priority_gap, missing_skills, weak_skills, max_recommend, blocker_type)}

    owned_set = set(owned_skills or [])

    # filter tasks to the same role
    df = task_df[task_df["target_role"] == target_role].copy()

    candidates = []

    # Helper to compute match scores
    for _, row in df.iterrows():
        task_id = row.get("task_id")
        task_skill = _clean_cell(row.get("target_skill_id"))
        prereq = _clean_cell(row.get("prerequisite_skill_id"))
        # Rule 1: skip if prerequisite exists and not owned
        if prereq and prereq not in owned_set:
            continue
        # target_skill_match: 1 if task_skill in missing_skills, 0.6 if in weak_skills, else 0
        if task_skill in missing_skills:
            target_skill_match = 1.0
        elif task_skill in weak_skills:
            target_skill_match = 0.6
        else:
            target_skill_match = 0.0

        # priority_gap_match: 1 if task_skill equals priority_gap
        priority_gap_match = 1.0 if (priority_gap and task_skill == priority_gap) else 0.0

        # level_match
        level_match = _level_match(row.get("current_level"), current_level)

        # prerequisite_ready already enforced by filter; set to 1.0
        prerequisite_ready = 1.0

        task_text = " ".join([
            str(row.get("task_title") or ""),
            str(row.get("task_description") or ""),
            str(row.get("output_format") or ""),
        ]).lower()
        blocker_match = 1.0 if (
            blocker_type == "no_portfolio"
            and any(keyword in task_text for keyword in ("portfolio", "repository", "readme"))
        ) else 0.0
        if blocker_match:
            target_skill_match = max(target_skill_match, 0.6)

        task_score = (
            target_skill_match * 0.40
            + priority_gap_match * 0.25
            + level_match * 0.20
            + prerequisite_ready * 0.15
            + blocker_match * 0.35
        )

        candidates.append({
            "task_id": task_id,
            "task_title": row.get("task_title"),
            "task_description": row.get("task_description"),
            "target_skill": task_skill,
            "duration_estimate": row.get("duration_estimate"),
            "difficulty": row.get("difficulty"),
            "output_format": row.get("output_format"),
            "learning_focus": _clean_cell(row.get("learning_focus")),
            "task_steps": _clean_cell(row.get("task_steps")),
            "assessment_checklist": _clean_cell(row.get("assessment_checklist")),
            "reference_keywords": _clean_cell(row.get("reference_keywords")),
            "prerequisite_skill_id": prereq,
            "task_score": round(float(task_score), 2),
            "priority_gap_match": priority_gap_match,
            "target_skill_match": target_skill_match,
            "blocker_match": blocker_match,
        })

    # If no candidate matches priority_gap, expand search to weak_skills (already included),
    # otherwise candidates list already covers both.

    if not candidates:
        return {"recommended_tasks": _fallback_tasks(target_role, priority_gap, missing_skills, weak_skills, max_recommend, blocker_type)}

    # sort by task_score desc; ensure tasks with priority_gap are prioritized
    candidates.sort(key=lambda x: (-x["task_score"], -x["priority_gap_match"]))

    # limit
    recommended = []
    for c in candidates[:max_recommend]:
        reason = ""
        if c.get("blocker_match"):
            reason = "Kamu menyebut belum punya portofolio, jadi task ini diprioritaskan untuk menghasilkan bukti proyek nyata."
        elif c["target_skill"] == priority_gap:
            reason = f"{c['target_skill']} adalah missing skill prioritas tertinggi untuk {target_role}."
        elif c["target_skill"] in missing_skills:
            reason = f"{c['target_skill']} adalah skill yang hilang untuk {target_role}."
        elif c["target_skill"] in weak_skills:
            reason = f"{c['target_skill']} terdeteksi lemah; direkomendasikan untuk memperkuat." 
        else:
            reason = f"Task relevan dengan peran {target_role}."

        recommended.append({
            "task_id": c["task_id"],
            "task_title": c["task_title"],
            "task_description": c["task_description"],
            "target_skill": c["target_skill"],
            "reason": reason,
            "duration_estimate": c["duration_estimate"],
            "difficulty": c["difficulty"],
            "output_format": c["output_format"],
            "learning_focus": c["learning_focus"],
            "task_steps": c["task_steps"],
            "assessment_checklist": c["assessment_checklist"],
            "reference_keywords": c["reference_keywords"],
            "task_score": c["task_score"],
        })

    return {"recommended_tasks": recommended}


def _humanize_skill(skill_id: str) -> str:
    mapping = {
        "html_basic": "HTML dasar",
        "css_basic": "CSS dasar",
        "javascript_basic": "JavaScript dasar",
        "sql_basic": "SQL dasar",
        "python_basic": "Python dasar",
        "rest_api": "REST API",
        "mysql": "MySQL",
        "git": "Git",
        "java": "Java",
        "php": "PHP",
    }
    return mapping.get(str(skill_id or ""), str(skill_id or "").replace("_", " ").title())


def _fallback_tasks(
    target_role: str,
    priority_gap: str,
    missing_skills: List[str],
    weak_skills: List[str],
    max_recommend: int,
    blocker_type: str = "",
) -> List[Dict[str, Any]]:
    ordered_skills = []
    if priority_gap:
        ordered_skills.append(priority_gap)
    ordered_skills.extend([s for s in missing_skills if s and s not in ordered_skills])
    ordered_skills.extend([s for s in weak_skills if s and s not in ordered_skills])

    tasks = []
    if blocker_type == "no_portfolio":
        role_label = str(target_role or "").replace("_", " ").title()
        portfolio_skill = priority_gap or (missing_skills[0] if missing_skills else "portfolio")
        tasks.append({
            "task_id": f"fallback_{target_role}_portfolio",
            "task_title": f"Buat mini portfolio {role_label}",
            "target_skill": portfolio_skill,
            "reason": f"Kamu menyebut belum punya portofolio, jadi output nyata perlu diprioritaskan untuk {target_role}.",
            "duration_estimate": "Hari ini",
            "difficulty": "practice",
            "output_format": "github_link/screenshot/catatan pendek",
            "learning_focus": "Portfolio kecil, dokumentasi hasil kerja, dan bukti proses belajar",
            "task_steps": "Pilih satu skill prioritas yang ingin dibuktikan|Buat output kecil yang bisa dilihat reviewer|Tulis README singkat berisi tujuan, cara menjalankan, dan hasil|Lampirkan screenshot atau link hasil kerja",
            "assessment_checklist": "Ada output nyata|Ada penjelasan proses|Ada link atau screenshot|Ada catatan bagian yang masih perlu dipelajari",
            "reference_keywords": "GitHub README portfolio|project documentation basics",
            "task_score": 0.9,
        })

    for index, skill in enumerate(ordered_skills[:max_recommend], start=1):
        if len(tasks) >= max_recommend:
            break
        skill_label = _humanize_skill(skill)
        is_weak = skill in weak_skills and skill not in missing_skills
        tasks.append({
            "task_id": f"fallback_{target_role}_{skill}",
            "task_title": f"Latihan {skill_label} untuk {target_role}",
            "target_skill": skill,
            "reason": (
                f"{skill_label} terdeteksi lemah; direkomendasikan untuk memperkuat."
                if is_weak
                else f"{skill_label} adalah missing skill prioritas untuk {target_role}."
            ),
            "duration_estimate": "1-2 hari" if index > 1 else "Hari ini",
            "difficulty": "practice",
            "output_format": "catatan belajar/link/screenshot",
            "learning_focus": f"Konsep inti {skill_label}, contoh sederhana, dan bukti hasil latihan",
            "task_steps": f"Pelajari konsep dasar {skill_label} dari satu referensi utama|Buat contoh kecil yang memakai {skill_label}|Jalankan atau demonstrasikan contoh tersebut|Tulis 3 poin yang sudah paham dan 1 hal yang masih membingungkan",
            "assessment_checklist": f"Ada contoh penggunaan {skill_label}|Ada output yang bisa dicek|Ada penjelasan proses|Ada catatan kendala atau pertanyaan lanjutan",
            "reference_keywords": f"{skill_label} basic tutorial|{skill_label} official documentation",
            "task_score": 0.75 if index == 1 else 0.6,
        })
    return tasks


def recommend_action_plan(gap_output: Dict[str, Any], max_tasks: int = 5) -> Dict[str, Any]:
    # backward-compatible wrapper using run inputs
    target_role = gap_output.get("target_role")
    current_level = gap_output.get("current_level") or gap_output.get("current_level")
    owned = gap_output.get("owned_skills") or gap_output.get("owned_skills", [])
    return generate_action_plan(gap_output, current_level, owned, max_recommend=max_tasks)
