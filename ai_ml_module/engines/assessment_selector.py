"""Engine 2 — Assessment Selector (baseline).

Function: generate_assessment(pretext_analysis: dict, top_k: int = 3) -> dict
"""
from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
QUESTION_BANK = DATA_DIR / "question_bank.csv"
ROLE_SKILL = DATA_DIR / "role_skill_mapping.csv"


def _load_question_bank() -> pd.DataFrame:
	if QUESTION_BANK.exists():
		return pd.read_csv(QUESTION_BANK)
	return pd.DataFrame()


def _load_role_skill() -> pd.DataFrame:
	if ROLE_SKILL.exists():
		return pd.read_csv(ROLE_SKILL)
	return pd.DataFrame()


def _level_rank(lv: str) -> int:
	return {"beginner": 0, "basic": 1, "intermediate": 2, "advanced": 3}.get(str(lv).lower(), 1)


def _clean_cell(value: Any) -> str:
	text = str(value or "").strip()
	return "" if text.lower() == "nan" else text


def generate_assessment(pretext_analysis: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
	df = _load_question_bank()
	if df.empty:
		return {"questions": []}

	role_df = _load_role_skill()

	domain = pretext_analysis.get("domain_interest")
	target_role = pretext_analysis.get("target_role")
	level = pretext_analysis.get("current_level")
	blocker = pretext_analysis.get("blocker_type")

	candidates = []
	for _, r in df.iterrows():
		q_domain = str(r.get("domain_interest") or "")
		q_skill = str(r.get("skill_id") or "")
		q_diff = str(r.get("difficulty") or "basic")

		domain_match = 1.0 if q_domain == domain else 0.0

		# role match: check if q_skill belongs to target_role in role_skill mapping
		role_match = 0.0
		if not role_df.empty and target_role:
			skills_for_role = set(role_df[role_df["role_id"] == target_role]["required_skill_id"].astype(str).tolist())
			if q_skill in skills_for_role:
				role_match = 1.0

		# level match
		level_match = 0.0
		qlvl = _level_rank(q_diff)
		ulvl = _level_rank(level)
		if qlvl == ulvl:
			level_match = 1.0
		elif qlvl == ulvl + 1:
			level_match = 0.5

		# blocker match: presence of blocker keyword in expected_keywords or prompt
		blocker_match = 0.0
		expected = str(r.get("expected_keywords") or "") + " " + str(r.get("prompt") or "")
		if blocker and blocker in expected:
			blocker_match = 1.0

		# priority weight (proxy using difficulty): normalize to 0..1
		priority_map = {"beginner": 0.6, "basic": 0.8, "intermediate": 0.9, "advanced": 1.0}
		priority_weight = priority_map.get(q_diff.lower(), 0.8)

		question_score = (
			domain_match * 0.35
			+ role_match * 0.25
			+ level_match * 0.20
			+ blocker_match * 0.10
			+ priority_weight * 0.10
		)

		candidates.append({
			"question_id": _clean_cell(r.get("question_id")),
			"skill_id": q_skill,
			"prompt": _clean_cell(r.get("prompt")),
			"expected_keywords": _clean_cell(r.get("expected_keywords")),
			"difficulty": q_diff,
			"answer_type": _clean_cell(r.get("answer_type")),
			"options": _clean_cell(r.get("options")),
			"target_role": _clean_cell(r.get("target_role")),
			"current_level": _clean_cell(r.get("current_level")),
			"blocker_type": _clean_cell(r.get("blocker_type")),
			"score": round(float(question_score), 3),
		})

	candidates = sorted(candidates, key=lambda x: -x["score"])[:top_k]
	return {"questions": candidates}


__all__ = ["generate_assessment"]
