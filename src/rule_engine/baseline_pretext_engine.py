from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from src.preprocessing.text import normalize_text

ROLE_LABELS = ["cybersecurity", "frontend", "backend", "data_analyst", "uiux", "unclear"]
PROBLEM_LABELS = [
    "beginner_lost",
    "direction_confused",
    "skill_gap",
    "overwhelmed",
    "confidence_issue",
    "unclear",
]

ROLE_PATTERNS: Dict[str, List[str]] = {
    "cybersecurity": [
        r"\bcyber\s?security\b",
        r"\bkeamanan\s?siber\b",
        r"\bsoc\b",
        r"\bsiem\b",
        r"\bpentest\b",
        r"\bsecurity\s?engineer\b",
    ],
    "frontend": [
        r"\bfront\s?end\b",
        r"\breact\b",
        r"\bjavascript\b",
        r"\bhtml\b",
        r"\bcss\b",
        r"\bweb\s?frontend\b",
    ],
    "backend": [
        r"\bback\s?end\b",
        r"\bapi\b",
        r"\bnode\b",
        r"\bexpress\b",
        r"\bserver\b",
        r"\bdatabase\b",
    ],
    "data_analyst": [
        r"\bdata\s?analyst\b",
        r"\banalis\w*\s?data\b",
        r"\bdashboard\b",
        r"\btableau\b",
        r"\bpower\s?bi\b",
        r"\bexcel\b",
        r"\bsql\b",
    ],
    "uiux": [
        r"\bui\s?/\s?ux\b",
        r"\buiux\b",
        r"\bux\b",
        r"\bfigma\b",
        r"\bwireframe\b",
        r"\bprototype\b",
        r"\bproduct\s?design\b",
    ],
}

PROBLEM_PATTERNS: Dict[str, List[str]] = {
    "beginner_lost": [
        r"\bpemula\b",
        r"\bbaru\s?banget\b",
        r"\bbaru\s?mulai\b",
        r"\blevel\s?nol\b",
        r"\bbelum\s?tahu\s?mulai\b",
        r"\bga\s?tau\s?mulai\b",
        r"\bnggak\s?tahu\s?mulai\b",
        r"\bnyasar\b",
        r"\blost\b",
    ],
    "direction_confused": [
        r"\bbingung\s?pilih\b",
        r"\bgalau\b",
        r"\bantara\b",
        r"\bbelum\s?yakin\b",
        r"\bcampur\s?campur\b",
        r"\btoo\s?many\s?options\b",
        r"\bkebanyakan\s?opsi\b",
        r"\bganti\s?topik\b",
    ],
    "skill_gap": [
        r"\bgap\s?skill\b",
        r"\bskill\w*\s?belum\s?cukup\b",
        r"\bskill\w*\s?kurang\b",
        r"\bkurang\s?skill\b",
        r"\bmentok\s?karena\s?skill\b",
        r"\bbelum\s?kuat\b",
        r"\bbelum\s?bisa\b",
    ],
    "overwhelmed": [
        r"\bkewalahan\b",
        r"\boverwhelmed\b",
        r"\boverload\b",
        r"\bnumpuk\b",
        r"\bmumet\b",
        r"\bpusing\b",
        r"\bburnout\b",
        r"\bfreeze\b",
    ],
    "confidence_issue": [
        r"\bnggak\s?pede\b",
        r"\btidak\s?pede\b",
        r"\bkurang\s?percaya\s?diri\b",
        r"\bminder\b",
        r"\btakut\s?gagal\b",
        r"\bcemas\b",
        r"\bpanik\b",
        r"\boverthinking\b",
        r"\bimpostor\b",
    ],
}

AMBIGUITY_PATTERNS = [
    r"\bbingung\b",
    r"\bbelum\s?yakin\b",
    r"\bantara\b",
    r"\bcampur\s?campur\b",
    r"\bga\s?tau\b",
    r"\bnggak\s?tau\b",
    r"\bmasih\s?belum\s?jelas\b",
]


@dataclass
class RankedResult:
    label: str
    score: int
    hits: List[str]


