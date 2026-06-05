from __future__ import annotations

import json
from pathlib import Path

from src.rule_engine.pretext import analyze_pretext

BASE_DIR = Path(__file__).resolve().parents[2]
SCENARIO_FILE = BASE_DIR / "data" / "labels" / "scenario_cases.json"


def run_scenarios() -> list[dict]:
    with SCENARIO_FILE.open("r", encoding="utf-8") as file:
        scenarios = json.load(file)

    rows: list[dict] = []
    for item in scenarios:
        classification, _, _, _, _, _ = analyze_pretext(item["text"])
        rows.append(
            {
                "id": item["id"],
                "expected_problem_category": item["expected_problem_category"],
                "predicted_problem_category": classification.problem_category.value,
                "fallback_triggered": classification.fallback_triggered,
            }
        )
    return rows
