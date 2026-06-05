"""Engine 2 — Question Selector (tuned scoring-based)."""
from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import pandas as pd

DATA_DIR   = Path(__file__).resolve().parents[1] / "data"
QUESTION_BANK = DATA_DIR / "question_bank.csv"
ROLE_SKILL    = DATA_DIR / "role_skill_mapping.csv"

# ---------------------------------------------------------------------------
# Scoring weights (konsisten dengan Engine 5 & 6)
# ---------------------------------------------------------------------------
WEIGHT_DOMAIN   = 0.35
WEIGHT_ROLE     = 0.25
WEIGHT_LEVEL    = 0.20
WEIGHT_BLOCKER  = 0.10
WEIGHT_PRIORITY = 0.10

LEVEL_RANK = {"beginner": 0, "basic": 1, "intermediate": 2, "advanced": 3}
PRIORITY_MAP = {"beginner": 0.6, "basic": 0.8, "intermediate": 0.9, "advanced": 1.0}
PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

ROLE_LABELS = {
    "frontend_developer": "Frontend Developer",
    "backend_developer": "Backend Developer",
    "data_analyst": "Data Analyst",
    "ui_ux_designer": "UI/UX Designer",
    "soc_analyst": "Cybersecurity",
    "machine_learning_engineer": "Machine Learning Engineer",
    "general_learner": "belum yakin",
}

ROLE_DOMAIN = {
    "frontend_developer": "frontend",
    "backend_developer": "backend",
    "data_analyst": "data",
    "ui_ux_designer": "ui_ux",
    "soc_analyst": "cyber_security",
    "machine_learning_engineer": "ai_ml",
}

SKILL_LABELS = {
    "html_basic": "HTML dasar",
    "css_basic": "CSS dasar",
    "javascript_basic": "JavaScript dasar",
    "sql_basic": "SQL dasar",
    "python_basic": "Python dasar",
    "spreadsheet_basic": "spreadsheet",
    "rest_api": "REST API",
    "mysql": "MySQL",
    "git": "Git",
    "figma": "Figma",
    "wireframing": "wireframing",
    "ui_principles": "prinsip UI/UX",
    "linux_basic": "Linux dasar",
    "networking_fundamental": "networking dasar",
    "log_analysis": "analisis log",
}

