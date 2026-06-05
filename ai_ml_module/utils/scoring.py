"""Scoring and gap analysis helpers for Skill Gap Engine."""
from __future__ import annotations

from typing import Dict, List, Tuple


def compute_skill_gaps(target_role: str, user_skill_profile: Dict[str, float], role_skills: Dict[str, List[str]]) -> List[Tuple[str, float]]:
    """Return list of (skill_id, gap_score) where higher gap_score means larger gap.

    Gap = expected_level(assumed 1.0) - user_level (if missing treated as 0).
    This is a simple heuristic; Engine 5 can replace with more sophisticated logic later.
    """
    expected_skills = role_skills.get(target_role, [])
    gaps: List[Tuple[str, float]] = []
    for s in expected_skills:
        user_level = 0.0
        # user_skill_profile keys may not match exactly; attempt direct match
        if s in user_skill_profile:
            user_level = float(user_skill_profile[s])
        else:
            # try substring match
            for k, v in user_skill_profile.items():
                if s.lower() in k.lower() or k.lower() in str(s).lower():
                    user_level = float(v)
                    break
        gap = max(0.0, 1.0 - user_level)
        gaps.append((s, gap))
    # sort by gap desc
    gaps.sort(key=lambda x: -x[1])
    return gaps


def top_n_gaps(gaps: List[Tuple[str, float]], n: int = 5) -> List[Tuple[str, float]]:
    return gaps[:n]
