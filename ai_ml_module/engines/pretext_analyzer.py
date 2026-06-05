"""Engine 1 — Pretext Analyzer (baseline rule-based).

Function: analyze_pretext(user_input_text: str) -> dict
Follows the contract described in project spec.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LABEL_PATH = DATA_DIR / "label_taxonomy.json"
BLOCKER_CSV = DATA_DIR / "keyword_blocker_mapping.csv"
PRETEXT_MASTER = DATA_DIR / "pretext_master.csv"


def _load_blockers() -> Dict[str, List[str]]:
	out = {}
	if not BLOCKER_CSV.exists():
		return out
	import csv

	with open(BLOCKER_CSV, newline="", encoding="utf-8") as fh:
		rd = csv.DictReader(fh)
		for r in rd:
			k = (r.get("keyword") or "").strip().lower()
			t = (r.get("blocker_type") or "").strip()
			if not k:
				continue
			out.setdefault(t, []).append(k)
	return out


def _clean(text: str) -> str:
	if not text:
		return ""
	return " ".join([t.strip().lower() for t in text.split() if t.strip()])


def analyze_pretext(user_input_text: str) -> Dict[str, object]:
	txt = _clean(user_input_text)

	# load label taxonomy (best-effort)
	try:
		if LABEL_PATH.exists():
			with open(LABEL_PATH, encoding="utf-8") as fh:
				labels = json.load(fh)
		else:
			labels = {}
	except Exception:
		labels = {}

	blockers = _load_blockers()

	# defaults
	domain_interest = "general"
	target_role = "general_learner"
	problem_category = "general_problem"
	blocker_type = "none"
	current_level = "beginner"
	intent = "skill_gap"

	matches = 0

	# domain & role detection
	if any(k in txt for k in ("ai ml", "ai/ml", "machine learning", "ml", "deep learning", "model", "classifier", "llm")):
		domain_interest = "ai_ml"
		target_role = "machine_learning_engineer"
		matches += 1
	elif any(k in txt for k in ("cyber", "cybersecurity", "security", "soc", "linux", "networking", "nmap")):
		domain_interest = "cyber_security"
		target_role = "soc_analyst"
		matches += 1
	elif any(k in txt for k in ("figma", "design", "wireframe", "prototype", "ux", "ui")):
		domain_interest = "ui_ux"
		target_role = "ui_ux_designer"
		matches += 1
	elif any(k in txt for k in ("html", "css", "javascript", "frontend", "js")):
		domain_interest = "frontend"
		target_role = "frontend_developer"
		matches += 1
	elif any(k in txt for k in ("python", "django", "flask", "backend")):
		domain_interest = "backend"
		target_role = "backend_developer"
		matches += 1
	elif any(k in txt for k in ("data", "analysis", "analytics", "pandas", "sql", "spreadsheet")):
		domain_interest = "data"
		target_role = "data_analyst"
		matches += 1

	# blocker detection via mapping
	detected_blockers = []
	for btype, kwlist in blockers.items():
		for kw in kwlist:
			if kw in txt:
				detected_blockers.append(btype)
				matches += 1
				break
	if detected_blockers:
		blocker_type = detected_blockers[0]
	else:
		blocker_type = "none"

	# problem_category from blocker_type
	if blocker_type != "none":
		problem_category = f"{blocker_type}_issue"
	else:
		problem_category = f"{domain_interest}_task"

	# current_level detection
	if any(p in txt for p in ("baru mulai", "belum pernah", "pemula", "newbie")):
		current_level = "beginner"
		matches += 1
	elif any(p in txt for p in ("sudah bisa", "pernah belajar", "basic")):
		current_level = "basic"
		matches += 1
	elif any(p in txt for p in ("sudah pernah project", "intermediate")):
		current_level = "intermediate"
		matches += 1

	# intent detection
	if any(p in txt for p in ("belajar", "mulai", "learn", "start")):
		intent = "learn_new"
		matches += 1
	elif any(p in txt for p in ("project", "portfolio", "portofolio")):
		intent = "build_portfolio"
		matches += 1
	elif any(p in txt for p in ("pindah karier", "pindah karir", "career change")):
		intent = "switch_career"
		matches += 1
	elif any(p in txt for p in ("takut salah", "takut salah jalan", "takut")):
		intent = "validate_direction"
		matches += 1

	# persona type rules
	persona_type = "learner"
	if current_level == "beginner" and blocker_type == "no_starting_point":
		persona_type = "beginner_explorer"
	elif blocker_type == "no_portfolio":
		persona_type = "project_seeker"
	elif blocker_type == "fear_wrong_path":
		persona_type = "validation_seeker"
	elif blocker_type == "too_many_options":
		persona_type = "overwhelmed_learner"

	# compute confidence: matches / heuristics (cap 1.0)
	confidence_score = min(1.0, matches / 5.0)

	needs_assessment = True
	if confidence_score >= 0.9 and current_level == "beginner":
		needs_assessment = False

	return {
		"intent": intent,
		"domain_interest": domain_interest,
		"target_role": target_role,
		"problem_category": problem_category,
		"current_level": current_level,
		"blocker_type": blocker_type,
		"persona_type": persona_type,
		"confidence_score": round(confidence_score, 2),
		"needs_assessment": needs_assessment,
	}


__all__ = ["analyze_pretext"]
