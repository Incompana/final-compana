"""Demo runner for Engines 5-8.

Creates minimal fallback datasets if official files are missing, then runs
Engine 5 -> Engine 6 -> Engine 7 -> Engine 8 and writes results to outputs/.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from ai_ml_module.engines import (
    skill_gap_engine,
    action_plan_recommender,
    evaluation_engine,
    progress_engine,
)
from ai_ml_module.utils import loader


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_label_taxonomy():
    try:
        lt = loader.load_label_taxonomy()
        return lt
    except Exception:
        # create minimal taxonomy
        p = loader.DEFAULT_DATA_DIR / "label_taxonomy.json"
        loader.DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        minimal = {
            "intent": ["skill_gap", "action_plan", "evaluate_task"],
            "domain_interest": ["frontend", "backend"],
            "target_role": ["frontend_developer"],
            "problem_category": ["frontend_task"],
            "current_level": ["beginner", "basic", "intermediate", "advanced"],
            "blocker_type": ["none"],
            "persona_type": ["learner"]
        }
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(minimal, fh, indent=2)
        return minimal


def _ensure_role_skill_mapping():
    try:
        df = loader.load_role_skill_mapping()
        return df
    except Exception:
        # write minimal CSV to satisfy loader
        p = loader.DEFAULT_DATA_DIR / "role_skill_mapping.csv"
        loader.DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        rows = [
            {
                "role_id": "frontend_developer",
                "role_name": "Frontend Developer",
                "domain_interest": "frontend",
                "required_skill_id": "html_basic",
                "required_skill_name": "HTML (basic)",
                "skill_category": "markup",
                "priority": "high",
                "minimum_level": "basic",
                "step_order": 1,
                "prerequisite_skill_id": "",
            },
            {
                "role_id": "frontend_developer",
                "role_name": "Frontend Developer",
                "domain_interest": "frontend",
                "required_skill_id": "css_basic",
                "required_skill_name": "CSS (basic)",
                "skill_category": "style",
                "priority": "medium",
                "minimum_level": "basic",
                "step_order": 2,
                "prerequisite_skill_id": "html_basic",
            },
            {
                "role_id": "frontend_developer",
                "role_name": "Frontend Developer",
                "domain_interest": "frontend",
                "required_skill_id": "javascript_basic",
                "required_skill_name": "JavaScript (basic)",
                "skill_category": "programming",
                "priority": "high",
                "minimum_level": "basic",
                "step_order": 3,
                "prerequisite_skill_id": "",
            },
        ]
        df = pd.DataFrame(rows)
        df.to_csv(p, index=False)
        return df


def _ensure_task_bank():
    try:
        df = loader.load_task_bank()
        return df
    except Exception:
        p = loader.DEFAULT_DATA_DIR / "task_bank.csv"
        loader.DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        rows = [
            {
                "task_id": "T1",
                "domain_interest": "frontend",
                "target_role": "frontend_developer",
                "target_skill_id": "html_basic",
                "current_level": "basic",
                "task_title": "Buat halaman HTML sederhana dengan tombol",
                "task_description": "Buat halaman HTML dengan sebuah tombol yang mengubah teks ketika diklik.",
                "duration_estimate": "30m",
                "output_format": "html/github_link",
                "difficulty": "beginner",
                "prerequisite_skill_id": "",
            },
            {
                "task_id": "T2",
                "domain_interest": "frontend",
                "target_role": "frontend_developer",
                "target_skill_id": "css_basic",
                "current_level": "basic",
                "task_title": "Style halaman dengan CSS sederhana",
                "task_description": "Tambahkan style CSS untuk layout dan tombol.",
                "duration_estimate": "45m",
                "output_format": "html/github_link",
                "difficulty": "basic",
                "prerequisite_skill_id": "html_basic",
            },
            {
                "task_id": "T3",
                "domain_interest": "frontend",
                "target_role": "frontend_developer",
                "target_skill_id": "javascript_basic",
                "current_level": "basic",
                "task_title": "Interaksi tombol dengan JavaScript",
                "task_description": "Gunakan addEventListener dan querySelector untuk interaksi tombol.",
                "duration_estimate": "60m",
                "output_format": "html/github_link",
                "difficulty": "basic",
                "prerequisite_skill_id": "html_basic",
            },
        ]
        df = pd.DataFrame(rows)
        df.to_csv(p, index=False)
        return df


def _ensure_rubric_bank():
    try:
        df = loader.load_rubric_feedback_bank()
        return df
    except Exception:
        p = loader.DEFAULT_DATA_DIR / "rubric_feedback_bank.csv"
        loader.DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        rows = [
            {
                "rubric_id": "R1",
                "task_id": "T1",
                "criteria": "Halaman menampilkan tombol yang dapat diklik",
                "weight": 50,
                "required": True,
                "keyword_signal": "button|onclick|queryselector",
                "feedback_if_missing": "Tambahkan tombol yang dapat diklik dan pastikan ada event handler.",
            },
            {
                "rubric_id": "R2",
                "task_id": "T1",
                "criteria": "Teks berubah ketika tombol diklik",
                "weight": 50,
                "required": True,
                "keyword_signal": "addeventlistener|queryselector",
                "feedback_if_missing": "Implementasikan event listener untuk mengubah teks saat klik.",
            },
            {
                "rubric_id": "R3",
                "task_id": "T3",
                "criteria": "Menggunakan addEventListener dan querySelector",
                "weight": 100,
                "required": True,
                "keyword_signal": "addeventlistener|queryselector",
                "feedback_if_missing": "Gunakan addEventListener dan querySelector untuk interaksi.",
            },
        ]
        df = pd.DataFrame(rows)
        df.to_csv(p, index=False)
        return df


def run_demo():
    # ensure datasets available (or create minimal fallbacks)
    _ensure_label_taxonomy()
    _ensure_role_skill_mapping()
    _ensure_task_bank()
    _ensure_rubric_bank()

    # 1) Engine 5
    gap = skill_gap_engine.generate_skill_gap(
        target_role="frontend_developer",
        user_skill_profile={"html_basic": 2, "css_basic": 2, "javascript_basic": 0},
    )

    # 2) Engine 6
    plan = action_plan_recommender.generate_action_plan(
        skill_gap_result=gap,
        current_level="basic",
        owned_skills=["html_basic", "css_basic"],
    )

    # choose first task id for evaluation
    first_task = None
    if plan.get("recommended_tasks"):
        first_task = plan["recommended_tasks"][0]["task_id"]

    # 3) Engine 7
    eval_res = None
    if first_task:
        eval_res = evaluation_engine.evaluate_task(
            task_id=first_task,
            submission_text=(
                "Saya membuat halaman HTML dengan tombol. Ketika tombol diklik, "
                "teks berubah menggunakan addEventListener dan querySelector."
            ),
            submission_files=["screenshot.png", "github_link"],
        )
    else:
        eval_res = {"task_id": None, "score": None, "status": "no_task", "feedback": []}

    # 4) Engine 8
    prev = {
        "current_path": "Frontend Developer Foundation",
        "current_level": "basic",
        "completed_tasks": 0,
        "average_score": 0,
        "validated_skills": ["html_basic", "css_basic"],
        "weak_skills": [],
        "target_role": "frontend_developer",
    }

    prog = progress_engine.update_progress(user_id="U001", task_result=eval_res, previous_progress=prev)

    # assemble output
    out = {
        "engine_5_skill_gap": gap,
        "engine_6_action_plan": plan,
        "engine_7_evaluation": eval_res,
        "engine_8_progress": prog,
    }

    # write JSON
    jpath = OUT_DIR / "engine_5_8_demo_result.json"
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    # write short markdown report
    rpt = OUT_DIR / "engine_5_8_demo_report.md"
    with open(rpt, "w", encoding="utf-8") as fh:
        fh.write("# Engine 5-8 Demo Report\n\n")
        fh.write("## Skill Gap (Engine 5)\n\n")
        fh.write(json.dumps(gap, indent=2, ensure_ascii=False))
        fh.write("\n\n## Action Plan (Engine 6)\n\n")
        fh.write(json.dumps(plan, indent=2, ensure_ascii=False))
        fh.write("\n\n## Evaluation (Engine 7)\n\n")
        fh.write(json.dumps(eval_res, indent=2, ensure_ascii=False))
        fh.write("\n\n## Progress (Engine 8)\n\n")
        fh.write(json.dumps(prog, indent=2, ensure_ascii=False))

    print(f"Wrote demo result to: {jpath}")
    print(f"Wrote demo report to: {rpt}")


if __name__ == "__main__":
    run_demo()
