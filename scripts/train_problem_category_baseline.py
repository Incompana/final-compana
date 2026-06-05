from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, Tuple

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

# Ensure local project modules are imported instead of similarly named site-packages.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rule_engine.baseline_pretext_engine import inspect_pretext


# Simple supported model choices for baseline experiments.
MODEL_CHOICES = ("logreg", "linear_svm")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and evaluate baseline ML for problem_category classification."
    )
    parser.add_argument(
        "--data",
        default="data/labels/compana_synthetic_pretext_id_v1.csv",
        help="CSV path containing pretext_text and problem_category columns.",
    )
    parser.add_argument("--text-col", default="pretext_text")
    parser.add_argument("--label-col", default="problem_category")
    parser.add_argument(
        "--model",
        default="logreg",
        choices=MODEL_CHOICES,
        help="Baseline model type.",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--dev-size", type=float, default=0.1)
    parser.add_argument(
        "--output-dir",
        default="evaluation/outputs/problem_category_baseline",
        help="Directory for reports, confusion matrices, and saved model.",
    )
    return parser.parse_args()


def _ensure_jsonable(value: Any) -> Any:
    """Convert numpy/pandas scalars to builtin JSON types recursively."""
    if isinstance(value, dict):
        return {k: _ensure_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_ensure_jsonable(v) for v in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def _build_pipeline(model_type: str, random_state: int) -> Pipeline:
    if model_type == "linear_svm":
        classifier = LinearSVC()
    else:
        classifier = LogisticRegression(max_iter=300, random_state=random_state)

    # TF-IDF + linear model keeps the baseline explainable and fast.
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", classifier),
        ]
    )


def _split_data(
    df: pd.DataFrame,
    label_col: str,
    test_size: float,
    dev_size: float,
    random_state: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    temp_size = test_size + dev_size
    if temp_size <= 0 or temp_size >= 1:
        raise ValueError("test_size + dev_size must be between 0 and 1.")

    stratify_labels = df[label_col] if df[label_col].value_counts().min() >= 2 else None
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_size,
        random_state=random_state,
        stratify=stratify_labels,
    )

    # Split temp into dev and test while preserving requested ratio.
    test_share_in_temp = test_size / temp_size
    temp_stratify = temp_df[label_col] if temp_df[label_col].value_counts().min() >= 2 else None
    dev_df, test_df = train_test_split(
        temp_df,
        test_size=test_share_in_temp,
        random_state=random_state,
        stratify=temp_stratify,
    )
    return train_df, dev_df, test_df


def _report_dict(y_true: pd.Series, y_pred: pd.Series, labels: list[str]) -> Dict[str, Any]:
    return classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )


def _save_confusion_matrix(
    y_true: pd.Series,
    y_pred: pd.Series,
    labels: list[str],
    out_path: Path,
) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    df_matrix = pd.DataFrame(
        matrix,
        index=[f"true_{label}" for label in labels],
        columns=[f"pred_{label}" for label in labels],
    )
    df_matrix.to_csv(out_path, index=True)


def _evaluate_rule_engine(texts: pd.Series) -> list[str]:
    predictions = []
    for text in texts:
        result = inspect_pretext(str(text))
        predictions.append(result["problem_category"])
    return predictions


