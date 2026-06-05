"""MVP app: run end-to-end pipeline Engines 1-8 in sequence (CLI demo)."""
from __future__ import annotations

import json
from pathlib import Path

from ai_ml_module.engines.engine1_pretext_ml import analyze_pretext
from ai_ml_module.engines.engine2_question_selector import select_questions
from ai_ml_module.engines.engine3_assessment import score_answer
from ai_ml_module.engines.engine4_profile_builder import build_skill_profile

from ai_ml_module.engines.skill_gap_engine import generate_skill_gap
from ai_ml_module.engines.action_plan_recommender import generate_action_plan
from ai_ml_module.engines.evaluation_engine import evaluate_task
from ai_ml_module.engines.progress_engine import update_progress


OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)


def run_pipeline(free_text: str):
    pre = analyze_pretext(free_text)
    print("Pretext analysis:", pre)

    questions = select_questions(pre)
    print("Selected questions:", questions)

    # simulate user answers (simple heuristics)
    answers = {}
    answers[questions[0]["question_id"]] = "I can write basic HTML with a button and handle clicks using querySelector and addEventListener."
    if len(questions) > 1:
        answers[questions[1]["question_id"]] = "I know the concept but not comfortable writing JS event handlers yet."

    assessments = []
    for q in questions:
        qid = q["question_id"]
        ans = answers.get(qid, "")
        res = score_answer(q, ans)
        # attach skill id for profile builder
        res["skill_id"] = q.get("skill_id")
        assessments.append(res)

    profile = build_skill_profile(assessments)
    print("Built skill profile:", profile)

    # Validate context (light): ensure target role present
    target_role = pre.get("target_role")

    # Engine 5: skill gap
    gap = generate_skill_gap(target_role, profile)
    print("Skill gap:", gap)

    # Engine 6: action plan
    plan = generate_action_plan(gap, current_level="basic", owned_skills=[k for k, v in profile.items() if v >= 1])
    print("Action plan:", plan)

    # pick first recommended task and simulate submission
    task_id = None
    if plan.get("recommended_tasks"):
        task_id = plan["recommended_tasks"][0]["task_id"]

    if task_id:
        eval_res = evaluate_task(task_id, "Saya membuat halaman HTML dengan tombol. Ketika tombol diklik, teks berubah menggunakan addEventListener dan querySelector.", ["screenshot.png"])
    else:
        eval_res = {"task_id": None, "score": None, "status": "no_task", "feedback": []}

    print("Evaluation result:", eval_res)

    prev = {
        "current_path": f"{target_role} path",
        "current_level": "basic",
        "completed_tasks": 0,
        "average_score": 0,
        "validated_skills": [k for k, v in profile.items() if v >= 1],
        "weak_skills": [k for k, v in profile.items() if v == 1],
        "target_role": target_role,
    }

    prog = update_progress(user_id="U999", task_result=eval_res, previous_progress=prev)
    print("Progress dashboard:", prog)

    out = {
        "pretext": pre,
        "assessments": assessments,
        "skill_profile": profile,
        "skill_gap": gap,
        "action_plan": plan,
        "evaluation": eval_res,
        "progress": prog,
    }

    p = OUT_DIR / "mvp_pipeline_result.json"
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print(f"Wrote pipeline output to {p}")


if __name__ == "__main__":
    sample_text = "I want a learning path to become a frontend developer. I know HTML and CSS but not JavaScript."
    run_pipeline(sample_text)
