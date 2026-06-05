"""Engine 4 — Context Validator (baseline).

Function: validate_context(pretext_analysis: dict, assessment_result: dict) -> dict
"""
from __future__ import annotations

from typing import Dict, Any
from ai_ml_module.utils.loader import load_role_skill_mapping


def validate_context(pretext_analysis: Dict[str, Any], assessment_result: Dict[str, Any]) -> Dict[str, Any]:
    # pretext_confidence
    pre_conf = float(pretext_analysis.get("confidence_score") or 0.0)

    # assessment_validation_score expected in assessment_result
    assess_score = float(assessment_result.get("assessment_validation_score") or 0.0)

    # label consistency: fraction of validated skills that match role required skills
    label_consistency = 0.0
    try:
        df = load_role_skill_mapping()
        target = pretext_analysis.get("target_role")
        if not df.empty and target:
            role_skills = set(df[df["role_id"] == target]["required_skill_id"].astype(str).tolist())
            validated = assessment_result.get("user_skill_profile") or {}
            if validated:
                validated_skills = set(k for k, v in validated.items() if v >= 1)
                if validated_skills:
                    label_consistency = len(validated_skills & role_skills) / max(1, len(validated_skills))
    except Exception:
        label_consistency = 0.0

    final_confidence = pre_conf * 0.55 + assess_score * 0.35 + label_consistency * 0.10

    validated_analysis = {
        "target_role": pretext_analysis.get("target_role"),
        "current_level": pretext_analysis.get("current_level"),
        "problem_category": pretext_analysis.get("problem_category"),
        "blocker_type": pretext_analysis.get("blocker_type"),
        "persona_type": pretext_analysis.get("persona_type"),
        "confidence_score": round(final_confidence, 2),
        "summary": f"Combined pretext confidence {pre_conf:.2f}, assessment {assess_score:.2f}, label_consistency {label_consistency:.2f}",
    }

    return {"validated_analysis": validated_analysis, "user_skill_profile": assessment_result.get("user_skill_profile")}


__all__ = ["validate_context"]
