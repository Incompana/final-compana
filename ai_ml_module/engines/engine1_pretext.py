"""Engine 1 — Pretext Analyzer (ML classifier + rule-based fallback)."""
from __future__ import annotations

import json
import csv
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

DATA_DIR      = Path(__file__).resolve().parents[1] / "data"
LABEL_PATH    = DATA_DIR / "label_taxonomy.json"
BLOCKER_CSV   = DATA_DIR / "keyword_blocker_mapping.csv"

# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------
WEIGHT_DOMAIN   = 0.35
WEIGHT_LEVEL    = 0.25
WEIGHT_BLOCKER  = 0.20
WEIGHT_INTENT   = 0.20

# ---------------------------------------------------------------------------
# Keyword maps (rule-based fallback)
# ---------------------------------------------------------------------------
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "ai_ml":    ["ai ml", "ai/ml", "machine learning", "ml", "deep learning", "model", "classifier", "neural", "llm"],
    "cyber_security": ["cyber", "cybersecurity", "security", "soc", "linux", "networking", "nmap", "incident"],
    "frontend": ["html", "css", "javascript", "js", "frontend", "front end", "front-end", "react", "vue", "tailwind"],
    "backend":  ["python", "django", "flask", "backend", "back end", "back-end", "nodejs", "node js", "express", "api", "rest"],
    "data":     ["data", "analysis", "analytics", "pandas", "numpy", "sql", "tableau", "spreadsheet"],
    "mobile":   ["android", "ios", "flutter", "kotlin", "swift", "mobile", "react native"],
    "devops":   ["docker", "kubernetes", "ci/cd", "devops", "jenkins", "terraform", "cloud"],
    "ui_ux":   ["figma", "design", "wireframe", "prototype", "ux", "ui"],
}

DOMAIN_TO_ROLE: Dict[str, str] = {
    "ai_ml":    "machine_learning_engineer",
    "cyber_security": "soc_analyst",
    "frontend": "frontend_developer",
    "backend":  "backend_developer",
    "data":     "data_analyst",
    "mobile":   "mobile_developer",
    "devops":   "devops_engineer",
    "ui_ux":    "ui_ux_designer",
    "general":  "general_learner",
}

EXPLICIT_ROLE_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(back\s?end|back-end|backend)\b", "backend", "backend_developer"),
    (r"\b(front\s?end|front-end|frontend)\b", "frontend", "frontend_developer"),
    (r"\b(ui\s?/??\s?ux|ux\s?/??\s?ui|figma|wireframe|prototype)\b", "ui_ux", "ui_ux_designer"),
    (r"\b(cyber\s?security|cybersecurity|soc|security analyst)\b", "cyber_security", "soc_analyst"),
    (r"\b(ai\s?ml|ai/ml|machine learning|ml engineer|data science|data scientist)\b", "ai_ml", "machine_learning_engineer"),
    (r"\b(data\s?analyst|analisis data|data analysis|business intelligence|bi analyst)\b", "data", "data_analyst"),
]

LEVEL_KEYWORDS: Dict[str, List[str]] = {
    "beginner":     ["baru mulai", "belum pernah", "pemula", "newbie", "dari nol", "awal", "mulai dari awal"],
    "basic":        ["sudah bisa", "pernah belajar", "basic", "dasar", "sedikit tahu", "pernah coba", "junior"],
    "intermediate": ["sudah pernah project", "intermediate", "sudah paham", "cukup paham", "pernah kerja"],
    "advanced":     ["advanced", "advance", "senior", "expert", "sangat paham", "sudah lama"],
}

INTENT_KEYWORDS: Dict[str, List[str]] = {
    "learn_new":          ["belajar", "mulai", "learn", "start", "ingin tahu", "mau belajar", "ingin jadi", "mau jadi"],
    "build_portfolio":    ["project", "portfolio", "portofolio", "karya", "bangun project"],
    "switch_career":      ["pindah karier", "pindah karir", "career change", "career switch", "ganti profesi", "non-tech"],
    "validate_direction": ["takut salah", "takut salah jalan", "ragu", "bingung", "yakin ga"],
    "skill_gap":          ["skill gap", "kekurangan", "belum bisa", "tidak bisa", "improve"],
    "action_plan":        ["rencana", "plan", "langkah", "roadmap", "recommend", "path"],
}

