"""Run a full pipeline demo (Engines 1-8 canonical flow)."""
from __future__ import annotations

import json
from pathlib import Path

from ai_ml_module.engines.pretext_analyzer import analyze_pretext
from ai_ml_module.engines.engine2_question_selector import select_questions
from ai_ml_module.engines.engine4_profile_builder import build_skill_profile
from ai_ml_module.engines.context_validator import validate_context

from ai_ml_module.engines.skill_gap_engine import generate_skill_gap
from ai_ml_module.engines.action_plan_recommender import generate_action_plan
from ai_ml_module.engines.evaluation_engine import evaluate_task
from ai_ml_module.engines.progress_engine import update_progress


OUT_DIR = Path("ai_ml_module/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_full_pipeline(free_text: str):
    pre = analyze_pretext(free_text)

    # select assessments
    qs = select_questions(pre)

    # simulate answers (reuse mvp_app sample)
    answers = {}
    if qs:
        answers[qs[0]["question_id"]] = "I can write basic HTML with a button and handle clicks using querySelector and addEventListener."
        if len(qs) > 1:
            answers[qs[1]["question_id"]] = "I know basics of JS event handling."

    assessments = []
    for q in qs:
        qid = q["question_id"]
        from ai_ml_module.engines.engine3_assessment import score_answer
        res = score_answer(q, answers.get(qid, ""))
        res["skill_id"] = q.get("skill_id")
        assessments.append(res)

    profile = build_skill_profile(assessments)

    # build a lightweight assessment_result structure for context validation
    avg_score = 0.0
    if assessments:
        avg_score = sum(float(a.get("score") or 0) for a in assessments) / (len(assessments) * 100.0)
    assessment_result = {"user_skill_profile": profile, "assessment_validation_score": round(avg_score, 2)}

    # validate context combining pretext and assessment results
    ctx = validate_context(pre, assessment_result)
    # if invalid, print reason but continue for demo
    if not ctx.get("validated_analysis"):
        print("Context validation returned unexpected shape")

    gap = generate_skill_gap(pre.get("target_role"), profile)

    plan = generate_action_plan(gap, current_level="basic", owned_skills=[k for k, v in profile.items() if v >= 1])

    task_id = None
    if plan.get("recommended_tasks"):
        task_id = plan["recommended_tasks"][0]["task_id"]

    if task_id:
        eval_res = evaluate_task(task_id, "Demo submission: uses addEventListener and querySelector", ["demo.png"])
    else:
        eval_res = {"task_id": None, "score": None, "status": "no_task", "feedback": []}

    prev = {
        "current_path": pre.get("target_role"),
        "current_level": "basic",
        "completed_tasks": 0,
        "average_score": 0,
        "validated_skills": [k for k, v in profile.items() if v >= 1],
        "weak_skills": [k for k, v in profile.items() if v == 1],
        "target_role": pre.get("target_role"),
    }

    prog = update_progress(user_id="demo", task_result=eval_res, previous_progress=prev)

    out = {
        "pretext": pre,
        "context_validation": ctx,
        "assessments": assessments,
        "skill_profile": profile,
        "skill_gap": gap,
        "action_plan": plan,
        "evaluation": eval_res,
        "progress": prog,
    }

    j = OUT_DIR / "full_pipeline_demo_result.json"
    with open(j, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    md = OUT_DIR / "full_pipeline_demo_report.md"
    with open(md, "w", encoding="utf-8") as fh:
        fh.write("# Full Pipeline Demo Report\n\n")
        fh.write(json.dumps(out, indent=2, ensure_ascii=False))

    print("Wrote results to", j, md)


if __name__ == "__main__":
    run_full_pipeline("I want to become a frontend developer. I know HTML and CSS but not JavaScript.")