# Fallback minimal jika question_bank.csv tidak ada
FALLBACK_QUESTIONS = [
    {"question_id": "Q1", "domain_interest": "frontend", "skill_id": "html_basic",
     "prompt": "Buat halaman HTML sederhana dengan tombol yang mengubah warna latar belakang.",
     "expected_keywords": "button|onclick|style|background", "difficulty": "beginner"},
    {"question_id": "Q2", "domain_interest": "frontend", "skill_id": "javascript_basic",
     "prompt": "Jelaskan bagaimana addEventListener bekerja dan berikan contoh sederhana.",
     "expected_keywords": "addeventlistener|queryselector|click|function", "difficulty": "basic"},
    {"question_id": "Q3", "domain_interest": "backend", "skill_id": "python_basic",
     "prompt": "Tulis fungsi Python yang menerima list dan mengembalikan rata-ratanya.",
     "expected_keywords": "def|return|sum|len|float", "difficulty": "beginner"},
    {"question_id": "Q4", "domain_interest": "data", "skill_id": "pandas_basic",
     "prompt": "Jelaskan perbedaan antara DataFrame dan Series di pandas.",
     "expected_keywords": "dataframe|series|pandas|index|column", "difficulty": "basic"},
]


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _clean_cell(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() == "nan" else text


def _labelize(value: Any) -> str:
    text = _clean_cell(value)
    if not text:
        return ""
    return SKILL_LABELS.get(text, text.replace("_", " ").title())


def _role_label(role_id: str) -> str:
    return ROLE_LABELS.get(role_id, _labelize(role_id))

def _load_question_bank() -> pd.DataFrame:
    if QUESTION_BANK.exists():
        return pd.read_csv(QUESTION_BANK)
    return pd.DataFrame(FALLBACK_QUESTIONS)


def _load_role_skill() -> pd.DataFrame:
    if ROLE_SKILL.exists():
        return pd.read_csv(ROLE_SKILL)
    return pd.DataFrame()


def _single_choice_question(
    question_id: str,
    skill_id: str,
    prompt: str,
    *,
    target_role: str = "",
    domain: str = "",
    current_level: str = "beginner",
    purpose: str = "assessment",
    score: float = 1.0,
) -> Dict[str, Any]:
    return {
        "question_id": question_id,
        "skill_id": skill_id,
        "skill_label": _labelize(skill_id),
        "prompt": prompt,
        "expected_keywords": "belum_paham|paham_dasar|cukup_paham",
        "difficulty": current_level or "beginner",
        "answer_type": "single_choice",
        "options": "belum_paham|paham_dasar|cukup_paham",
        "target_role": target_role,
        "current_level": current_level or "beginner",
        "blocker_type": purpose,
        "domain_interest": domain,
        "question_score": score,
    }


def _clarification_questions(pretext_analysis: Dict[str, Any], max_questions: int) -> List[Dict[str, Any]]:
    meta_scores = (pretext_analysis.get("_meta") or {}).get("scores") or {}
    role_ambiguity = bool(meta_scores.get("role_ambiguity"))
    confusion_signal = bool(meta_scores.get("confusion_signal"))
    confidence = float(pretext_analysis.get("confidence_score") or 0)
    domain = pretext_analysis.get("domain_interest") or "general"

    if domain != "general" and not role_ambiguity:
        if not confusion_signal:
            return []
        return [
            {
                "question_id": "Q_CLARIFY_BLOCKER",
                "skill_id": "career_direction_clarity",
                "prompt": "Kamu sudah menyebut arah yang cukup jelas. Bagian mana yang paling bikin kamu bingung sekarang?",
                "expected_keywords": "belum_tahu_mulai|skill_belum_cukup|belum_ada_portfolio|takut_salah_pilih",
                "difficulty": "beginner",
                "answer_type": "single_choice",
                "options": "belum_tahu_mulai|skill_belum_cukup|belum_ada_portfolio|takut_salah_pilih",
                "target_role": pretext_analysis.get("target_role") or "",
                "current_level": pretext_analysis.get("current_level") or "beginner",
                "blocker_type": "clarify_blocker",
                "domain_interest": domain,
                "question_score": 1.0,
            }
        ][:max_questions]

    if domain != "general" and not role_ambiguity and confidence >= 0.45:
        return []

    first_prompt = (
        "Dari ceritamu, arah mana yang paling ingin kamu cek dulu?"
        if role_ambiguity
        else "Aku belum bisa menangkap target role-mu dengan jelas. Kamu ingin diarahkan ke jalur apa dulu?"
    )
    questions = [
        {
            "question_id": "Q_CLARIFY_ROLE",
            "skill_id": "career_direction_clarity",
            "prompt": first_prompt,
            "expected_keywords": "frontend_developer|backend_developer|data_analyst|ui_ux_designer|soc_analyst|masih_bingung",
            "difficulty": "beginner",
            "answer_type": "single_choice",
            "options": "frontend_developer|backend_developer|data_analyst|ui_ux_designer|soc_analyst|masih_bingung",
            "target_role": "general_learner",
            "current_level": "beginner",
            "blocker_type": "clarify_role",
            "domain_interest": "general",
            "question_score": 1.0,
        },
        {
            "question_id": "Q_CLARIFY_BLOCKER",
            "skill_id": "career_direction_clarity",
            "prompt": "Bagian mana yang paling bikin kamu bingung sekarang?",
            "expected_keywords": "belum_tahu_role|belum_tahu_mulai|skill_belum_cukup|belum_ada_portfolio|takut_salah_pilih",
            "difficulty": "beginner",
            "answer_type": "single_choice",
            "options": "belum_tahu_role|belum_tahu_mulai|skill_belum_cukup|belum_ada_portfolio|takut_salah_pilih",
            "target_role": "general_learner",
            "current_level": "beginner",
            "blocker_type": "clarify_blocker",
            "domain_interest": "general",
            "question_score": 0.98,
        },
    ]
    return questions[:max_questions]


def _role_skill_questions(
    role_df: pd.DataFrame,
    target_role: str,
    user_level: str,
    max_questions: int,
) -> List[Dict[str, Any]]:
    if role_df.empty or not target_role or target_role == "general_learner":
        return []

    rows = role_df[role_df["role_id"] == target_role].copy()
    if rows.empty:
        return []
    rows["_priority_weight"] = rows["priority"].astype(str).str.lower().map(PRIORITY_WEIGHT).fillna(1)
    rows["_step_order"] = pd.to_numeric(rows.get("step_order"), errors="coerce").fillna(9999)
    rows = rows.sort_values(["_step_order", "_priority_weight"], ascending=[True, False]).head(max_questions)

    role_label = _role_label(target_role)
    domain = ROLE_DOMAIN.get(target_role, "")
    questions: List[Dict[str, Any]] = []
    for _, row in rows.iterrows():
        skill_id = _clean_cell(row.get("required_skill_id"))
        skill_name = _clean_cell(row.get("required_skill_name")) or _labelize(skill_id)
        prompt = (
            f"Untuk jalur {role_label}, seberapa paham kamu tentang {skill_name}? "
            "Pilih yang paling sesuai dengan kondisimu sekarang."
        )
        questions.append(_single_choice_question(
            f"Q_RUNTIME_{target_role}_{skill_id}",
            skill_id,
            prompt,
            target_role=target_role,
            domain=domain,
            current_level=user_level,
            purpose="skill_check",
            score=0.95,
        ))
    return questions


def _rewrite_generated_prompt(question: Dict[str, Any]) -> Dict[str, Any]:
    prompt = question.get("prompt") or ""
    if "Pertanyaan untuk" not in prompt:
        return question
    role = _role_label(question.get("target_role") or "")
    skill = _labelize(question.get("skill_id"))
    if not role or role == "Belum Yakin":
        role = "jalur ini"
    question = dict(question)
    question["prompt"] = (
        f"Untuk {role}, seberapa paham kamu tentang {skill}? "
        "Pilih level yang paling menggambarkan kemampuanmu saat ini."
    )
    return question


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _level_match_score(q_difficulty: str, user_level: str) -> float:
    """Exact level = 1.0, satu step di atas = 0.5, lainnya = 0.0 (sama kayak Engine 6)."""
    ql = LEVEL_RANK.get(str(q_difficulty).lower(), 1)
    ul = LEVEL_RANK.get(str(user_level).lower(), 1)
    if ql == ul:
        return 1.0
    if ql == ul + 1:
        return 0.5
    return 0.0


def _blocker_match_score(blocker: str, row: pd.Series) -> float:
    """1.0 jika blocker keyword muncul di prompt atau expected_keywords."""
    if not blocker or blocker == "none":
        return 0.0
    combined = (str(row.get("expected_keywords") or "") + " " + str(row.get("prompt") or "")).lower()
    return 1.0 if blocker.lower() in combined else 0.0


def _compute_question_score(
    row: pd.Series,
    domain: str,
    target_role: str,
    user_level: str,
    blocker: str,
    role_skills: set,
) -> float:
    q_domain = str(row.get("domain_interest") or "")
    q_skill  = str(row.get("skill_id") or "")
    q_diff   = str(row.get("difficulty") or "basic")

    domain_match   = 1.0 if q_domain == domain else 0.0
    role_match     = 1.0 if q_skill in role_skills else 0.0
    level_match    = _level_match_score(q_diff, user_level)
    blocker_match  = _blocker_match_score(blocker, row)
    priority_weight = PRIORITY_MAP.get(q_diff.lower(), 0.8)

    return round(
        domain_match   * WEIGHT_DOMAIN   +
        role_match     * WEIGHT_ROLE     +
        level_match    * WEIGHT_LEVEL    +
        blocker_match  * WEIGHT_BLOCKER  +
        priority_weight* WEIGHT_PRIORITY,
        3,
    )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def select_questions(pretext_analysis: Dict[str, Any], max_questions: int = 3) -> Dict[str, Any]:
    """Pilih soal assessment berdasarkan hasil analisis pretext.

    Scoring per soal:
        score = domain_match   * 0.35
              + role_match     * 0.25
              + level_match    * 0.20
              + blocker_match  * 0.10
              + priority_weight* 0.10
    """
    df       = _load_question_bank()
    role_df  = _load_role_skill()

    domain      = pretext_analysis.get("domain_interest") or "general"
    target_role = pretext_analysis.get("target_role") or ""
    user_level  = pretext_analysis.get("current_level") or "beginner"
    blocker     = pretext_analysis.get("blocker_type") or "none"
    if target_role in ROLE_DOMAIN:
        domain = ROLE_DOMAIN[target_role]

    clarification = _clarification_questions(pretext_analysis, max_questions)
    if clarification:
        remaining = max(0, max_questions - len(clarification))
        role_questions = []
        if target_role and target_role != "general_learner":
            role_questions = _role_skill_questions(role_df, target_role, user_level, remaining)
        return {"questions": clarification + role_questions[:remaining]}

    role_questions = _role_skill_questions(role_df, target_role, user_level, max_questions)
    if role_questions:
        return {"questions": role_questions[:max_questions]}

    # Kumpulkan required skills untuk role ini (pola sama Engine 5)
    role_skills: set = set()
    if not role_df.empty and target_role:
        role_skills = set(
            role_df[role_df["role_id"] == target_role]["required_skill_id"].astype(str).tolist()
        )

    candidates = []
    for _, row in df.iterrows():
        score = _compute_question_score(row, domain, target_role, user_level, blocker, role_skills)
        candidates.append(_rewrite_generated_prompt({
            "question_id":       _clean_cell(row.get("question_id")),
            "skill_id":          _clean_cell(row.get("skill_id")),
            "skill_label":        _labelize(row.get("skill_id")),
            "prompt":            _clean_cell(row.get("prompt")),
            "expected_keywords": _clean_cell(row.get("expected_keywords")),
            "difficulty":        _clean_cell(row.get("difficulty")) or "basic",
            "answer_type":       _clean_cell(row.get("answer_type")),
            "options":           _clean_cell(row.get("options")),
            "target_role":       _clean_cell(row.get("target_role")),
            "current_level":     _clean_cell(row.get("current_level")),
            "blocker_type":      _clean_cell(row.get("blocker_type")),
            "question_score":    score,
        }))

    # Sort descending by score, ambil top max_questions
    candidates.sort(key=lambda x: -x["question_score"])
    selected = candidates[:max_questions]

    return {"questions": selected}


# Alias untuk backward-compatibility dengan assessment_selector.py lama
def generate_assessment(pretext_analysis: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
    return select_questions(pretext_analysis, max_questions=top_k)


__all__ = ["select_questions", "generate_assessment"]
