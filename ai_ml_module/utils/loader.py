"""Loader utilities to read official datasets for Engines 5-8.

Rules: Only load the official dataset filenames. If not present in `ai_ml_module/data/`,
try to find equivalents in the repository (e.g., configs/ or ai_engines_5_8/outputs/).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "data"

# ---------------------------------------------------------------------------
# Data contract required columns
# ---------------------------------------------------------------------------
ROLE_SKILL_COLUMNS = [
    "role_id",
    "role_name",
    "domain_interest",
    "required_skill_id",
    "required_skill_name",
    "skill_category",
    "priority",
    "minimum_level",
    "step_order",
    "prerequisite_skill_id",
]

TASK_BANK_COLUMNS = [
    "task_id",
    "domain_interest",
    "target_role",
    "target_skill_id",
    "current_level",
    "task_title",
    "task_description",
    "duration_estimate",
    "output_format",
    "difficulty",
    "prerequisite_skill_id",
]

RUBRIC_COLUMNS = [
    "rubric_id",
    "task_id",
    "criteria",
    "weight",
    "required",
    "keyword_signal",
    "feedback_if_missing",
]

LABEL_KEYS = [
    "intent",
    "domain_interest",
    "target_role",
    "problem_category",
    "current_level",
    "blocker_type",
    "persona_type",
]

# ---------------------------------------------------------------------------
# Model search paths
# ---------------------------------------------------------------------------
MODELS_DIR = ROOT / "ai_ml_module" / "models"

MODEL_SEARCH_PATHS = [
    MODELS_DIR,
    ROOT / "evaluation" / "outputs" / "notebook_problem_category_baseline",
    ROOT / "evaluation" / "outputs" / "problem_category_baseline_expanded",
]

PROBLEM_CATEGORY_MODEL_NAMES = [
    "problem_category_logreg_notebook.joblib",
    "problem_category_logreg.joblib",
    "model.joblib",
]

TENSORFLOW_PROBLEM_CATEGORY_MODEL = "problem_category_tf.keras"
TENSORFLOW_PROBLEM_CATEGORY_LABELS = "problem_category_tf_labels.json"


# ---------------------------------------------------------------------------
# Dataset finders
# ---------------------------------------------------------------------------

def _find_file(filename: str) -> Optional[Path]:
    p = DEFAULT_DATA_DIR / filename
    if p.exists():
        return p
    alt = [Path("configs") / filename, Path("ai_engines_5_8") / "outputs" / filename]
    for a in alt:
        if a.exists():
            return a
    return None


def _validate_columns(df: pd.DataFrame, required: List[str]) -> List[str]:
    return [c for c in required if c not in df.columns]


# ---------------------------------------------------------------------------
# Dataset loaders
# ---------------------------------------------------------------------------

def load_label_taxonomy() -> Dict:
    p = _find_file("label_taxonomy.json") or _find_file("label_taxonomy.schema.json")
    if not p:
        raise FileNotFoundError("label_taxonomy.json not found in ai_ml_module/data or configs")
    with open(p, "r", encoding="utf-8") as fh:
        j = json.load(fh)
    missing_keys = [k for k in LABEL_KEYS if k not in j]
    if missing_keys:
        raise ValueError(f"label_taxonomy.json missing required keys: {missing_keys}")
    return j


def load_rubric_taxonomy() -> Dict:
    p = _find_file("rubric_taxonomy.json")
    if not p:
        return {}
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_role_skill_mapping() -> pd.DataFrame:
    p = _find_file("role_skill_mapping.csv")
    if not p:
        raise FileNotFoundError("role_skill_mapping.csv not found in ai_ml_module/data or ai_engines_5_8/outputs")
    df = pd.read_csv(p)
    missing = _validate_columns(df, ROLE_SKILL_COLUMNS)
    if missing:
        raise ValueError(f"role_skill_mapping.csv is missing required columns: {missing}")
    return df


def load_task_bank() -> pd.DataFrame:
    p = _find_file("task_bank.csv")
    if not p:
        raise FileNotFoundError("task_bank.csv not found in ai_ml_module/data or ai_engines_5_8/outputs")
    df = pd.read_csv(p)
    missing = _validate_columns(df, TASK_BANK_COLUMNS)
    if missing:
        raise ValueError(f"task_bank.csv is missing required columns: {missing}")
    return df


def load_rubric_feedback_bank() -> pd.DataFrame:
    p = _find_file("rubric_feedback_bank.csv") or _find_file("rubric_bank.csv")
    if not p:
        raise FileNotFoundError("rubric_feedback_bank.csv not found in ai_ml_module/data or ai_engines_5_8/outputs")
    df = pd.read_csv(p)
    missing = _validate_columns(df, RUBRIC_COLUMNS)
    if missing:
        raise ValueError(f"rubric_feedback_bank.csv is missing required columns: {missing}")
    return df


def get_role_skills_dict() -> Dict[str, List[str]]:
    df = load_role_skill_mapping()
    out: Dict[str, List[str]] = {}
    for _, r in df.iterrows():
        role = str(r["role_id"]).strip()
        skill = str(r["required_skill_id"]).strip()
        if not role or not skill:
            continue
        out.setdefault(role, []).append(skill)
    return out


# ---------------------------------------------------------------------------
# Model loaders
# ---------------------------------------------------------------------------

def _find_model_file(filenames: List[str]) -> Optional[Path]:
    """Cari file model di semua search paths."""
    for search_dir in MODEL_SEARCH_PATHS:
        for fname in filenames:
            p = search_dir / fname
            if p.exists():
                return p
    return None


def load_problem_category_model() -> Optional[object]:
    """Load sklearn Pipeline problem_category classifier.

    Returns:
        Model object jika ditemukan dan berhasil load.
        None jika tidak ditemukan (Engine 1 fallback ke rule-based).
    """
    model_path = _find_model_file(PROBLEM_CATEGORY_MODEL_NAMES)
    if not model_path:
        logger.info(
            "Model problem_category tidak ditemukan. "
            "Fallback ke rule-based. Untuk mengaktifkan ML, jalankan: "
            "notebooks/compana_ai_ml_training_overview.ipynb atau "
            "scripts/train_problem_category_baseline.py"
        )
        return None

    try:
        import joblib
        model = joblib.load(model_path)
        logger.info(f"Model dimuat dari: {model_path}")
        return model
    except Exception as e:
        logger.warning(f"Gagal load model dari {model_path}: {e}. Fallback ke rule-based.")
        return None


def get_model_status() -> Dict:
    """Cek status ketersediaan model. Untuk health check endpoint /model-status."""
    tf_model_path = MODELS_DIR / TENSORFLOW_PROBLEM_CATEGORY_MODEL
    tf_labels_path = MODELS_DIR / TENSORFLOW_PROBLEM_CATEGORY_LABELS
    path = _find_model_file(PROBLEM_CATEGORY_MODEL_NAMES)
    tensorflow_available = tf_model_path.exists() and tf_labels_path.exists()
    if tensorflow_available:
        active_classifier = "tensorflow"
    elif path is not None:
        active_classifier = "sklearn"
    else:
        active_classifier = "rule_based"
    return {
        "tensorflow_problem_category_model": {
            "available": tensorflow_available,
            "path": str(tf_model_path) if tf_model_path.exists() else None,
            "labels_path": str(tf_labels_path) if tf_labels_path.exists() else None,
            "format": ".keras",
        },
        "problem_category_model": {
            "available": path is not None,
            "path": str(path) if path else None,
            "format": ".joblib",
            "search_paths": [str(p) for p in MODEL_SEARCH_PATHS],
        },
        "active_classifier": active_classifier,
    }