PERSONA_RULES: List[Tuple[str, str, str]] = [
    ("no_starting_point", "beginner", "beginner_explorer"),
    ("no_portfolio",      "*",        "project_seeker"),
    ("fear_wrong_path",   "*",        "validation_seeker"),
    ("too_many_options",  "*",        "overwhelmed_learner"),
    ("no_time",           "*",        "busy_learner"),
]

# ---------------------------------------------------------------------------
# Model cache (load sekali, reuse)
# ---------------------------------------------------------------------------
_MODEL_CACHE: Dict[str, Any] = {}


def _get_classifier():
    """Load problem_category classifier (cached)."""
    if "problem_category" not in _MODEL_CACHE:
        try:
            from ai_ml_module.utils.model_loader import load_problem_category_model
            _MODEL_CACHE["problem_category"] = load_problem_category_model()
        except ImportError:
            logger.warning("model_loader tidak ditemukan. Fallback ke rule-based.")
            _MODEL_CACHE["problem_category"] = None
    return _MODEL_CACHE["problem_category"]


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_blocker_mapping() -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    if not BLOCKER_CSV.exists():
        return out
    with open(BLOCKER_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            kw = (r.get("keyword") or "").strip().lower()
            bt = (r.get("blocker_type") or "").strip()
            if kw and bt:
                out.setdefault(bt, []).append(kw)
    return out


def _load_label_taxonomy() -> Dict:
    try:
        if LABEL_PATH.exists():
            with open(LABEL_PATH, encoding="utf-8") as fh:
                return json.load(fh)
    except Exception:
        pass
    return {}


# ---------------------------------------------------------------------------
# Scoring helpers (rule-based)
# ---------------------------------------------------------------------------

def _score_domain(txt: str) -> Tuple[str, float]:
    best_domain, best_count = "general", 0
    for domain, kws in DOMAIN_KEYWORDS.items():
        hit = sum(1 for k in kws if _keyword_present(txt, k))
        if hit > best_count:
            best_count, best_domain = hit, domain
    return best_domain, round(min(1.0, best_count / 3.0), 3)


def _domain_hit_counts(txt: str) -> Dict[str, int]:
    return {
        domain: sum(1 for keyword in keywords if _keyword_present(txt, keyword))
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }


def _keyword_present(txt: str, keyword: str) -> bool:
    if len(keyword) <= 3 and keyword.isalnum():
        return re.search(rf"\b{re.escape(keyword)}\b", txt) is not None
    return keyword in txt


def _explicit_role_match(txt: str) -> Optional[Tuple[str, str]]:
    for pattern, domain, role in EXPLICIT_ROLE_PATTERNS:
        if re.search(pattern, txt):
            return domain, role
    return None


def _score_level(txt: str) -> Tuple[str, float]:
    best_level, best_hit = "beginner", 0
    for level, kws in LEVEL_KEYWORDS.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > best_hit:
            best_hit, best_level = hit, level
    return best_level, round(min(1.0, best_hit / 2.0), 3)


def _score_blocker(txt: str, blocker_map: Dict[str, List[str]]) -> Tuple[str, float]:
    best_type, best_hit = "none", 0
    for btype, kws in blocker_map.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > best_hit:
            best_hit, best_type = hit, btype
    heuristic_blockers = {
        "no_portfolio": ["tidak ada portofolio", "ga ada portofolio", "belum ada portofolio", "tidak punya portofolio", "portfolio", "portofolio"],
        "no_starting_point": ["mulai dari mana", "apa saja yang harus dipelajari", "harus dipelajari", "roadmap", "langkah"],
        "skill_gap_confusion": ["belum paham", "tidak paham", "skill kurang", "skill gap", "belum bisa"],
        "fear_wrong_path": ["takut salah", "salah pilih", "takut ga cocok", "tidak yakin"],
    }
    for btype, kws in heuristic_blockers.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > best_hit:
            best_hit, best_type = hit, btype
    return best_type, round(min(1.0, best_hit / 2.0), 3)


def _score_intent(txt: str) -> Tuple[str, float]:
    best_intent, best_hit = "skill_gap", 0
    for intent, kws in INTENT_KEYWORDS.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > best_hit:
            best_hit, best_intent = hit, intent
    return best_intent, round(min(1.0, best_hit / 2.0), 3)


def _rule_based_problem_category(domain: str, blocker: str) -> str:
    """Fallback rule-based untuk problem_category."""
    if blocker != "none":
        return f"{blocker}_issue"
    return f"{domain}_task"


def _ml_prediction_matches_context(prediction: str, domain: str, blocker: str) -> bool:
    """Prevent an old classifier from overriding newly added capstone domains."""
    taxonomy = _load_label_taxonomy()
    known_categories = set(taxonomy.get("problem_category", []))
    prediction = str(prediction)

    # Domain/blocker-formatted labels must match the detected context.
    if prediction.endswith("_task"):
        return prediction == f"{domain}_task"
    if prediction.endswith("_issue"):
        return blocker != "none" and prediction == f"{blocker}_issue"

    # Capstone model labels are problem-shape labels such as direction_confused.
    return prediction in known_categories


def _resolve_persona(blocker_type: str, current_level: str) -> str:
    for rule_blocker, rule_level, persona in PERSONA_RULES:
        if rule_blocker == blocker_type:
            if rule_level == "*" or rule_level == current_level:
                return persona
    return "learner"


def _has_any(txt: str, keywords: List[str]) -> bool:
    return any(keyword in txt for keyword in keywords)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def analyze_pretext(user_input_text: str) -> Dict[str, Any]:
    """Analyze free-text → structured pretext dict.

    Menggunakan ML classifier untuk `problem_category` jika model tersedia,
    field lain tetap menggunakan weighted rule-based scoring.

    Confidence score:
        confidence = domain_score * 0.35
                   + level_score  * 0.25
                   + blocker_score* 0.20
                   + intent_score * 0.20
    """
    txt = " ".join((user_input_text or "").lower().split())

    blocker_map = _load_blocker_mapping()

    # --- Rule-based scoring ---
    domain_interest, domain_score  = _score_domain(txt)
    current_level,   level_score   = _score_level(txt)
    blocker_type,    blocker_score = _score_blocker(txt, blocker_map)
    intent,          intent_score  = _score_intent(txt)
    explicit_role = _explicit_role_match(txt)
    if explicit_role:
        domain_interest, explicit_target_role = explicit_role
        domain_score = max(domain_score, 1.0)
    else:
        explicit_target_role = None
        if domain_interest == "general" and blocker_type in {"no_starting_point", "fear_wrong_path"}:
            blocker_type, blocker_score = "none", 0.0
    if _has_any(txt, ["pengalaman", "2 tahun", "pernah kerja", "belajar 2 tahun"]):
        current_level, level_score = "intermediate", max(level_score, 0.5)
    domain_hits = _domain_hit_counts(txt)
    mentioned_domains = [domain for domain, hit in domain_hits.items() if hit > 0]
    skill_signal_count = sum(domain_hits.values())
    role_ambiguity = len(mentioned_domains) >= 2 and _has_any(
        txt,
        ["antara", "atau", "vs", "mana", "pilih", "dibanding", "dibandingkan", "ataukah"],
    )
    confusion_signal = _has_any(
        txt,
        ["bingung", "ragu", "ga tahu", "tidak tahu", "tidak yakin", "takut", "sulit memilih", "salah pilih", "overthinking"],
    )
    overwhelmed_signal = ((not explicit_role or role_ambiguity) and len(mentioned_domains) >= 3) or _has_any(
        txt,
        ["terlalu banyak", "banyak banget", "kewalahan", "overwhelmed", "tidak tahu prioritas", "ga tahu fokus"],
    )
    clear_direction_signal = _has_any(
        txt,
        ["jelas mau", "target saya", "ingin jadi", "mau jadi"],
    ) and not role_ambiguity and not confusion_signal

    # --- Weighted confidence ---
    confidence_score = round(min(1.0,
        domain_score  * WEIGHT_DOMAIN  +
        level_score   * WEIGHT_LEVEL   +
        blocker_score * WEIGHT_BLOCKER +
        intent_score  * WEIGHT_INTENT
    ), 2)

    # Deterministic confidence calibration for confused-vs-clear user scenarios.
    # The weighted keyword score is intentionally simple, so calibrate obvious
    # product-critical cases without letting ML override the source-of-truth logic.
    if explicit_role and domain_interest != "general":
        confidence_score = max(confidence_score, 0.72)
    if clear_direction_signal and domain_interest != "general":
        confidence_score = max(confidence_score, 0.75)
    if skill_signal_count >= 3 and not role_ambiguity and not confusion_signal:
        confidence_score = max(confidence_score, 0.78)
    if _has_any(txt, ["pengalaman", "2 tahun", "sudah advance", "sudah advanced"]) and not role_ambiguity:
        confidence_score = max(confidence_score, 0.75)
    if confusion_signal and not clear_direction_signal:
        confidence_score = min(confidence_score, 0.68)
    if role_ambiguity:
        confidence_score = min(confidence_score, 0.74)
    if overwhelmed_signal:
        confidence_score = min(confidence_score, 0.58 if role_ambiguity else 0.62)

    # --- problem_category: coba ML dulu, fallback rule-based ---
    ml_used = False
    ml_confidence: Optional[float] = None
    classifier_type = "rule_based"
    model_format: Optional[str] = None
    problem_category = _rule_based_problem_category(domain_interest, blocker_type)

    classifier = _get_classifier()
    if classifier is not None:
        try:
            classifier_type = getattr(classifier, "classifier_type", "sklearn")
            model_format = getattr(classifier, "model_format", ".joblib")
            prediction = classifier.predict([user_input_text])[0]
            predicted_category = str(prediction)
            ml_used = True

            # ambil probability jika model support predict_proba
            if hasattr(classifier, "predict_proba"):
                proba = classifier.predict_proba([user_input_text])[0]
                ml_confidence = round(float(max(proba)), 3)

            logger.debug(
                f"{classifier_type} prediction: {predicted_category} "
                f"(confidence: {ml_confidence})"
            )
            low_confidence = classifier_type == "tensorflow" and ml_confidence is not None and ml_confidence < 0.5
            if not low_confidence and _ml_prediction_matches_context(predicted_category, domain_interest, blocker_type):
                problem_category = predicted_category
            else:
                problem_category = _rule_based_problem_category(domain_interest, blocker_type)
        except Exception as e:
            logger.warning(f"ML prediction gagal: {e}. Fallback ke rule-based.")
            problem_category = _rule_based_problem_category(domain_interest, blocker_type)
            ml_used = False
            classifier_type = "rule_based"
            model_format = None

    # --- Derived fields ---
    target_role  = explicit_target_role or DOMAIN_TO_ROLE.get(domain_interest, "general_learner")
    persona_type = _resolve_persona(blocker_type, current_level)
    if overwhelmed_signal:
        persona_type = "overwhelmed_learner"
    needs_assessment = confidence_score < 0.7 or current_level == "beginner" or role_ambiguity or confusion_signal
    if confidence_score >= 0.78:
        confidence_label = "Tinggi"
        confidence_explanation = "Role dan sinyal kebutuhan user cukup jelas dari input."
    elif confidence_score >= 0.55:
        confidence_label = "Sedang"
        confidence_explanation = "Role utama terbaca, tetapi beberapa detail masih perlu divalidasi lewat assessment."
    else:
        confidence_label = "Rendah"
        confidence_explanation = "Input masih ambigu; sistem perlu klarifikasi sebelum memberi rekomendasi kuat."

    result: Dict[str, Any] = {
        "intent":           intent,
        "domain_interest":  domain_interest,
        "target_role":      target_role,
        "problem_category": problem_category,
        "current_level":    current_level,
        "blocker_type":     blocker_type,
        "persona_type":     persona_type,
        "confidence_score": confidence_score,
        "needs_assessment": needs_assessment,
        # metadata untuk debugging & monitoring
        "_meta": {
            "ml_used":        ml_used,
            "ml_confidence":  ml_confidence,
            "classifier_type": classifier_type,
            "model_format": model_format,
            "confidence_score": confidence_score,
            "confidence_label": confidence_label,
            "confidence_explanation": confidence_explanation,
            "scores": {
                "domain_score":  domain_score,
                "level_score":   level_score,
                "blocker_score": blocker_score,
                "intent_score":  intent_score,
                "role_ambiguity": role_ambiguity,
                "confusion_signal": confusion_signal,
                "overwhelmed_signal": overwhelmed_signal,
            },
        },
    }

    return result


__all__ = ["analyze_pretext"]
