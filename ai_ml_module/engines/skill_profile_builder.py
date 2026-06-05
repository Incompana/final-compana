"""Engine 3 — Skill Profile Builder (baseline).

Function: build_skill_profile(assessment_answers: list) -> dict
"""
from __future__ import annotations

from typing import List, Dict
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ANSWER_MAP = DATA_DIR / "answer_skill_mapping.csv"


def _load_answer_map() -> pd.DataFrame:
	if ANSWER_MAP.exists():
		return pd.read_csv(ANSWER_MAP)
	return pd.DataFrame()


def build_skill_profile(assessment_answers: List[Dict[str, object]]) -> Dict[str, object]:
	# assessment_answers: list of dicts with keys question_id, score, status, skill_id optional
	df_map = _load_answer_map()
	profile = {}
	levels = []
	scores = []

	for a in assessment_answers:
		skill = a.get("skill_id") or None
		score = float(a.get("score") or 0)
		scores.append(score)
		# map score to level
		if score >= 80:
			lvl = 2
		elif score >= 50:
			lvl = 1
		else:
			lvl = 0
		if not skill and not df_map.empty:
			# try to map via question id
			qid = a.get("question_id")
			row = df_map[df_map["question_id"].astype(str) == str(qid)]
			if not row.empty:
				skill = str(row.iloc[0].get("skill_id"))
		if skill:
			profile[str(skill)] = lvl
			levels.append(lvl)

	avg_level = sum(levels) / len(levels) if levels else 0
	# determine validated_level
	if avg_level >= 1.5:
		validated_level = "intermediate"
	elif avg_level >= 0.75:
		validated_level = "basic"
	else:
		validated_level = "beginner"

	assessment_validation_score = (sum(scores) / (len(scores) * 100.0)) if scores else 0.0

	return {
		"user_skill_profile": profile,
		"validated_level": validated_level,
		"assessment_validation_score": round(assessment_validation_score, 2),
	}


__all__ = ["build_skill_profile"]
