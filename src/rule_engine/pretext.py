from __future__ import annotations

from collections import OrderedDict
from typing import Optional

from src.preprocessing.text import normalize_text
from src.schemas import BlockerType, ClassificationResult, CurrentLevel, ProblemCategory

ROLE_KEYWORDS = OrderedDict(
    {
        "frontend_developer": ["frontend", "react", "javascript", "css", "ui", "web"],
        "backend_developer": ["backend", "api", "node", "express", "database", "server"],
        "data_analyst": ["data analyst", "analytics", "sql", "dashboard", "excel", "tableau"],
        "ui_ux_designer": ["ux", "ui ux", "figma", "wireframe", "prototype", "design"],
    }
)

PROBLEM_KEYWORDS = OrderedDict(
    {
        "role_clarity": ["which role", "career path", "confused role", "cannot decide", "decide"],
        "skill_gap": ["missing skill", "lack skill", "need to learn", "skill gap", "not good at"],
        "portfolio_execution": ["portfolio", "project", "cannot finish", "stuck building", "execution"],
        "interview_prep": ["interview", "technical interview", "behavioral", "mock interview"],
        "job_search_strategy": ["apply", "job search", "resume", "cv", "linkedin", "networking"],
    }
)

LEVEL_KEYWORDS = OrderedDict(
    {
        "beginner": ["beginner", "new", "just started", "no experience"],
        "intermediate": ["intermediate", "some experience", "1 year", "2 years"],
        "advanced": ["advanced", "senior", "lead", "expert", "5 years"],
    }
)

BLOCKER_KEYWORDS = OrderedDict(
    {
        "knowledge": ["don't know", "do not know", "no idea", "not sure", "lack knowledge"],
        "execution": ["procrastinate", "stuck", "cannot finish", "inconsistent", "overwhelmed"],
        "confidence": ["anxious", "afraid", "not confident", "imposter", "scared"],
        "time": ["no time", "busy", "schedule", "full time"],
        "focus": ["distracted", "too many interests", "cannot focus", "switching"],
    }
)

DISTRESS_KEYWORDS = ["anxious", "stressed", "overwhelmed", "panic", "afraid"]
POSITIVE_KEYWORDS = ["motivated", "excited", "ready"]
URGENT_KEYWORDS = ["urgent", "asap", "immediately", "deadline", "this week"]


def _rank_labels(text: str, keyword_map: OrderedDict[str, list[str]]) -> list[tuple[str, int, list[str]]]:
    ranked: list[tuple[str, int, list[str]]] = []
    for label, keywords in keyword_map.items():
        hits = [keyword for keyword in keywords if keyword in text]
        ranked.append((label, len(hits), hits))
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked


def _safe_problem(label: str) -> ProblemCategory:
    return ProblemCategory(label) if label in ProblemCategory._value2member_map_ else ProblemCategory.UNCLEAR


def _safe_level(label: str) -> CurrentLevel:
    return CurrentLevel(label) if label in CurrentLevel._value2member_map_ else CurrentLevel.UNCLEAR


def _safe_blocker(label: str) -> BlockerType:
    return BlockerType(label) if label in BlockerType._value2member_map_ else BlockerType.UNCLEAR


def _build_clarification(
    matched_roles: list[str],
    problem_category: ProblemCategory,
    blocker_type: BlockerType,
) -> Optional[str]:
    if len(matched_roles) > 1:
        return "Choose one target role for the next 4 weeks so the plan can stay focused."
    if problem_category == ProblemCategory.UNCLEAR:
        return "What exact outcome do you want in the next 30 days (role, portfolio, interview, or job search)?"
    if blocker_type == BlockerType.UNCLEAR:
        return "What is your main blocker right now: knowledge, execution, confidence, time, or focus?"
    return None


def analyze_pretext(text: str) -> tuple[ClassificationResult, str, str, str, str, str]:
    normalized = normalize_text(text)
    word_count = len(normalized.split())

    role_ranked = _rank_labels(normalized, ROLE_KEYWORDS)
    problem_ranked = _rank_labels(normalized, PROBLEM_KEYWORDS)
    level_ranked = _rank_labels(normalized, LEVEL_KEYWORDS)
    blocker_ranked = _rank_labels(normalized, BLOCKER_KEYWORDS)

    matched_roles = [label for label, score, _ in role_ranked if score > 0]
    target_role = matched_roles[0] if matched_roles else "unknown"

    best_problem_label, best_problem_score, best_problem_hits = problem_ranked[0]
    best_level_label, best_level_score, best_level_hits = level_ranked[0]
    best_blocker_label, best_blocker_score, best_blocker_hits = blocker_ranked[0]

    if best_problem_score == 0:
        best_problem_label = ProblemCategory.UNCLEAR.value
    if best_level_score == 0:
        best_level_label = CurrentLevel.UNCLEAR.value
    if best_blocker_score == 0:
        best_blocker_label = BlockerType.UNCLEAR.value

    if word_count < 3:
        best_problem_label = ProblemCategory.UNCLEAR.value
        best_blocker_label = BlockerType.UNCLEAR.value

    problem_category = _safe_problem(best_problem_label)
    current_level = _safe_level(best_level_label)
    blocker_type = _safe_blocker(best_blocker_label)

    confidence_components = [
        1 if target_role != "unknown" else 0,
        1 if problem_category != ProblemCategory.UNCLEAR else 0,
        1 if current_level != CurrentLevel.UNCLEAR else 0,
        1 if blocker_type != BlockerType.UNCLEAR else 0,
    ]
    confidence = sum(confidence_components) / 4
    if len(matched_roles) > 1:
        confidence -= 0.2
    if word_count < 5:
        confidence = min(confidence, 0.35)
    confidence = round(max(0.05, min(1.0, confidence)), 2)

    reasons: list[str] = []
    if target_role != "unknown":
        reasons.append(f"Matched role keywords: {', '.join(role_ranked[0][2])}")
    if best_problem_hits:
        reasons.append(f"Matched problem keywords: {', '.join(best_problem_hits)}")
    if best_level_hits:
        reasons.append(f"Matched level keywords: {', '.join(best_level_hits)}")
    if best_blocker_hits:
        reasons.append(f"Matched blocker keywords: {', '.join(best_blocker_hits)}")
    if len(matched_roles) > 1:
        reasons.append(f"Multiple role signals detected: {', '.join(matched_roles)}")

    fallback_triggered = (
        confidence < 0.55
        or problem_category == ProblemCategory.UNCLEAR
        or blocker_type == BlockerType.UNCLEAR
        or len(matched_roles) > 1
    )

    clarification_prompt = _build_clarification(matched_roles, problem_category, blocker_type)

    emotion = "neutral"
    if any(keyword in normalized for keyword in DISTRESS_KEYWORDS):
        emotion = "distressed"
    elif any(keyword in normalized for keyword in POSITIVE_KEYWORDS):
        emotion = "positive"

    urgency = "high" if any(keyword in normalized for keyword in URGENT_KEYWORDS) else "normal"

    summary = (
        f"User appears focused on {problem_category.value.replace('_', ' ')} "
        f"with primary blocker {blocker_type.value.replace('_', ' ')}."
    )

    next_action = "ask_clarification" if fallback_triggered else "generate_assessment"

    classification = ClassificationResult(
        target_role=target_role,
        problem_category=problem_category,
        current_level=current_level,
        blocker_type=blocker_type,
        confidence=confidence,
        reasons=reasons,
        fallback_triggered=fallback_triggered,
        clarification_prompt=clarification_prompt,
    )
    return classification, normalized, summary, emotion, urgency, next_action
