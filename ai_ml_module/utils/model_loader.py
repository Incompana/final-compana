"""Model Loader — utility untuk load ML classifier artifacts.

Dipakai Engine 1 (dan engine lain ke depannya) untuk load model .joblib
dengan graceful fallback jika model tidak tersedia.

Lokasi model yang dicari (urutan prioritas):
1. ai_ml_module/models/
2. evaluation/outputs/notebook_problem_category_baseline/
3. evaluation/outputs/problem_category_baseline_expanded/
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

# Kandidat lokasi model (urutan prioritas)
MODEL_SEARCH_PATHS = [
    ROOT / "ai_ml_module" / "models",
    ROOT / "evaluation" / "outputs" / "notebook_problem_category_baseline",
    ROOT / "evaluation" / "outputs" / "problem_category_baseline_expanded",
]

# Nama file model yang dicari
TENSORFLOW_PROBLEM_CATEGORY_MODEL = "problem_category_tf.keras"
TENSORFLOW_PROBLEM_CATEGORY_LABELS = "problem_category_tf_labels.json"

PROBLEM_CATEGORY_MODEL_NAMES = [
    "problem_category_logreg_notebook.joblib",
    "problem_category_logreg.joblib",
    "model.joblib",
]


def _find_model_file(filenames: list[str]) -> Optional[Path]:
    """Cari file model di semua search paths."""
    for search_dir in MODEL_SEARCH_PATHS:
        for fname in filenames:
            p = search_dir / fname
            if p.exists():
                return p
    return None


def load_problem_category_model() -> Optional[Any]:
    """Load best available problem_category classifier.

    Returns:
        TensorFlow wrapper jika .keras tersedia, sklearn model jika tersedia,
        None jika tidak ada (fallback ke rule-based).
    """
    tf_model_path = MODEL_SEARCH_PATHS[0] / TENSORFLOW_PROBLEM_CATEGORY_MODEL
    tf_labels_path = MODEL_SEARCH_PATHS[0] / TENSORFLOW_PROBLEM_CATEGORY_LABELS
    if tf_model_path.exists() and tf_labels_path.exists():
        try:
            from ai_ml_module.deep_learning.inference_tf import TensorFlowProblemCategoryClassifier
            model = TensorFlowProblemCategoryClassifier(tf_model_path, tf_labels_path)
            logger.info(f"TensorFlow problem_category model dimuat dari: {tf_model_path}")
            return model
        except Exception as e:
            logger.warning(f"Gagal load TensorFlow model dari {tf_model_path}: {e}. Fallback ke sklearn.")

    model_path = _find_model_file(PROBLEM_CATEGORY_MODEL_NAMES)
    if not model_path:
        logger.info(
            "Model problem_category tidak ditemukan. "
            "Jalankan notebook atau train_problem_category_baseline.py dulu. "
            "Fallback ke rule-based."
        )
        return None

    try:
        import joblib
        model = joblib.load(model_path)
        logger.info(f"Model problem_category berhasil dimuat dari: {model_path}")
        return model
    except Exception as e:
        logger.warning(f"Gagal load model dari {model_path}: {e}. Fallback ke rule-based.")
        return None


def get_model_status() -> dict:
    """Cek status ketersediaan semua model. Berguna untuk health check API."""
    tf_model_path = MODEL_SEARCH_PATHS[0] / TENSORFLOW_PROBLEM_CATEGORY_MODEL
    tf_labels_path = MODEL_SEARCH_PATHS[0] / TENSORFLOW_PROBLEM_CATEGORY_LABELS
    sklearn_path = _find_model_file(PROBLEM_CATEGORY_MODEL_NAMES)
    tensorflow_available = tf_model_path.exists() and tf_labels_path.exists()
    if tensorflow_available:
        active_classifier = "tensorflow"
    elif sklearn_path is not None:
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
            "available": sklearn_path is not None,
            "path": str(sklearn_path) if sklearn_path else None,
            "format": ".joblib",
        },
        "active_classifier": active_classifier,
    }


__all__ = ["load_problem_category_model", "get_model_status"]
