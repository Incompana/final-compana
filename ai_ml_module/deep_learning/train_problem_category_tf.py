"""Train TensorFlow Functional API model for problem_category classification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from ai_ml_module.deep_learning.custom_components import make_confidence_logging_callback


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = PROJECT_ROOT / "data" / "labels" / "dataset_pretext.csv"
DEFAULT_MODEL = PROJECT_ROOT / "ai_ml_module" / "models" / "problem_category_tf.keras"
DEFAULT_LABELS = PROJECT_ROOT / "ai_ml_module" / "models" / "problem_category_tf_labels.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "evaluation" / "outputs" / "problem_category_tensorflow"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train TensorFlow problem_category classifier.")
    parser.add_argument("--data", default=str(DEFAULT_DATA))
    parser.add_argument("--text-col", default="pretext")
    parser.add_argument("--label-col", default="problem_category")
    parser.add_argument("--model-out", default=str(DEFAULT_MODEL))
    parser.add_argument("--labels-out", default=str(DEFAULT_LABELS))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--sequence-length", type=int, default=160)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def _load_dataset(path: Path, text_col: str, label_col: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = {text_col, label_col} - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {sorted(missing)}")
    df = df[[text_col, label_col]].dropna()
    df[text_col] = df[text_col].astype(str).str.strip()
    df[label_col] = df[label_col].astype(str).str.strip()
    df = df[(df[text_col] != "") & (df[label_col] != "")]
    if df.empty:
        raise ValueError("Dataset is empty after cleaning.")
    return df


def _split_data(df: pd.DataFrame, label_col: str, random_state: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stratify = df[label_col] if df[label_col].value_counts().min() >= 2 else None
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=random_state,
        stratify=stratify,
    )
    temp_stratify = temp_df[label_col] if temp_df[label_col].value_counts().min() >= 2 else None
    dev_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=random_state,
        stratify=temp_stratify,
    )
    return train_df, dev_df, test_df


def _build_model(
    train_texts: np.ndarray,
    class_count: int,
    max_tokens: int,
    sequence_length: int,
    embedding_dim: int,
):
    import tensorflow as tf

    vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=max_tokens,
        output_mode="int",
        output_sequence_length=sequence_length,
        name="text_vectorization",
    )
    vectorizer.adapt(tf.constant(train_texts))

    inputs = tf.keras.Input(shape=(), dtype=tf.string, name="pretext_text")
    x = vectorizer(inputs)
    x = tf.keras.layers.Embedding(
        input_dim=max_tokens,
        output_dim=embedding_dim,
        mask_zero=True,
        name="token_embedding",
    )(x)
    x = tf.keras.layers.GlobalAveragePooling1D(name="average_pooling")(x)
    x = tf.keras.layers.Dense(96, activation="relu", name="dense_features")(x)
    x = tf.keras.layers.Dropout(0.25, name="dropout")(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax", name="problem_category")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="compana_problem_category_functional")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _encode_labels(labels: pd.Series) -> Tuple[Dict[str, int], Dict[int, str]]:
    unique = sorted(labels.unique().tolist())
    label_to_id = {label: idx for idx, label in enumerate(unique)}
    id_to_label = {idx: label for label, idx in label_to_id.items()}
    return label_to_id, id_to_label


def _save_reports(
    output_dir: Path,
    test_labels: np.ndarray,
    predictions: np.ndarray,
    labels: list[str],
    history: Dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = classification_report(test_labels, predictions, target_names=labels, output_dict=True, zero_division=0)
    matrix = confusion_matrix(test_labels, predictions, labels=list(range(len(labels))))
    pd.DataFrame(report).transpose().to_csv(output_dir / "classification_report.csv")
    pd.DataFrame(
        matrix,
        index=[f"true_{label}" for label in labels],
        columns=[f"pred_{label}" for label in labels],
    ).to_csv(output_dir / "confusion_matrix.csv")
    metrics = {
        "accuracy": float(accuracy_score(test_labels, predictions)),
        "macro_f1": float(f1_score(test_labels, predictions, average="macro")),
        "weighted_f1": float(f1_score(test_labels, predictions, average="weighted")),
        "history": history,
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    model_path = Path(args.model_out)
    labels_path = Path(args.labels_out)
    output_dir = Path(args.output_dir)

    import tensorflow as tf

    tf.keras.utils.set_random_seed(args.random_state)

    df = _load_dataset(data_path, args.text_col, args.label_col)
    train_df, dev_df, test_df = _split_data(df, args.label_col, args.random_state)
    label_to_id, id_to_label = _encode_labels(df[args.label_col])
    labels = [id_to_label[idx] for idx in range(len(id_to_label))]

    x_train = train_df[args.text_col].to_numpy(dtype=str)
    y_train = train_df[args.label_col].map(label_to_id).to_numpy(dtype="int32")
    x_dev = dev_df[args.text_col].to_numpy(dtype=str)
    y_dev = dev_df[args.label_col].map(label_to_id).to_numpy(dtype="int32")
    x_test = test_df[args.text_col].to_numpy(dtype=str)
    y_test = test_df[args.label_col].map(label_to_id).to_numpy(dtype="int32")

    model = _build_model(
        x_train,
        class_count=len(labels),
        max_tokens=args.max_tokens,
        sequence_length=args.sequence_length,
        embedding_dim=args.embedding_dim,
    )

    callbacks = [
        make_confidence_logging_callback(output_dir / "confidence_history.json"),
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
    ]
    train_ds = tf.data.Dataset.from_tensor_slices((tf.constant(x_train), tf.constant(y_train))).batch(args.batch_size)
    dev_ds = tf.data.Dataset.from_tensor_slices((tf.constant(x_dev), tf.constant(y_dev))).batch(args.batch_size)
    test_ds = tf.data.Dataset.from_tensor_slices(tf.constant(x_test)).batch(args.batch_size)

    history = model.fit(
        train_ds,
        validation_data=dev_ds,
        epochs=args.epochs,
        callbacks=callbacks,
        verbose=2,
    )

    proba = model.predict(test_ds, verbose=0)
    predictions = np.argmax(proba, axis=1)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)
    labels_path.write_text(
        json.dumps(
            {
                "labels": labels,
                "label_to_id": label_to_id,
                "model_type": "tensorflow_functional_api",
                "data_path": str(data_path),
                "text_col": args.text_col,
                "label_col": args.label_col,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    _save_reports(output_dir, y_test, predictions, labels, history.history)

    print(json.dumps({
        "model_path": str(model_path),
        "labels_path": str(labels_path),
        "output_dir": str(output_dir),
        "test_accuracy": float(accuracy_score(y_test, predictions)),
        "test_macro_f1": float(f1_score(y_test, predictions, average="macro")),
    }, indent=2))


if __name__ == "__main__":
    main()
