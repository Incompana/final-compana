"""Custom TensorFlow components for Compana model training."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json


class ConfidenceLoggingCallback:
    """Log validation confidence after each epoch.

    This callback is intentionally small and explainable: it records validation
    accuracy/loss snapshots so the team can inspect whether a model is stable
    enough to act as an assistive classifier.
    """

    def __init__(self, output_path: str | Path | None = None) -> None:
        try:
            import tensorflow as tf
        except Exception as exc:  # pragma: no cover - import guarded for non-TF envs
            raise RuntimeError("TensorFlow is required for ConfidenceLoggingCallback") from exc

        class _Callback(tf.keras.callbacks.Callback):
            def __init__(self, path: str | Path | None) -> None:
                super().__init__()
                self.output_path = Path(path) if path else None
                self.history_rows: List[Dict[str, Any]] = []

            def on_epoch_end(self, epoch: int, logs: Dict[str, Any] | None = None) -> None:
                logs = logs or {}
                row = {
                    "epoch": int(epoch + 1),
                    "loss": _to_float(logs.get("loss")),
                    "accuracy": _to_float(logs.get("accuracy")),
                    "val_loss": _to_float(logs.get("val_loss")),
                    "val_accuracy": _to_float(logs.get("val_accuracy")),
                }
                self.history_rows.append(row)
                if self.output_path:
                    self.output_path.parent.mkdir(parents=True, exist_ok=True)
                    self.output_path.write_text(
                        json.dumps(self.history_rows, indent=2),
                        encoding="utf-8",
                    )

        self.callback = _Callback(output_path)


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def make_confidence_logging_callback(output_path: str | Path | None = None):
    """Factory returning a real tf.keras callback instance."""
    return ConfidenceLoggingCallback(output_path).callback

