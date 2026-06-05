"""Engine 4 — Skill Profile Builder (tuned weighted aggregation)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

DATA_DIR  = Path(__file__).resolve().parents[1] / "data"
ROLE_SKILL = DATA_DIR / "role_skill_mapping.csv"
ANSWER_MAP = DATA_DIR / "answer_skill_mapping.csv"

# ---------------------------------------------------------------------------
# Scoring config (konsisten dengan Engine 5 PRIORITY_WEIGHT)
# ---------------------------------------------------------------------------
PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

# Threshold konversi score → level (0/1/2)
LEVEL_THRESHOLDS = [
    (80.0, 2),   # ≥ 80 → level 2 (owned / strong)
    (50.0, 1),   # ≥ 50 → level 1 (weak)
    (0.0,  0),   # < 50 → level 0 (missing)
]

LEVEL_LABEL = {2: "intermediate", 1: "basic", 0: "beginner"}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_role_skill() -> pd.DataFrame:
    if ROLE_SKILL.exists():
        return pd.read_csv(ROLE_SKILL)
    return pd.DataFrame()


def _load_answer_map() -> pd.DataFrame:
    if ANSWER_MAP.exists():
        return pd.read_csv(ANSWER_MAP)
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_to_level(score: float) -> int:
    for threshold, level in LEVEL_THRESHOLDS:
        if score >= threshold:
            return level
    return 0


def _get_skill_priority(skill_id: str, role_df: pd.DataFrame, target_role: str) -> str:
    """Cari priority dari role_skill_mapping; default 'low'."""
    if role_df.empty or not target_role:
        return "low"
    rows = role_df[(role_df["role_id"] == target_role) & (role_df["required_skill_id"].astype(str) == skill_id)]
    if rows.empty:
        return "low"
    return str(rows.iloc[0].get("priority") or "low").lower()


def _resolve_skill_id(answer: Dict[str, Any], answer_map_df: pd.DataFrame) -> str:
    """Ambil skill_id dari answer dict; fallback ke answer_skill_mapping CSV."""
    skill = answer.get("skill_id") or None
    if skill:
        return str(skill)
    if not answer_map_df.empty:
        qid = answer.get("question_id")
        row = answer_map_df[answer_map_df["question_id"].astype(str) == str(qid)]
        if not row.empty:
            return str(row.iloc[0].get("skill_id") or "")
    # fallback: gunakan question_id sebagai proxy
    return str(answer.get("question_id") or "unknown")


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def build_skill_profile(
    assessment_results: List[Dict[str, Any]],
    target_role: str = "",
) -> Dict[str, Any]:
    """Bangun skill profile dari hasil assessment.

    Weighted aggregation (mirip Engine 5 readiness_score):
        - Setiap skill punya priority_weight dari role_skill_mapping
        - Jika skill muncul lebih dari sekali (multiple questions), ambil max score
        - assessment_validation_score = sum(score * priority_weight) / sum(priority_weight)

    Returns:
        {
          "user_skill_profile": {skill_id: 0|1|2, ...},
          "validated_level": "beginner"|"basic"|"intermediate"|"advanced",
          "assessment_validation_score": float (0..1),
          "skill_details": [{skill_id, score, level, priority, priority_weight}, ...]
        }
    """
    role_df     = _load_role_skill()
    answer_map  = _load_answer_map()

    # Kumpulkan max score per skill (jika ada duplicate question untuk skill sama)
    skill_scores: Dict[str, float] = {}
    for a in assessment_results:
        sid   = _resolve_skill_id(a, answer_map)
        score = float(a.get("score") or 0.0)
        # ambil max jika skill muncul lebih dari sekali
        skill_scores[sid] = max(skill_scores.get(sid, 0.0), score)

    if not skill_scores:
        return {
            "user_skill_profile":        {},
            "validated_level":           "beginner",
            "assessment_validation_score": 0.0,
            "skill_details":             [],
        }

    # Build weighted profile
    user_skill_profile: Dict[str, int] = {}
    skill_details: List[Dict[str, Any]] = []

    total_weight        = 0.0
    weighted_score_sum  = 0.0

    for sid, score in skill_scores.items():
        level    = _score_to_level(score)
        priority = _get_skill_priority(sid, role_df, target_role)
        weight   = PRIORITY_WEIGHT.get(priority, 1)

        user_skill_profile[sid] = level
        total_weight       += weight
        weighted_score_sum += (score / 100.0) * weight

        skill_details.append({
            "skill_id":       sid,
            "score":          round(score, 1),
            "level":          level,
            "priority":       priority,
            "priority_weight": weight,
        })

    # assessment_validation_score: weighted average 0..1
    assessment_validation_score = round(
        weighted_score_sum / total_weight if total_weight > 0 else 0.0, 2
    )

    # validated_level dari rata-rata level semua skill
    all_levels = list(user_skill_profile.values())
    avg_level  = sum(all_levels) / len(all_levels) if all_levels else 0.0

    if avg_level >= 1.75:
        validated_level = "advanced"
    elif avg_level >= 1.25:
        validated_level = "intermediate"
    elif avg_level >= 0.5:
        validated_level = "basic"
    else:
        validated_level = "beginner"

    return {
        "user_skill_profile":          user_skill_profile,
        "validated_level":             validated_level,
        "assessment_validation_score": assessment_validation_score,
        "skill_details":               skill_details,
    }


__all__ = ["build_skill_profile"]