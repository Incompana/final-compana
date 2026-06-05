from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ProblemCategory(str, Enum):
    ROLE_CLARITY = "role_clarity"
    SKILL_GAP = "skill_gap"
    PORTFOLIO_EXECUTION = "portfolio_execution"
    INTERVIEW_PREP = "interview_prep"
    JOB_SEARCH_STRATEGY = "job_search_strategy"
    UNCLEAR = "unclear"


class CurrentLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    UNCLEAR = "unclear"


class BlockerType(str, Enum):
    KNOWLEDGE = "knowledge"
    EXECUTION = "execution"
    CONFIDENCE = "confidence"
    TIME = "time"
    FOCUS = "focus"
    UNCLEAR = "unclear"


class SkillPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClassificationResult(BaseModel):
    target_role: str
    problem_category: ProblemCategory
    current_level: CurrentLevel
    blocker_type: BlockerType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    fallback_triggered: bool = False
    clarification_prompt: Optional[str] = None


class PretextSignals(BaseModel):
    emotion: Literal["neutral", "distressed", "positive"]
    urgency: Literal["normal", "high"]


class PretextAnalyzeRequest(BaseModel):
    user_id: Optional[str] = None
    text: str = Field(..., min_length=1)
    recent_context: list[str] = Field(default_factory=list)


class PretextAnalyzeResponse(BaseModel):
    input_text: str
    normalized_text: str
    pretext_summary: str
    signals: PretextSignals
    classification: ClassificationResult
    next_action: Literal["generate_assessment", "ask_clarification"]


class AssessmentQuestion(BaseModel):
    id: str
    prompt: str
    answer_type: Literal["single_choice", "multi_choice", "text"]
    options: list[str] = Field(default_factory=list)
    required: bool = True


class GenerateAssessmentRequest(BaseModel):
    target_role: str
    problem_category: ProblemCategory
    current_level: CurrentLevel
    blocker_type: BlockerType


class GenerateAssessmentResponse(BaseModel):
    questions: list[AssessmentQuestion]
    rationale: list[str]


class MapGapSkillsRequest(BaseModel):
    target_role: str
    current_skills: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class MissingSkill(BaseModel):
    skill: str
    priority: SkillPriority
    why_missing: str
    example_task: str


class MapGapSkillsResponse(BaseModel):
    target_role: str
    current_skills_normalized: list[str]
    missing_skills: list[MissingSkill]
    confidence: float = Field(..., ge=0.0, le=1.0)
    fallback_triggered: bool = False
    rationale: list[str] = Field(default_factory=list)


class GenerateActionPlanRequest(BaseModel):
    target_role: str
    problem_category: ProblemCategory
    current_level: CurrentLevel
    gap_skills: list[str] = Field(default_factory=list)
    time_budget_hours_per_week: int = Field(default=5, ge=1, le=40)


class ActionPlanStep(BaseModel):
    step_number: int = Field(..., ge=1)
    title: str
    objective: str
    tasks: list[str]
    evidence_required: list[str]
    estimated_hours: int = Field(..., ge=1)


class GenerateActionPlanResponse(BaseModel):
    plan_title: str
    steps: list[ActionPlanStep]
    rationale: list[str]


class EvaluateTaskRequest(BaseModel):
    target_role: str
    task_type: str
    submission_text: str = Field(..., min_length=1)
    rubric_id: Optional[str] = None


class CriterionScore(BaseModel):
    criterion: str
    score: int = Field(..., ge=0)
    max_score: int = Field(..., ge=1)
    reason: str


class EvaluateTaskResponse(BaseModel):
    overall_score: int = Field(..., ge=0)
    max_score: int = Field(..., ge=1)
    status: Literal["good", "revise_minor", "revise_major"]
    criterion_scores: list[CriterionScore]
    feedback: list[str]
    next_attempt_focus: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    fallback_triggered: bool = False
