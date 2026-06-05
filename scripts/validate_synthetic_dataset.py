from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = [
    "pretext_text",
    "target_role",
    "problem_category",
    "current_level",
    "blocker_type",
]

EMOTION_MARKERS = ["cemas", "panik", "takut", "overthinking", "down", "minder"]
MESSY_MARKERS = ["tp", "muter2", "nggak tau", "ga tau", "ngga", "btw"]


def validate_rows(rows: list[dict], taxonomy: dict, expected_count: int) -> list[str]:
    errors: list[str] = []

    if len(rows) != expected_count:
        errors.append(f"Row count must be {expected_count}, found {len(rows)}")

    for idx, row in enumerate(rows, start=2):
        for column in REQUIRED_COLUMNS:
            value = (row.get(column) or "").strip()
            if not value:
                errors.append(f"Row {idx}: '{column}' is empty")

        for field in ["target_role", "problem_category", "current_level", "blocker_type"]:
            value = (row.get(field) or "").strip()
            allowed = taxonomy.get(field, [])
            if value not in allowed:
                errors.append(f"Row {idx}: invalid {field}='{value}'")

    return errors


def summarize(rows: list[dict]) -> dict:
    summary: dict[str, Counter] = {
        "target_role": Counter(),
        "problem_category": Counter(),
        "current_level": Counter(),
        "blocker_type": Counter(),
    }

    short_count = 0
    medium_count = 0
    long_count = 0
    messy_count = 0
    emotion_count = 0

    for row in rows:
        for field in summary:
            summary[field][row[field]] += 1

        text = row["pretext_text"].lower().strip()
        word_count = len(text.split())
        if word_count <= 10:
            short_count += 1
        elif word_count <= 28:
            medium_count += 1
        else:
            long_count += 1

        if any(marker in text for marker in MESSY_MARKERS):
            messy_count += 1
        if any(marker in text for marker in EMOTION_MARKERS):
            emotion_count += 1

    return {
        "label_counts": summary,
        "style_counts": {
            "short_words_le_10": short_count,
            "medium_words_11_28": medium_count,
            "long_words_gt_28": long_count,
            "contains_messy_markers": messy_count,
            "contains_emotion_markers": emotion_count,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Compana synthetic pretext dataset")
    parser.add_argument(
        "--csv",
        default="data/labels/compana_synthetic_pretext_id_v1.csv",
        help="Path to CSV dataset",
    )
    parser.add_argument(
        "--taxonomy",
        default="configs/taxonomy.json",
        help="Path to taxonomy JSON",
    )
    parser.add_argument("--expected-count", type=int, default=120)
    args = parser.parse_args()

    csv_path = Path(args.csv)
    tax_path = Path(args.taxonomy)

    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}")
        return 1
    if not tax_path.exists():
        print(f"ERROR: taxonomy file not found: {tax_path}")
        return 1

    taxonomy = json.loads(tax_path.read_text(encoding="utf-8"))

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []

        missing_cols = [column for column in REQUIRED_COLUMNS if column not in columns]
        if missing_cols:
            print(f"ERROR: Missing required columns: {missing_cols}")
            return 1

        rows = list(reader)

    errors = validate_rows(rows, taxonomy, args.expected_count)
    if errors:
        print("VALIDATION FAILED")
        for error in errors[:30]:
            print(f"- {error}")
        if len(errors) > 30:
            print(f"... and {len(errors) - 30} more errors")
        return 1

    result = summarize(rows)
    print("VALIDATION PASSED")
    print(f"Rows: {len(rows)}")

    print("\nLabel distribution:")
    for field, counts in result["label_counts"].items():
        print(f"- {field}:")
        for label, count in sorted(counts.items()):
            print(f"  - {label}: {count}")

    print("\nStyle indicators:")
    for key, count in result["style_counts"].items():
        print(f"- {key}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