def _write_comparison_note(
    out_path: Path,
    model_name: str,
    dataset_rows: int,
    ml_accuracy: float,
    ml_macro_f1: float,
    rule_accuracy: float,
    rule_macro_f1: float,
) -> None:
    diff_f1 = ml_macro_f1 - rule_macro_f1
    diff_acc = ml_accuracy - rule_accuracy

    if diff_f1 > 0.02:
        headline = "ML baseline outperformed rule-based baseline on macro F1."
    elif diff_f1 < -0.02:
        headline = "Rule-based baseline outperformed ML baseline on macro F1."
    else:
        headline = "ML and rule-based baselines are close on macro F1."

    # Be explicit that synthetic + small data cannot justify strong general claims.
    caution = (
        "Dataset size is small and synthetic, so results are directional only. "
        "Do not treat this as production-level evidence."
        if dataset_rows < 500
        else "Dataset is larger, but external validation is still required before production claims."
    )

    content = f"""# Problem Category Baseline Comparison

## Summary

- {headline}
- Model: `{model_name}` with TF-IDF features.
- Test metrics:
  - ML accuracy: `{ml_accuracy:.4f}`
  - ML macro F1: `{ml_macro_f1:.4f}`
  - Rule accuracy: `{rule_accuracy:.4f}`
  - Rule macro F1: `{rule_macro_f1:.4f}`
  - Accuracy delta (ML - Rule): `{diff_acc:.4f}`
  - Macro F1 delta (ML - Rule): `{diff_f1:.4f}`

## Interpretation

- Rule-based baseline is easier to explain and deterministic by design.
- ML baseline can generalize keyword variation better, but is data-dependent.
- {caution}

## Recommendation

- Keep rule-based baseline as safe fallback.
- Use ML as optional assist only after validating with more real user data.
"""
    out_path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()

    data_path = Path(args.data)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    # 1) Load and validate minimal required columns.
    df = pd.read_csv(data_path)
    required = {args.text_col, args.label_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Keep only required fields and drop empty rows.
    df = df[[args.text_col, args.label_col]].dropna().copy()
    df[args.text_col] = df[args.text_col].astype(str)
    df[args.label_col] = df[args.label_col].astype(str)

    labels = sorted(df[args.label_col].unique().tolist())

    # 2) Build train/dev/test split.
    train_df, dev_df, test_df = _split_data(
        df=df,
        label_col=args.label_col,
        test_size=args.test_size,
        dev_size=args.dev_size,
        random_state=args.random_state,
    )

    # 3) Train baseline model.
    pipeline = _build_pipeline(model_type=args.model, random_state=args.random_state)
    pipeline.fit(train_df[args.text_col], train_df[args.label_col])

    # Save model so it can be reused without retraining.
    joblib.dump(pipeline, out_dir / f"problem_category_{args.model}.joblib")

    # 4) Evaluate ML baseline on dev and test.
    ml_dev_pred = pipeline.predict(dev_df[args.text_col])
    ml_test_pred = pipeline.predict(test_df[args.text_col])

    ml_dev_report = _report_dict(dev_df[args.label_col], ml_dev_pred, labels)
    ml_test_report = _report_dict(test_df[args.label_col], ml_test_pred, labels)

    _save_confusion_matrix(dev_df[args.label_col], ml_dev_pred, labels, out_dir / "ml_dev_confusion_matrix.csv")
    _save_confusion_matrix(test_df[args.label_col], ml_test_pred, labels, out_dir / "ml_test_confusion_matrix.csv")

    # 5) Evaluate rule-based baseline on the same test split for fair comparison.
    rule_test_pred = _evaluate_rule_engine(test_df[args.text_col])
    rule_test_report = _report_dict(test_df[args.label_col], pd.Series(rule_test_pred), labels)
    _save_confusion_matrix(
        test_df[args.label_col],
        pd.Series(rule_test_pred),
        labels,
        out_dir / "rule_test_confusion_matrix.csv",
    )

    # 6) Save structured outputs.
    (out_dir / "split_summary.json").write_text(
        json.dumps(
            {
                "rows_total": int(len(df)),
                "rows_train": int(len(train_df)),
                "rows_dev": int(len(dev_df)),
                "rows_test": int(len(test_df)),
                "labels": labels,
                "model": args.model,
                "text_col": args.text_col,
                "label_col": args.label_col,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (out_dir / "ml_dev_classification_report.json").write_text(
        json.dumps(_ensure_jsonable(ml_dev_report), indent=2), encoding="utf-8"
    )
    (out_dir / "ml_test_classification_report.json").write_text(
        json.dumps(_ensure_jsonable(ml_test_report), indent=2), encoding="utf-8"
    )
    (out_dir / "rule_test_classification_report.json").write_text(
        json.dumps(_ensure_jsonable(rule_test_report), indent=2), encoding="utf-8"
    )

    prediction_df = test_df.copy()
    prediction_df["ml_prediction"] = ml_test_pred
    prediction_df["rule_prediction"] = rule_test_pred
    prediction_df.to_csv(out_dir / "test_predictions.csv", index=False)

    # 7) Build compact comparison summary and markdown note.
    ml_accuracy = accuracy_score(test_df[args.label_col], ml_test_pred)
    ml_macro_f1 = f1_score(test_df[args.label_col], ml_test_pred, average="macro")
    rule_accuracy = accuracy_score(test_df[args.label_col], rule_test_pred)
    rule_macro_f1 = f1_score(test_df[args.label_col], rule_test_pred, average="macro")

    comparison_summary = {
        "dataset_rows": int(len(df)),
        "model": args.model,
        "ml": {
            "accuracy": float(ml_accuracy),
            "macro_f1": float(ml_macro_f1),
        },
        "rule": {
            "accuracy": float(rule_accuracy),
            "macro_f1": float(rule_macro_f1),
        },
        "delta_ml_minus_rule": {
            "accuracy": float(ml_accuracy - rule_accuracy),
            "macro_f1": float(ml_macro_f1 - rule_macro_f1),
        },
        "small_data_warning": bool(len(df) < 500),
    }
    (out_dir / "comparison_summary.json").write_text(
        json.dumps(comparison_summary, indent=2),
        encoding="utf-8",
    )

    _write_comparison_note(
        out_path=out_dir / "comparison_note.md",
        model_name=args.model,
        dataset_rows=len(df),
        ml_accuracy=ml_accuracy,
        ml_macro_f1=ml_macro_f1,
        rule_accuracy=rule_accuracy,
        rule_macro_f1=rule_macro_f1,
    )

    print("Baseline experiment completed.")
    print(f"Outputs saved to: {out_dir}")


if __name__ == "__main__":
    main()
