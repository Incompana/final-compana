"""FastAPI MVP app for the AI/ML Learning Path pipeline."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Engine 1 — ML + rule-based fallback
from ai_ml_module.engines.engine1_pretext import analyze_pretext

# Engine 2 — scoring matrix
from ai_ml_module.engines.engine2_question_selector import select_questions, generate_assessment

# Engine 3 — partial credit scoring + batch
from ai_ml_module.engines.engine3_assessment import score_answer, score_all_answers

# Engine 4 — weighted aggregation
from ai_ml_module.engines.engine4_profile_builder import build_skill_profile

# Engine 4b — context validator
from ai_ml_module.engines.context_validator import validate_context

# Engine 5-8
from ai_ml_module.engines.skill_gap_engine import generate_skill_gap
from ai_ml_module.engines.action_plan_recommender import generate_action_plan
from ai_ml_module.engines.evaluation_engine import evaluate_task
from ai_ml_module.engines.progress_engine import update_progress
from ai_ml_module.engines.compana_ai_assistant import (
    explain_skill_gap,
    generate_learning_references,
    generate_task_feedback,
)

# Model status helper
from ai_ml_module.settings import get_settings
from ai_ml_module.utils.loader import (
    get_model_status,
    load_label_taxonomy,
    load_role_skill_mapping,
    load_rubric_taxonomy,
    load_rubric_feedback_bank,
    load_task_bank,
)


settings = get_settings()


app = FastAPI(
    title="AI/ML Learning Path MVP",
    description="FastAPI endpoints for Engines 1-8 of the learning path advisor.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class FullPipelineRequest(BaseModel):
    user_id: str
    user_input_text: str


class AnalyzePretextRequest(BaseModel):
    user_input_text: str


class PredictProblemCategoryRequest(BaseModel):
    text: str
    top_k: int = 3


class SelectQuestionsRequest(BaseModel):
    pretext_analysis: Dict[str, Any]
    max_questions: int = 3


class ScoreAnswerRequest(BaseModel):
    question: Dict[str, Any]
    answer_text: str


class ScoreAllAnswersRequest(BaseModel):
    questions: List[Dict[str, Any]]
    answers: List[str]


class AssessmentAnswer(BaseModel):
    question_id: str
    answer: Optional[str] = None
    answer_value: Optional[str] = None
    answer_text: Optional[str] = None


class SubmitAssessmentRequest(BaseModel):
    user_id: str
    pretext_analysis: Dict[str, Any]
    questions: Optional[List[Dict[str, Any]]] = None
    answers: List[AssessmentAnswer]
    max_questions: int = 3


class BuildProfileRequest(BaseModel):
    assessment_results: List[Dict[str, Any]]
    target_role: str = ""


class SkillGapRequest(BaseModel):
    target_role: str
    user_skill_profile: Dict[str, int]


class ActionPlanRequest(BaseModel):
    skill_gap_result: Dict[str, Any]
    current_level: str
    owned_skills: List[str]


class EvaluateTaskRequest(BaseModel):
    task_id: str
    submission_text: str
    submission_files: List[str]


class TaskAiFeedbackRequest(BaseModel):
    task_id: str
    submission_text: str = ""
    submission_files: List[str] = Field(default_factory=list)


class TaskReferenceRequest(BaseModel):
    task_id: str


class SkillGapExplainRequest(BaseModel):
    skill_gap: Dict[str, Any]


class UpdateProgressRequest(BaseModel):
    user_id: str
    task_result: Dict[str, Any]
    previous_progress: Dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_skill_profile(skill_profile_result: Any) -> Dict[str, int]:
    """Ekstrak user_skill_profile dari output Engine 4."""
    if isinstance(skill_profile_result, dict):
        return skill_profile_result.get("user_skill_profile") or {}
    return skill_profile_result or {}


def simulate_answer(question: Dict[str, Any]) -> str:
    """Simulasi jawaban user untuk demo pipeline."""
    if str(question.get("answer_type") or "").lower() == "single_choice":
        question_id = str(question.get("question_id") or "")
        options = [item.strip() for item in str(question.get("options") or "").split("|") if item.strip()]
        if question_id == "Q_CLARIFY_BLOCKER" and "belum_ada_portfolio" in options:
            return "belum_ada_portfolio"
        if "paham_dasar" in options:
            return "paham_dasar"
        if "frontend_developer" in options:
            return "frontend_developer"
        if options:
            return options[0]

    prompt   = str(question.get("prompt") or question.get("question") or "").lower()
    keywords = str(question.get("expected_keywords") or "").lower()
    html_css = ["html", "css", "style", "layout", "responsive"]
    project  = ["project", "landing", "portfolio", "website"]
    js_dom   = ["javascript", "js", "dom", "addeventlistener", "queryselector", "click", "event"]

    if any(t in prompt or t in keywords for t in html_css):
        return "Saya bisa membuat halaman HTML dengan button dan onclick sederhana."
    if any(t in prompt or t in keywords for t in project):
        return "belum"
    if any(t in prompt or t in keywords for t in js_dom):
        return "belum"
    return "Saya sudah memahami dasar topik ini."


def _answer_value(item: AssessmentAnswer) -> str:
    return item.answer_value or item.answer_text or item.answer or ""


ROLE_FROM_ANSWER = {
    "frontend_developer": {"target_role": "frontend_developer", "domain_interest": "frontend"},
    "backend_developer": {"target_role": "backend_developer", "domain_interest": "backend"},
    "data_analyst": {"target_role": "data_analyst", "domain_interest": "data"},
    "ui_ux_designer": {"target_role": "ui_ux_designer", "domain_interest": "ui_ux"},
    "soc_analyst": {"target_role": "soc_analyst", "domain_interest": "cyber_security"},
}

BLOCKER_FROM_ANSWER = {
    "belum_tahu_role": "too_many_options",
    "belum_tahu_mulai": "no_starting_point",
    "skill_belum_cukup": "skill_gap_confusion",
    "belum_ada_portfolio": "no_portfolio",
    "takut_salah_pilih": "fear_wrong_path",
}


def _apply_clarification_answers(
    pretext: Dict[str, Any],
    answers: List[AssessmentAnswer],
) -> Dict[str, Any]:
    updated = dict(pretext)
    for item in answers:
        qid = str(item.question_id or "")
        value = _answer_value(item)
        if qid == "Q_CLARIFY_ROLE" and value in ROLE_FROM_ANSWER:
            updated.update(ROLE_FROM_ANSWER[value])
            updated["needs_assessment"] = True
            updated["confidence_score"] = max(float(updated.get("confidence_score") or 0), 0.55)
        if qid == "Q_CLARIFY_BLOCKER" and value in BLOCKER_FROM_ANSWER:
            updated["blocker_type"] = BLOCKER_FROM_ANSWER[value]
            if value == "takut_salah_pilih":
                updated["persona_type"] = "validation_seeker"
            elif value in {"belum_tahu_role", "belum_tahu_mulai"}:
                updated["persona_type"] = "beginner_explorer"
    return updated


def _score_assessment_submission(
    pretext: Dict[str, Any],
    questions: List[Dict[str, Any]],
    answers: List[AssessmentAnswer],
) -> Dict[str, Any]:
    pretext = _apply_clarification_answers(pretext, answers)
    answer_by_question = {item.question_id: _answer_value(item) for item in answers}

    scored = []
    normalized_answers = []
    for question in questions:
        qid = str(question.get("question_id") or "")
        answer_text = answer_by_question.get(qid, "")
        score_result = score_answer(question, answer_text)
        score_result["answer"] = answer_text
        scored.append(score_result)
        normalized_answers.append({"question_id": qid, "answer": answer_text})

    skill_profile_result = build_skill_profile(scored, target_role=pretext.get("target_role", ""))
    user_skill_profile = _extract_skill_profile(skill_profile_result)

    assessment_result = {
        "user_skill_profile": user_skill_profile,
        "assessment_validation_score": skill_profile_result.get("assessment_validation_score", 0.0)
            if isinstance(skill_profile_result, dict) else 0.0,
    }
    validated_context = validate_context(pretext, assessment_result)
    gap_result = generate_skill_gap(pretext.get("target_role"), user_skill_profile)
    gap_result["blocker_type"] = pretext.get("blocker_type")
    gap_result["problem_category"] = pretext.get("problem_category")
    owned_skills = [k for k, v in user_skill_profile.items() if v >= 1]
    action_plan_result = generate_action_plan(
        gap_result,
        current_level=pretext.get("current_level", "beginner"),
        owned_skills=owned_skills,
    )

    return {
        "assessment_questions": questions,
        "assessment_answers": normalized_answers,
        "scored_answers": scored,
        "skill_profile": skill_profile_result,
        "validated_context": validated_context,
        "skill_gap": gap_result,
        "action_plan": action_plan_result,
    }


# ---------------------------------------------------------------------------
# Health check endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "message": "AI/ML Learning Path MVP is running",
        "version": "0.2.0",
        "environment": settings.app_env,
        "engines": {
            "engine_1": "pretext_analyzer (ML + rule-based fallback)",
            "engine_2": "question_selector (scoring matrix)",
            "engine_3": "assessment_scoring (partial credit)",
            "engine_4": "skill_profile_builder (weighted aggregation)",
            "engine_5": "skill_gap (rule-based)",
            "engine_6": "action_plan (rule-based)",
            "engine_7": "evaluation (rubric-based)",
            "engine_8": "progress_tracking (rule-based)",
        },
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    """Lightweight uptime check for deployment platforms."""
    return {"status": "ok", "environment": settings.app_env}


@app.get("/readiness")
def readiness() -> Dict[str, Any]:
    """Check model and canonical datasets needed for the demo flow."""
    checks: Dict[str, Any] = {}
    try:
        taxonomy = load_label_taxonomy()
        role_df = load_role_skill_mapping()
        task_df = load_task_bank()
        rubric_df = load_rubric_feedback_bank()
        model = get_model_status()["problem_category_model"]

        checks = {
            "label_taxonomy_keys": sorted(taxonomy.keys()),
            "role_skill_rows": int(len(role_df)),
            "task_rows": int(len(task_df)),
            "rubric_rows": int(len(rubric_df)),
            "task_rows_by_role": {
                str(role): int(count)
                for role, count in task_df.groupby("target_role")["task_id"].count().to_dict().items()
            } if "target_role" in task_df.columns else {},
            "generic_task_title_count": int(
                task_df["task_title"].astype(str).str.contains(r"Task \d+ untuk", regex=True).sum()
            ) if "task_title" in task_df.columns else 0,
            "generic_task_description_count": int(
                task_df["task_description"].astype(str).str.contains("Deskripsi tugas mendalam di sini", regex=False).sum()
            ) if "task_description" in task_df.columns else 0,
            "problem_category_model_available": bool(model.get("available")),
            "problem_category_model_path": model.get("path"),
        }
        ready = (
            len(role_df) > 0
            and len(task_df) > 0
            and len(rubric_df) > 0
            and bool(model.get("available"))
        )
        return {"status": "ready" if ready else "degraded", "checks": checks}
    except Exception as exc:
        return {"status": "not_ready", "error": str(exc), "checks": checks}


@app.get("/model-status")
def model_status() -> Dict[str, Any]:
    """Health check: cek apakah ML model tersedia atau fallback rule-based."""
    status = get_model_status()
    return {
        "status": "ok",
        "models": status,
        "note": (
            "Jika tensorflow_problem_category_model.available = true, "
            "Engine 1 memakai TensorFlow .keras classifier. Jika tidak, "
            "fallback ke sklearn .joblib lalu rule-based."
        ),
    }


@app.get("/rubric-taxonomy")
def rubric_taxonomy() -> Dict[str, Any]:
    """Expose role-based rubric taxonomy used by task evaluation."""
    return load_rubric_taxonomy()


# ---------------------------------------------------------------------------
# Engine 1-4 individual endpoints
# ---------------------------------------------------------------------------

@app.post("/analyze-pretext")
def api_analyze_pretext(payload: AnalyzePretextRequest) -> Dict[str, Any]:
    """Engine 1: Analisis teks bebas user → structured pretext."""
    return analyze_pretext(payload.user_input_text)


@app.post("/predict-problem-category")
def api_predict_problem_category(payload: PredictProblemCategoryRequest) -> Dict[str, Any]:
    """Predict problem_category with the active classifier only."""
    from ai_ml_module.utils.model_loader import load_problem_category_model

    classifier = load_problem_category_model()
    if classifier is not None:
        if hasattr(classifier, "predict_one"):
            result = classifier.predict_one(payload.text, top_k=payload.top_k)
            return result

        prediction = str(classifier.predict([payload.text])[0])
        confidence = None
        top_k = [{"label": prediction, "confidence": None}]
        if hasattr(classifier, "predict_proba"):
            proba = classifier.predict_proba([payload.text])[0]
            classes = list(getattr(classifier, "classes_", []))
            if not classes and hasattr(classifier, "named_steps"):
                classes = list(getattr(classifier.named_steps.get("clf"), "classes_", []))
            ranked = sorted(
                zip(classes, proba),
                key=lambda item: float(item[1]),
                reverse=True,
            )[: payload.top_k]
            top_k = [{"label": str(label), "confidence": round(float(score), 6)} for label, score in ranked]
            confidence = top_k[0]["confidence"] if top_k else None
        return {
            "label": prediction,
            "confidence": confidence,
            "top_k": top_k,
            "model_type": "tfidf_linear_classifier",
            "classifier_type": "sklearn",
            "model_format": ".joblib",
        }

    analysis = analyze_pretext(payload.text)
    return {
        "label": analysis["problem_category"],
        "confidence": analysis.get("confidence_score"),
        "top_k": [{"label": analysis["problem_category"], "confidence": analysis.get("confidence_score")}],
        "model_type": "rule_based_pretext_analyzer",
        "classifier_type": "rule_based",
        "model_format": None,
    }


@app.post("/select-questions")
def api_select_questions(payload: SelectQuestionsRequest) -> Dict[str, Any]:
    """Engine 2: Pilih soal assessment berdasarkan pretext analysis."""
    return select_questions(payload.pretext_analysis, max_questions=payload.max_questions)


@app.post("/score-answer")
def api_score_answer(payload: ScoreAnswerRequest) -> Dict[str, Any]:
    """Engine 3: Score satu jawaban terhadap satu soal."""
    return score_answer(payload.question, payload.answer_text)


@app.post("/score-all-answers")
def api_score_all_answers(payload: ScoreAllAnswersRequest) -> Dict[str, Any]:
    """Engine 3 batch: Score semua jawaban sekaligus."""
    return score_all_answers(payload.questions, payload.answers)


@app.post("/submit-assessment")
def api_submit_assessment(payload: SubmitAssessmentRequest) -> Dict[str, Any]:
    """Submit jawaban assessment real user dan lanjutkan ke profile/gap/action plan."""
    questions = payload.questions
    if questions is None:
        questions = select_questions(payload.pretext_analysis, max_questions=payload.max_questions).get("questions") or []

    result = _score_assessment_submission(payload.pretext_analysis, questions, payload.answers)
    return {
        "input": {
            "user_id": payload.user_id,
            "pretext_analysis": payload.pretext_analysis,
        },
        **result,
    }


@app.post("/build-skill-profile")
def api_build_skill_profile(payload: BuildProfileRequest) -> Dict[str, Any]:
    """Engine 4: Bangun skill profile dari hasil assessment."""
    return build_skill_profile(payload.assessment_results, target_role=payload.target_role)


# ---------------------------------------------------------------------------
# Engine 5-8 individual endpoints
# ---------------------------------------------------------------------------

@app.post("/generate-skill-gap")
def api_generate_skill_gap(payload: SkillGapRequest) -> Dict[str, Any]:
    """Engine 5: Hitung skill gap untuk target role."""
    return generate_skill_gap(payload.target_role, payload.user_skill_profile)


@app.post("/generate-action-plan")
def api_generate_action_plan(payload: ActionPlanRequest) -> Dict[str, Any]:
    """Engine 6: Generate action plan dari skill gap."""
    return generate_action_plan(payload.skill_gap_result, payload.current_level, payload.owned_skills)


@app.post("/evaluate-task")
def api_evaluate_task(payload: EvaluateTaskRequest) -> Dict[str, Any]:
    """Engine 7: Evaluasi submission task berdasarkan rubrik."""
    return evaluate_task(payload.task_id, payload.submission_text, payload.submission_files)


@app.post("/compana-ai/task-feedback")
def api_compana_ai_task_feedback(payload: TaskAiFeedbackRequest) -> Dict[str, Any]:
    """Generate actionable task feedback with Gemini or deterministic fallback."""
    return generate_task_feedback(payload.task_id, payload.submission_text, payload.submission_files)


@app.post("/compana-ai/learning-references")
def api_compana_ai_learning_references(payload: TaskReferenceRequest) -> Dict[str, Any]:
    """Generate learning reference suggestions for a task."""
    return generate_learning_references(payload.task_id)


@app.post("/compana-ai/explain-skill-gap")
def api_compana_ai_explain_skill_gap(payload: SkillGapExplainRequest) -> Dict[str, Any]:
    """Explain skill gap output in user-facing language."""
    return explain_skill_gap(payload.skill_gap)


@app.post("/update-progress")
def api_update_progress(payload: UpdateProgressRequest) -> Dict[str, Any]:
    """Engine 8: Update progress dashboard user."""
    return update_progress(payload.user_id, payload.task_result, payload.previous_progress)


# ---------------------------------------------------------------------------
# Full pipeline (Engine 1-8)
# ---------------------------------------------------------------------------

@app.post("/full-pipeline-demo")
def full_pipeline_demo(payload: FullPipelineRequest) -> Dict[str, Any]:
    """Jalankan Engine 1-8 secara berurutan (demo end-to-end)."""

    # Engine 1 — Pretext Analysis
    pretext = analyze_pretext(payload.user_input_text)

    # Engine 2 — Question Selection
    assessment_output  = select_questions(pretext, max_questions=3)
    selected_questions = assessment_output.get("questions") or []

    # Simulasi jawaban user (demo only)
    answers = []
    for question in selected_questions:
        answer_text = simulate_answer(question)
        answers.append({"question_id": question.get("question_id"), "answer": answer_text})

    submission_result = _score_assessment_submission(
        pretext,
        selected_questions,
        [AssessmentAnswer(question_id=a["question_id"], answer=a["answer"]) for a in answers],
    )
    scored = submission_result["scored_answers"]
    skill_profile_result = submission_result["skill_profile"]
    user_skill_profile = _extract_skill_profile(skill_profile_result)
    validated_context = submission_result["validated_context"]
    gap_result = submission_result["skill_gap"]
    action_plan_result = submission_result["action_plan"]

    # Engine 7 — Task Evaluation
    recommended_tasks = action_plan_result.get("recommended_tasks") or []
    task_id           = recommended_tasks[0].get("task_id") if recommended_tasks else None
    if task_id:
        eval_result = evaluate_task(
            task_id,
            "Saya membuat halaman HTML dengan tombol. Ketika tombol diklik, teks berubah menggunakan addEventListener dan querySelector.",
            ["screenshot.png", "github_link"],
        )
    else:
        eval_result = {
            "task_id": None, "score": None, "status": "no_task",
            "feedback": [], "validated_skill": None, "criteria_results": [],
        }

    # Engine 8 — Progress Tracking
    prev_progress = {
        "current_path":     pretext.get("target_role"),
        "current_level":    pretext.get("current_level", "basic"),
        "completed_tasks":  0,
        "average_score":    0,
        "validated_skills": [k for k, v in user_skill_profile.items() if v >= 1],
        "weak_skills":      [k for k, v in user_skill_profile.items() if v == 1],
        "target_role":      pretext.get("target_role"),
    }
    progress_result = update_progress(payload.user_id, eval_result, prev_progress)

    return {
        "input":                {"user_id": payload.user_id, "user_input_text": payload.user_input_text},
        "pretext_analysis":     pretext,
        "assessment_questions": selected_questions,
        "assessment_answers":   answers,
        "skill_profile":        skill_profile_result,
        "validated_context":    validated_context,
        "skill_gap":            gap_result,
        "action_plan":          action_plan_result,
        "evaluation":           eval_result,
        "progress":             progress_result,
    }


@app.get("/demo/end-to-end")
def demo_end_to_end() -> Dict[str, Any]:
    """Use case demo yang bisa langsung dipakai frontend untuk alur end-to-end."""
    user_text = (
        "Saya ingin menjadi backend developer, tapi bingung apa saja yang harus dipelajari. "
        "Saya sudah belajar sekitar 2 tahun dan mengerti dasar SQL dan JavaScript, "
        "tetapi belum punya portofolio backend."
    )
    pipeline = full_pipeline_demo(FullPipelineRequest(user_id="demo_backend_user", user_input_text=user_text))
    validated_pretext = (
        pipeline.get("validated_context", {}).get("validated_analysis")
        or pipeline.get("pretext_analysis")
        or {}
    )
    pipeline["pretext_analysis"] = validated_pretext
    first_task = (pipeline.get("action_plan", {}).get("recommended_tasks") or [{}])[0]
    suggested_submission = (
        "Saya membuat repository GitHub untuk mini API backend. README berisi tujuan project, "
        "struktur folder, cara install dan menjalankan project, contoh endpoint GET /todos dan "
        "POST /todos, contoh request response JSON, serta screenshot endpoint berjalan."
    )
    evaluation = evaluate_task(
        first_task.get("task_id", ""),
        suggested_submission,
        ["github_backend_portfolio_link", "readme_screenshot.png", "api_endpoint_screenshot.png"],
    )

    previous_progress = {
        "current_path": validated_pretext.get("target_role"),
        "current_level": validated_pretext.get("current_level", "basic"),
        "completed_tasks": 0,
        "average_score": 0,
        "validated_skills": [],
        "weak_skills": [],
        "target_role": validated_pretext.get("target_role"),
    }
    progress = update_progress("demo_backend_user", evaluation, previous_progress)

    return {
        "use_case": {
            "title": "Backend Developer tanpa portfolio",
            "goal": "User mendapatkan role backend, task pertama yang jelas, submit bukti kerja, lalu menerima feedback.",
            "user_input_text": user_text,
            "suggested_submission": suggested_submission,
        },
        "rubric_taxonomy": load_rubric_taxonomy(),
        **pipeline,
        "demo_task_submission": {
            "task_id": first_task.get("task_id"),
            "submission_text": suggested_submission,
            "submission_files": ["github_backend_portfolio_link", "readme_screenshot.png", "api_endpoint_screenshot.png"],
        },
        "demo_evaluation": evaluation,
        "demo_progress": progress,
    }
