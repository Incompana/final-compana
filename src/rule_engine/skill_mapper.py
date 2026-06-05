from __future__ import annotations

from src.knowledge_base import get_role
from src.schemas import MapGapSkillsResponse, MissingSkill, SkillPriority

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

ALIASES = {
    "react": "javascript react",
    "javascript": "javascript react",
    "js": "javascript react",
    "html": "html css",
    "css": "html css",
    "api": "api integration",
    "sql": "sql querying",
    "ux": "user research",
}


def _normalize_skill(value: str) -> str:
    normalized = value.strip().lower().replace("_", " ").replace("-", " ")
    if normalized in ALIASES:
        return ALIASES[normalized]
    return normalized


def _is_skill_covered(required_skill: str, current_skills: set[str]) -> bool:
    if required_skill in current_skills:
        return True
    required_tokens = set(required_skill.split())
    for current in current_skills:
        overlap = required_tokens.intersection(current.split())
        if len(overlap) >= 2 or required_skill in current or current in required_skill:
            return True
    return False


def map_gap_skills(target_role: str, current_skills: list[str]) -> MapGapSkillsResponse:
    role_payload = get_role(target_role)
    normalized_current = sorted({_normalize_skill(skill) for skill in current_skills if skill.strip()})

    if role_payload is None:
        return MapGapSkillsResponse(
            target_role=target_role,
            current_skills_normalized=normalized_current,
            missing_skills=[],
            confidence=0.2,
            fallback_triggered=True,
            rationale=["Target role not found in knowledge base."],
        )

    missing: list[MissingSkill] = []
    for required in role_payload.get("required_skills", []):
        skill_name = _normalize_skill(required["skill"])
        if _is_skill_covered(skill_name, set(normalized_current)):
            continue

        priority_value = required.get("priority", "low")
        priority = SkillPriority(priority_value) if priority_value in SkillPriority._value2member_map_ else SkillPriority.LOW
        missing.append(
            MissingSkill(
                skill=required["skill"],
                priority=priority,
                why_missing=(
                    f"{required['skill']} is required for {target_role} but not observed in current skills evidence."
                ),
                example_task=required.get("example_task", "Build one focused task that demonstrates this skill."),
            )
        )

    missing.sort(key=lambda item: PRIORITY_ORDER.get(item.priority.value, 99))
    total_required = max(len(role_payload.get("required_skills", [])), 1)
    covered = total_required - len(missing)
    confidence = round(max(0.3, min(0.95, covered / total_required)), 2)

    rationale = [
        f"Role requirements loaded from knowledge base for {target_role}.",
        f"Compared {len(normalized_current)} provided skills against {total_required} required skills.",
    ]
    return MapGapSkillsResponse(
        target_role=target_role,
        current_skills_normalized=normalized_current,
        missing_skills=missing,
        confidence=confidence,
        fallback_triggered=False,
        rationale=rationale,
    )