def _collect_hits(text: str, pattern_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {}
    for label, patterns in pattern_map.items():
        hits = [pattern for pattern in patterns if re.search(pattern, text)]
        results[label] = hits
    return results


def _rank(hit_map: Dict[str, List[str]]) -> List[RankedResult]:
    ranked = [RankedResult(label=label, score=len(hits), hits=hits) for label, hits in hit_map.items()]
    ranked.sort(key=lambda row: row.score, reverse=True)
    return ranked


def _top_labels(ranked: List[RankedResult]) -> List[str]:
    if not ranked or ranked[0].score == 0:
        return []
    top_score = ranked[0].score
    return [row.label for row in ranked if row.score == top_score and top_score > 0]


def _apply_role_tiebreakers(text: str, top_roles: List[str]) -> List[str]:
    # Explicit role phrases should win over indirect keyword overlap.
    explicit_map = {
        "frontend": [r"\bmau\s?jadi\s?frontend\b", r"\btarget\w*\s?frontend\b"],
        "backend": [r"\bmau\s?jadi\s?backend\b", r"\btarget\w*\s?backend\b"],
        "data_analyst": [r"\bmau\s?jadi\s?data\s?analyst\b", r"\btarget\w*\s?data\s?analyst\b"],
        "cybersecurity": [r"\bmau\s?masuk\s?cyber\s?security\b", r"\btarget\w*\s?soc\b"],
        "uiux": [r"\bmau\s?jadi\s?ui\s?/\s?ux\b", r"\btarget\w*\s?uiux\b"],
    }
    explicit_hits = [
        role
        for role in top_roles
        if any(re.search(pattern, text) for pattern in explicit_map.get(role, []))
    ]
    if len(explicit_hits) == 1:
        return explicit_hits
    return top_roles


def _build_confidence(
    word_count: int,
    role_top_count: int,
    problem_top_count: int,
    role_score: int,
    problem_score: int,
    has_ambiguity: bool,
    role_unclear: bool,
    problem_unclear: bool,
) -> float:
    role_strength = min(1.0, role_score / 2) if role_score > 0 else 0.0
    problem_strength = min(1.0, problem_score / 2) if problem_score > 0 else 0.0
    length_strength = 1.0 if word_count >= 8 else 0.5 if word_count >= 4 else 0.2

    confidence = 0.1 + (0.4 * role_strength) + (0.35 * problem_strength) + (0.15 * length_strength)

    if role_top_count > 1:
        confidence -= 0.2
    if problem_top_count > 1:
        confidence -= 0.15
    if has_ambiguity:
        confidence -= 0.15
    if role_unclear:
        confidence -= 0.15
    if problem_unclear:
        confidence -= 0.15
    if word_count <= 3:
        confidence -= 0.2

    return round(max(0.05, min(0.95, confidence)), 2)


def inspect_pretext(pretext_text: str) -> dict:
    normalized = normalize_text(pretext_text)
    words = normalized.split()
    word_count = len(words)

    role_hits = _collect_hits(normalized, ROLE_PATTERNS)
    problem_hits = _collect_hits(normalized, PROBLEM_PATTERNS)

    role_ranked = _rank(role_hits)
    problem_ranked = _rank(problem_hits)

    top_roles = _top_labels(role_ranked)
    top_roles = _apply_role_tiebreakers(normalized, top_roles)
    top_problems = _top_labels(problem_ranked)

    target_role = top_roles[0] if len(top_roles) == 1 else "unclear"
    problem_category = top_problems[0] if len(top_problems) == 1 else "unclear"

    ambiguity_hits = [pattern for pattern in AMBIGUITY_PATTERNS if re.search(pattern, normalized)]
    has_ambiguity = len(ambiguity_hits) > 0

    top_role_score = role_ranked[0].score if role_ranked else 0
    top_problem_score = problem_ranked[0].score if problem_ranked else 0

    confidence = _build_confidence(
        word_count=word_count,
        role_top_count=len(top_roles),
        problem_top_count=len(top_problems),
        role_score=top_role_score,
        problem_score=top_problem_score,
        has_ambiguity=has_ambiguity,
        role_unclear=target_role == "unclear",
        problem_unclear=problem_category == "unclear",
    )

    clarification_needed = (
        confidence < 0.6
        or target_role == "unclear"
        or problem_category == "unclear"
        or len(top_roles) > 1
        or len(top_problems) > 1
    )

    reasons: List[str] = []
    if target_role != "unclear":
        reasons.append(f"Role inferred from {top_role_score} matched signal(s).")
    else:
        reasons.append("Role signal is ambiguous or insufficient.")

    if problem_category != "unclear":
        reasons.append(f"Problem category inferred from {top_problem_score} matched signal(s).")
    else:
        reasons.append("Problem category signal is ambiguous or insufficient.")

    if has_ambiguity:
        reasons.append("Ambiguity markers detected in input text.")

    return {
        "input_text": pretext_text,
        "normalized_text": normalized,
        "target_role": target_role,
        "problem_category": problem_category,
        "confidence": confidence,
        "clarification_needed": clarification_needed,
        "reasons": reasons,
        "matched_signals": {
            "roles": {label: hits for label, hits in role_hits.items() if hits},
            "problem_categories": {
                label: hits for label, hits in problem_hits.items() if hits
            },
            "ambiguity": ambiguity_hits,
        },
    }
