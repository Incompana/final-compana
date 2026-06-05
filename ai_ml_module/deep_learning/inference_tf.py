"""TensorFlow inference utilities for problem_category classifier."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = PROJECT_ROOT / "ai_ml_module" / "models" / "problem_category_tf.keras"
DEFAULT_LABELS = PROJECT_ROOT / "ai_ml_module" / "models" / "problem_category_tf_labels.json"


class TensorFlowProblemCategoryClassifier:
    """Small sklearn-like wrapper around the exported TensorFlow model."""

    classifier_type = "tensorflow"
    model_format = ".keras"
    model_type = "tensorflow_functional_api"

    def __init__(self, model_path: str | Path = DEFAULT_MODEL, labels_path: str | Path = DEFAULT_LABELS) -> None:
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"TensorFlow model not found: {self.model_path}")
        if not self.labels_path.exists():
            raise FileNotFoundError(f"TensorFlow labels not found: {self.labels_path}")

        import tensorflow as tf

        self.model = tf.keras.models.load_model(self.model_path)
        metadata = json.loads(self.labels_path.read_text(encoding="utf-8"))
        self.labels: List[str] = list(metadata["labels"])
        self.metadata = metadata

    def predict_proba(self, texts: Iterable[str]) -> np.ndarray:
        batch = np.array([str(text) for text in texts], dtype=object)
        proba = self.model.predict(batch, verbose=0)
        return np.asarray(proba, dtype=float)

    def predict(self, texts: Iterable[str]) -> np.ndarray:
        proba = self.predict_proba(texts)
        indexes = np.argmax(proba, axis=1)
        return np.array([self.labels[int(index)] for index in indexes], dtype=object)

    def predict_one(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        proba = self.predict_proba([text])[0]
        order = np.argsort(proba)[::-1][:top_k]
        top = [
            {"label": self.labels[int(index)], "confidence": round(float(proba[int(index)]), 6)}
            for index in order
        ]
        return {
            "label": top[0]["label"] if top else "",
            "confidence": top[0]["confidence"] if top else 0.0,
            "top_k": top,
            "model_type": self.model_type,
            "classifier_type": self.classifier_type,
            "model_format": self.model_format,
        }


def predict_text(text: str, model_path: str | Path = DEFAULT_MODEL, labels_path: str | Path = DEFAULT_LABELS, top_k: int = 3) -> Dict[str, Any]:
    classifier = TensorFlowProblemCategoryClassifier(model_path, labels_path)
    return classifier.predict_one(text, top_k=top_k)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TensorFlow problem_category inference.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--labels", default=str(DEFAULT_LABELS))
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = predict_text(args.text, args.model, args.labels, top_k=args.top_k)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

