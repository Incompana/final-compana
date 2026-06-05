from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TargetRole = Literal["cybersecurity", "frontend", "backend", "data_analyst", "uiux", "unclear"]
ProblemCategory = Literal[
    "beginner_lost",
    "direction_confused",
    "skill_gap",
    "overwhelmed",
    "confidence_issue",
    "unclear",
]
CurrentLevel = Literal["zero", "basic", "intermediate", "unclear"]
BlockerType = Literal[
    "no_roadmap",
    "no_portfolio",
    "no_foundation",
    "no_time",
    "no_confidence",
    "too_many_options",
    "unclear",
]
EvaluationStatus = Literal["passed", "need_revision", "pending"]


class AnalyzePretextRequest(BaseModel):
    pretext_text: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pretext_text": "Aku mau jadi frontend tapi masih bingung mulai dari mana dan sering stuck pas bikin project."
            }
        }
    )


class AnalyzePretextResponse(BaseModel):
    input_text: str
    normalized_text: str
    target_role: TargetRole
    problem_category: ProblemCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    clarification_needed: bool
    reasons: List[str] = Field(default_factory=list)
    matched_signals: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input_text": "Aku mau jadi frontend tapi masih bingung mulai dari mana.",
                "normalized_text": "aku mau jadi frontend tapi masih bingung mulai dari mana",
                "target_role": "frontend",
                "problem_category": "beginner_lost",
                "confidence": 0.74,
                "clarification_needed": False,
                "reasons": [
                    "Role inferred from 1 matched signal(s).",
                    "Problem category inferred from 2 matched signal(s).",
                ],
                "matched_signals": {
                    "roles": {"frontend": ["\\bfront\\s?end\\b"]},
                    "problem_categories": {
                        "beginner_lost": ["\\bga\\s?tau\\s?mulai\\b", "\\bbingung\\b"]
                    },
                    "ambiguity": ["\\bbingung\\b"],
                },
            }
        }
    )


class PretextAnalysisInput(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0)
    clarification_needed: bool
    matched_signals: Dict[str, Any] = Field(default_factory=dict)


class GenerateAssessmentRequest(BaseModel):
    pretext_analysis: PretextAnalysisInput
    problem_category: ProblemCategory
    target_role: TargetRole
    current_level: CurrentLevel
    blocker_type: BlockerType

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pretext_analysis": {
                    "confidence": 0.78,
                    "clarification_needed": False,
                    "matched_signals": {"roles": {"frontend": ["\\breact\\b"]}},
                },
                "problem_category": "skill_gap",
                "target_role": "frontend",
                "current_level": "basic",
                "blocker_type": "no_portfolio",
            }
        }
    )


class RoutedQuestion(BaseModel):
    id: str
    prompt: str
    answer_type: Literal["single_choice", "multi_choice", "text"]
    options: List[str] = Field(default_factory=list)
    required: bool
    goal: str
    why_asked: str


class GenerateAssessmentResponse(BaseModel):
    router_version: str
    input_snapshot: Dict[str, Any]
    clarification_needed: bool
    decision_path: List[str]
    question_count: int = Field(..., ge=0)
    questions: List[RoutedQuestion]


class MapGapSkillsRequest(BaseModel):
    target_role: TargetRole
    current_level: CurrentLevel
    assessment_answers: Dict[str, Any] = Field(default_factory=dict)
    detected_skills: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_role": "cybersecurity",
                "current_level": "zero",
                "assessment_answers": {
                    "foundation_check": [
                        "Saya belum paham network",
                        "Saya baru belajar Linux command dasar"
                    ]
                },
                "detected_skills": ["linux"]
            }
        }
    )


class SkillGapRow(BaseModel):
    skill_id: str
    skill_name: str
    priority: Literal["high", "medium", "low"]
    evidence: List[str] = Field(default_factory=list)
    reason: str


class SuggestedTask(BaseModel):
    task_id: str
    title: str


class PrioritizedNextSkill(BaseModel):
    skill_id: str
    skill_name: str
    priority: Literal["high", "medium", "low"]
    gap_type: Literal["missing", "weak"]
    reason: str
    suggested_task: Optional[SuggestedTask] = None


class MapGapSkillsResponse(BaseModel):
    mapper_version: str
    target_role: str
    current_level: str
    clarification_needed: bool
    fallback_triggered: bool
    safe_next_action: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    detected_skill_ids: List[str] = Field(default_factory=list)
    missing_skills: List[SkillGapRow] = Field(default_factory=list)
    weak_skills: List[SkillGapRow] = Field(default_factory=list)
    prioritized_next_skills: List[PrioritizedNextSkill] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)


class GenerateActionPlanRequest(BaseModel):
    target_role: TargetRole
    problem_category: ProblemCategory
    current_level: CurrentLevel
    blocker_type: BlockerType
    gap_skills: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_role": "frontend",
                "problem_category": "skill_gap",
                "current_level": "basic",
                "blocker_type": "no_portfolio",
                "gap_skills": ["react_component_basics", "api_fetch_state"],
            }
        }
    )


class ActionPlanStep(BaseModel):
    order: int = Field(..., ge=1)
    title: str
    task_suggestion: str
    expected_output: str
    success_criteria: str


class GenerateActionPlanResponse(BaseModel):
    planner_version: str
    input_snapshot: Dict[str, Any]
    clarification_needed: bool
    title: str
    steps: List[ActionPlanStep]
    rationale: List[str]
    markdown_view: str


class EvaluateTaskRequest(BaseModel):
    task_id: str = Field(..., min_length=3)
    submission_text: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "frontend_simple_html_dashboard",
                "submission_text": "<html><head><meta name=\"viewport\" content=\"width=device-width\" /></head><body><h1>Dashboard</h1></body></html>",
            }
        }
    )


class DimensionScore(BaseModel):
    dimension: Literal["correctness", "completeness", "clarity", "technical_accuracy", "best_practice"]
    label: str
    score: int = Field(..., ge=0, le=2)
    max_score: int = Field(..., ge=1)
    weight: float = Field(..., ge=0.0)
    comment: str


class EvaluateTaskResponse(BaseModel):
    evaluator_version: str
    task_id: str
    status: EvaluationStatus
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    dimension_scores: List[DimensionScore] = Field(default_factory=list)
    weighted_score: Optional[float] = None
    weighted_max_score: Optional[float] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    assistive_note: str
