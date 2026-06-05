from __future__ import annotations

from fastapi import FastAPI

from src.api_models import (
    AnalyzePretextRequest,
    AnalyzePretextResponse,
    EvaluateTaskRequest,
    EvaluateTaskResponse,
    GenerateActionPlanRequest,
    GenerateActionPlanResponse,
    GenerateAssessmentRequest,
    GenerateAssessmentResponse,
    MapGapSkillsRequest,
    MapGapSkillsResponse,
)
from src.rule_engine.action_plan_generator import generate_action_plan
from src.rule_engine.baseline_pretext_engine import inspect_pretext
from src.rule_engine.gap_skill_mapper import map_gap_skills
from src.rule_engine.question_router import route_assessment_questions
from src.rule_engine.task_rubric_engine import evaluate_task_submission_with_rubric
from src.utils.pipeline_logger import log_pipeline_error, log_pipeline_step

app = FastAPI(
    title="Compana AI/ML Service",
    version="0.2.0",
    description=(
        "Minimal FastAPI layer for Compana rule-based AI/ML modules. "
        "No authentication is enabled in this baseline service."
    ),
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze-pretext", response_model=AnalyzePretextResponse)
def analyze_pretext_endpoint(payload: AnalyzePretextRequest) -> AnalyzePretextResponse:
    request_payload = payload.model_dump()
    try:
        result = inspect_pretext(payload.pretext_text)
        response = AnalyzePretextResponse(
            input_text=result["input_text"],
            normalized_text=result["normalized_text"],
            target_role=result["target_role"],
            problem_category=result["problem_category"],
            confidence=result["confidence"],
            clarification_needed=result["clarification_needed"],
            reasons=result["reasons"],
            matched_signals=result["matched_signals"],
        )
        log_pipeline_step("analyze-pretext", request_payload, response.model_dump())
        return response
    except Exception as error:
        log_pipeline_error("analyze-pretext", request_payload, error)
        raise


@app.post("/generate-assessment", response_model=GenerateAssessmentResponse)
def generate_assessment_endpoint(payload: GenerateAssessmentRequest) -> GenerateAssessmentResponse:
    request_payload = payload.model_dump()
    try:
        response_data = route_assessment_questions(
            pretext_analysis=payload.pretext_analysis.model_dump(),
            problem_category=payload.problem_category,
            target_role=payload.target_role,
            current_level=payload.current_level,
            blocker_type=payload.blocker_type,
        )
        response = GenerateAssessmentResponse(**response_data)
        log_pipeline_step("generate-assessment", request_payload, response.model_dump())
        return response
    except Exception as error:
        log_pipeline_error("generate-assessment", request_payload, error)
        raise


@app.post("/map-gap-skills", response_model=MapGapSkillsResponse)
def map_gap_skills_endpoint(payload: MapGapSkillsRequest) -> MapGapSkillsResponse:
    request_payload = payload.model_dump()
    try:
        response_data = map_gap_skills(
            target_role=payload.target_role,
            current_level=payload.current_level,
            assessment_answers=payload.assessment_answers,
            detected_skills=payload.detected_skills,
        )
        response = MapGapSkillsResponse(**response_data)
        log_pipeline_step("map-gap-skills", request_payload, response.model_dump())
        return response
    except Exception as error:
        log_pipeline_error("map-gap-skills", request_payload, error)
        raise


@app.post("/generate-action-plan", response_model=GenerateActionPlanResponse)
def generate_action_plan_endpoint(payload: GenerateActionPlanRequest) -> GenerateActionPlanResponse:
    request_payload = payload.model_dump()
    try:
        response_data = generate_action_plan(
            target_role=payload.target_role,
            problem_category=payload.problem_category,
            current_level=payload.current_level,
            blocker_type=payload.blocker_type,
            gap_skills=payload.gap_skills,
        )
        response = GenerateActionPlanResponse(**response_data)
        log_pipeline_step("generate-action-plan", request_payload, response.model_dump())
        return response
    except Exception as error:
        log_pipeline_error("generate-action-plan", request_payload, error)
        raise


@app.post("/evaluate-task", response_model=EvaluateTaskResponse)
def evaluate_task_endpoint(payload: EvaluateTaskRequest) -> EvaluateTaskResponse:
    request_payload = payload.model_dump()
    try:
        response_data = evaluate_task_submission_with_rubric(
            task_id=payload.task_id,
            submission_text=payload.submission_text,
        )
        response = EvaluateTaskResponse(**response_data)
        log_pipeline_step("evaluate-task", request_payload, response.model_dump())
        return response
    except Exception as error:
        log_pipeline_error("evaluate-task", request_payload, error)
        raise
