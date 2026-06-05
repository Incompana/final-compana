from __future__ import annotations

import re

from src.schemas import CriterionScore, EvaluateTaskResponse

ACTION_VERBS = {
    "built",
    "created",
    "designed",
    "implemented",
    "analyzed",
    "optimized",
    "improved",
    "developed",
    "led",
}

TASK_RUBRICS = {
    "portfolio_project": ["specificity", "evidence", "structure", "reflection"],
    "resume_bullet": ["action_verb", "evidence", "clarity", "role_alignment"],
    "interview_answer": ["structure_star", "specificity", "evidence", "reflection"],
}


def _score_action_verb(words: list[str]) -> tuple[int, str]:
    if words and words[0] in ACTION_VERBS:
        return 3, "Starts with a strong action verb."
    if any(word in ACTION_VERBS for word in words[:5]):
        return 2, "Contains an action verb but not at the start."
    return 1, "Action verb is weak or missing."


def _score_evidence(text: str) -> tuple[int, str]:
    if re.search(r"\b\d+(?:\.\d+)?%?\b", text):
        return 3, "Includes measurable evidence."
    if any(token in text for token in ["users", "customers", "team", "project"]):
        return 2, "Has context but lacks numeric impact."
    return 1, "No concrete evidence found."


def _score_specificity(word_count: int) -> tuple[int, str]:
    if word_count >= 35:
        return 3, "Specific detail level is strong."
    if word_count >= 18:
        return 2, "Moderate detail, could be more concrete."
    return 1, "Too short for clear evaluation."


def _score_structure(text: str) -> tuple[int, str]:
    if all(marker in text for marker in ["situation", "task", "action", "result"]):
        return 3, "STAR structure is explicit."
    if any(marker in text for marker in ["first", "then", "finally"]):
        return 2, "Has sequence but structure is partial."
    return 1, "Structure is not explicit."


def _score_reflection(text: str) -> tuple[int, str]:
    if any(token in text for token in ["learned", "improved", "next time"]):
        return 3, "Shows reflection and iteration mindset."
    if any(token in text for token in ["challenge", "difficult", "fixed"]):
        return 2, "Mentions challenge but limited reflection."
    return 1, "Reflection is missing."


def _score_clarity(word_count: int) -> tuple[int, str]:
    if 12 <= word_count <= 45:
        return 3, "Length and clarity are suitable."
    if 8 <= word_count <= 60:
        return 2, "Mostly clear but can be tighter."
    return 1, "Needs clearer and more concise writing."


def _score_role_alignment(text: str, target_role: str) -> tuple[int, str]:
    role_hint = target_role.replace("_", " ")
    if role_hint in text:
        return 3, "Submission is explicitly aligned to target role."
    if any(token in text for token in target_role.split("_")):
        return 2, "Submission is partially aligned to target role."
    return 1, "Role alignment is not explicit."


def _score_structure_star(text: str) -> tuple[int, str]:
    return _score_structure(text)


def evaluate_task_submission(target_role: str, task_type: str, submission_text: str) -> EvaluateTaskResponse:
    normalized = submission_text.strip().lower()
    words = [word for word in re.findall(r"[a-zA-Z0-9]+", normalized)]
    word_count = len(words)

    rubric = TASK_RUBRICS.get(task_type, ["specificity", "evidence", "structure", "clarity"])

    criteria: list[CriterionScore] = []
    for criterion in rubric:
        if criterion == "action_verb":
            score, reason = _score_action_verb(words)
        elif criterion == "evidence":
            score, reason = _score_evidence(normalized)
        elif criterion == "specificity":
            score, reason = _score_specificity(word_count)
        elif criterion == "structure":
            score, reason = _score_structure(normalized)
        elif criterion == "reflection":
            score, reason = _score_reflection(normalized)
        elif criterion == "clarity":
            score, reason = _score_clarity(word_count)
        elif criterion == "role_alignment":
            score, reason = _score_role_alignment(normalized, target_role)
        elif criterion == "structure_star":
            score, reason = _score_structure_star(normalized)
        else:
            score, reason = 1, "Criterion scorer not found; assigned conservative score."

        criteria.append(CriterionScore(criterion=criterion, score=score, max_score=3, reason=reason))

    overall_score = sum(item.score for item in criteria)
    max_score = sum(item.max_score for item in criteria)
    ratio = overall_score / max_score if max_score else 0

    if ratio >= 0.8:
        status = "good"
    elif ratio >= 0.6:
        status = "revise_minor"
    else:
        status = "revise_major"

    low_criteria = [item.criterion for item in criteria if item.score <= 1]
    feedback = []
    if not low_criteria:
        feedback.append("Strong submission. Keep the same level of specificity and evidence.")
    else:
        for criterion in low_criteria:
            feedback.append(f"Improve {criterion}: add one concrete example and measurable detail.")

    confidence = 0.8 if task_type in TASK_RUBRICS else 0.55
    fallback_triggered = False
    if word_count < 8:
        confidence = 0.35
        fallback_triggered = True
        feedback.append("Submission is too short for reliable scoring; add more detail.")

    return EvaluateTaskResponse(
        overall_score=overall_score,
        max_score=max_score,
        status=status,
        criterion_scores=criteria,
        feedback=feedback,
        next_attempt_focus=low_criteria[:2],
        confidence=round(confidence, 2),
        fallback_triggered=fallback_triggered,
    )
