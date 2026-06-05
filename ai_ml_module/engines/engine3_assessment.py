"""Engine 3 — Assessment Scoring (tuned rubric-based)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

# ---------------------------------------------------------------------------
# Scoring config (konsisten dengan Engine 7)
# ---------------------------------------------------------------------------
THRESHOLD_PASSED   = 80.0
THRESHOLD_REVISION = 60.0

# Bobot per tipe keyword match
WEIGHT_EXACT   = 1.0   # keyword muncul persis
WEIGHT_PARTIAL = 0.5   # stem/substring dari keyword muncul

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ANSWER_MAP = DATA_DIR / "answer_skill_mapping.csv"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_answer_map() -> pd.DataFrame:
    if ANSWER_MAP.exists():
        return pd.read_csv(ANSWER_MAP)
    return pd.DataFrame()


def _normalize_answer(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())

def _parse_keywords(expected_keywords: str) -> List[str]:
    """Parse keyword pipe-separated → list bersih."""
    return [k.strip().lower() for k in (expected_keywords or "").split("|") if k.strip()]


def _match_keyword(keyword: str, text: str) -> float:
    """Score satu keyword terhadap teks jawaban.

    Returns:
        1.0 jika exact match
        0.5 jika stem (3+ char prefix) ditemukan
        0.0 jika tidak ada
    """
    t = text.lower()
    if keyword in t:
        return WEIGHT_EXACT
    # partial: cek apakah stem (min 4 char) ada di teks
    if len(keyword) >= 4 and keyword[:4] in t:
        return WEIGHT_PARTIAL
    return 0.0


def _keyword_scores(keywords: List[str], text: str) -> List[Dict[str, Any]]:
    """Return list detail per keyword."""
    results = []
    for kw in keywords:
        match_score = _match_keyword(kw, text)
        results.append({
            "keyword": kw,
            "matched": match_score > 0,
            "match_score": match_score,
        })
    return results


def _score_single_choice(question: Dict[str, Any], answer_text: str) -> Dict[str, Any] | None:
    """Score capstone single-choice answers using answer_skill_mapping.csv."""
    if str(question.get("answer_type") or "").strip().lower() != "single_choice":
        return None

    qid = str(question.get("question_id") or "")
    answer_value = _normalize_answer(answer_text)
    if not qid or not answer_value:
        return None

    answer_map = _load_answer_map()
    if answer_map.empty or "answer_value" not in answer_map.columns:
        return _score_generic_single_choice(question, answer_text)

    rows = answer_map[
        (answer_map["question_id"].astype(str) == qid)
        & (answer_map["answer_value"].map(_normalize_answer) == answer_value)
    ]
    if rows.empty:
        return _score_generic_single_choice(question, answer_text)

    row = rows.iloc[0]
    skill_score = float(row.get("skill_score") or 0)
    max_skill_score = 2.0
    final_score = round(max(0.0, min(skill_score, max_skill_score)) / max_skill_score * 100.0, 1)

    if final_score >= THRESHOLD_PASSED:
        status = "passed"
    elif final_score >= THRESHOLD_REVISION:
        status = "needs_revision"
    else:
        status = "failed"

    return {
        "question_id":     question.get("question_id"),
        "skill_id":        str(row.get("skill_id") or question.get("skill_id") or ""),
        "score":           final_score,
        "status":          status,
        "found_keywords":  1 if skill_score > 0 else 0,
        "total_keywords":  1,
        "keyword_details": [],
        "scoring_method":  "answer_skill_mapping",
        "answer_value":    str(row.get("answer_value") or answer_text),
        "skill_score":     int(skill_score) if skill_score.is_integer() else skill_score,
        "max_skill_score": int(max_skill_score),
    }


def _score_generic_single_choice(question: Dict[str, Any], answer_text: str) -> Dict[str, Any] | None:
    """Score runtime single-choice questions that are generated from KB rows."""
    answer_value = _normalize_answer(answer_text)
    level_map = {"belum_paham": 0, "paham_dasar": 1, "cukup_paham": 2}
    if answer_value not in level_map:
        # Clarification questions are not skill-evaluation questions.
        if str(question.get("question_id") or "").startswith("Q_CLARIFY_"):
            return {
                "question_id":     question.get("question_id"),
                "skill_id":        question.get("skill_id") or "career_direction_clarity",
                "score":           0.0,
                "status":          "clarification",
                "found_keywords":  0,
                "total_keywords":  0,
                "keyword_details": [],
                "scoring_method":  "clarification",
                "answer_value":    answer_text,
                "skill_score":     0,
                "max_skill_score": 2,
            }
        return {
            "question_id":     question.get("question_id"),
            "skill_id":        question.get("skill_id") or "",
            "score":           0.0,
            "status":          "invalid_answer",
            "found_keywords":  0,
            "total_keywords":  0,
            "keyword_details": [],
            "scoring_method":  "generic_single_choice",
            "answer_value":    answer_text,
            "skill_score":     0,
            "max_skill_score": 2,
        }

    skill_score = level_map[answer_value]
    final_score = round(skill_score / 2.0 * 100.0, 1)
    if final_score >= THRESHOLD_PASSED:
        status = "passed"
    elif final_score >= THRESHOLD_REVISION:
        status = "needs_revision"
    else:
        status = "failed"

    return {
        "question_id":     question.get("question_id"),
        "skill_id":        question.get("skill_id") or "",
        "score":           final_score,
        "status":          status,
        "found_keywords":  1 if skill_score > 0 else 0,
        "total_keywords":  1,
        "keyword_details": [],
        "scoring_method":  "generic_single_choice",
        "answer_value":    answer_value,
        "skill_score":     skill_score,
        "max_skill_score": 2,
    }


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def score_answer(question: Dict[str, Any], answer_text: str) -> Dict[str, Any]:
    """Score satu jawaban terhadap satu soal.

    Formula (mirip Engine 7 rubric weighted scoring):
        raw_score = sum(match_score per keyword) / len(keywords)
        final_score = raw_score * 100

    Returns dict dengan:
        question_id, skill_id, score (0-100), status,
        found_keywords, total_keywords, keyword_details
    """
    mapped_score = _score_single_choice(question, answer_text)
    if mapped_score is not None:
        return mapped_score

    answer = (answer_text or "").lower()
    keywords = _parse_keywords(question.get("expected_keywords") or "")

    if not keywords:
        # tidak ada keyword → tidak bisa dinilai, beri score 0
        return {
            "question_id":     question.get("question_id"),
            "skill_id":        question.get("skill_id") or "",
            "score":           0.0,
            "status":          "no_rubric",
            "found_keywords":  0,
            "total_keywords":  0,
            "keyword_details": [],
            "scoring_method":  "keyword",
        }

    keyword_details = _keyword_scores(keywords, answer)
    raw_score = sum(d["match_score"] for d in keyword_details) / len(keywords)
    final_score = round(raw_score * 100.0, 1)

    found_keywords = sum(1 for d in keyword_details if d["matched"])

    if final_score >= THRESHOLD_PASSED:
        status = "passed"
    elif final_score >= THRESHOLD_REVISION:
        status = "needs_revision"
    else:
        status = "failed"

    return {
        "question_id":     question.get("question_id"),
        "skill_id":        question.get("skill_id") or "",
        "score":           final_score,
        "status":          status,
        "found_keywords":  found_keywords,
        "total_keywords":  len(keywords),
        "keyword_details": keyword_details,
        "scoring_method":  "keyword",
    }


def score_all_answers(
    questions: List[Dict[str, Any]],
    answers: List[str],
) -> Dict[str, Any]:
    """Score semua jawaban sekaligus (batch helper).

    Args:
        questions: list hasil Engine 2 (setiap item punya question_id, skill_id, expected_keywords)
        answers:   list jawaban user, index-aligned dengan questions

    Returns:
        {
          "results": [score_answer hasil per soal],
          "aggregate": {
              "average_score": float,
              "pass_count": int,
              "revision_count": int,
              "fail_count": int,
              "assessment_validation_score": float  ← untuk Engine 4 / context_validator
          }
        }
    """
    results = []
    for i, q in enumerate(questions):
        ans = answers[i] if i < len(answers) else ""
        results.append(score_answer(q, ans))

    scores = [r["score"] for r in results]
    avg    = round(sum(scores) / len(scores), 1) if scores else 0.0

    pass_count     = sum(1 for r in results if r["status"] == "passed")
    revision_count = sum(1 for r in results if r["status"] == "needs_revision")
    fail_count     = sum(1 for r in results if r["status"] == "failed")

    # assessment_validation_score: normalized 0..1 (dikonsumsi Engine 4)
    validation_score = round(avg / 100.0, 2)

    return {
        "results": results,
        "aggregate": {
            "average_score":             avg,
            "pass_count":                pass_count,
            "revision_count":            revision_count,
            "fail_count":                fail_count,
            "assessment_validation_score": validation_score,
        },
    }


__all__ = ["score_answer", "score_all_answers"]
