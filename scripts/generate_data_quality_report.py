"""Generate a data quality report for the AI/ML module datasets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "ai_ml_module" / "data"
OUT_DIR = ROOT / "outputs"
REPORT_MD = OUT_DIR / "data_quality_report.md"
REPORT_JSON = OUT_DIR / "data_quality_report.json"


def read_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def records(df: pd.DataFrame, limit: int = 25) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return df.head(limit).fillna("").to_dict(orient="records")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    role = read_csv("role_skill_mapping.csv")
    task = read_csv("task_bank.csv")
    rubric = read_csv("rubric_feedback_bank.csv")
    question = read_csv("question_bank.csv")
    answer = read_csv("answer_skill_mapping.csv")

    duplicate_role_skill = pd.DataFrame()
    duplicate_role_names = pd.DataFrame()
    if not role.empty:
        duplicate_role_skill = role[
            role.duplicated(["role_id", "required_skill_id"], keep=False)
        ].sort_values(["role_id", "required_skill_id"])
        duplicate_role_names = (
            role.groupby("role_id")["role_name"]
            .nunique()
            .reset_index(name="role_name_count")
            .query("role_name_count > 1")
            .sort_values("role_name_count", ascending=False)
        )

    task_ids = set(task.get("task_id", pd.Series(dtype=str)).astype(str))
    rubric_task_ids = set(rubric.get("task_id", pd.Series(dtype=str)).astype(str))
    tasks_without_rubric = task[~task["task_id"].astype(str).isin(rubric_task_ids)] if not task.empty else pd.DataFrame()
    rubric_without_task = rubric[~rubric["task_id"].astype(str).isin(task_ids)] if not rubric.empty else pd.DataFrame()

    question_ids = set(question.get("question_id", pd.Series(dtype=str)).astype(str))
    answer_question_ids = set(answer.get("question_id", pd.Series(dtype=str)).astype(str))
    single_choice = question[
        question.get("answer_type", pd.Series(dtype=str)).fillna("").astype(str).str.lower() == "single_choice"
    ] if not question.empty else pd.DataFrame()
    single_choice_without_mapping = single_choice[
        ~single_choice["question_id"].astype(str).isin(answer_question_ids)
    ] if not single_choice.empty else pd.DataFrame()
    answer_without_question = answer[
        ~answer["question_id"].astype(str).isin(question_ids)
    ] if not answer.empty else pd.DataFrame()

    role_skill_pairs = set()
    if not role.empty:
        role_skill_pairs = set(zip(role["role_id"].astype(str), role["required_skill_id"].astype(str)))
    task_skill_without_role = pd.DataFrame()
    if not task.empty:
        mask = [
            (str(row["target_role"]), str(row["target_skill_id"])) not in role_skill_pairs
            for _, row in task.iterrows()
        ]
        task_skill_without_role = task[mask]

    answer_skill_values = pd.Series(dtype=float)
    invalid_answer_scores = pd.DataFrame()
    if not answer.empty and "skill_score" in answer:
        answer_skill_values = pd.to_numeric(answer["skill_score"], errors="coerce")
        invalid_answer_scores = answer[answer_skill_values.isna() | ~answer_skill_values.between(0, 2)]

    summary = {
        "row_counts": {
            "role_skill_mapping": len(role),
            "task_bank": len(task),
            "rubric_feedback_bank": len(rubric),
            "question_bank": len(question),
            "answer_skill_mapping": len(answer),
        },
        "issue_counts": {
            "duplicate_role_skill_rows": len(duplicate_role_skill),
            "role_ids_with_multiple_names": len(duplicate_role_names),
            "tasks_without_rubric": len(tasks_without_rubric),
            "rubric_rows_without_task": len(rubric_without_task),
            "single_choice_questions_without_mapping": len(single_choice_without_mapping),
            "answer_rows_without_question": len(answer_without_question),
            "task_target_skills_not_in_role_mapping": len(task_skill_without_role),
            "invalid_answer_skill_scores": len(invalid_answer_scores),
        },
        "samples": {
            "duplicate_role_skill_rows": records(duplicate_role_skill),
            "role_ids_with_multiple_names": records(duplicate_role_names),
            "tasks_without_rubric": records(tasks_without_rubric),
            "single_choice_questions_without_mapping": records(single_choice_without_mapping),
            "answer_rows_without_question": records(answer_without_question),
            "task_target_skills_not_in_role_mapping": records(task_skill_without_role),
            "invalid_answer_skill_scores": records(invalid_answer_scores),
        },
    }

    REPORT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Data Quality Report",
        "",
        "## Row Counts",
        "",
    ]
    for key, value in summary["row_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Issue Counts", ""])
    for key, value in summary["issue_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Notes", ""])
    lines.append("- `tasks_without_rubric` blocks reliable Engine 7 evaluation for those tasks.")
    lines.append("- `task_target_skills_not_in_role_mapping` means recommended task skills may not affect readiness as expected.")
    lines.append("- `single_choice_questions_without_mapping` should stay at 0 for capstone assessment scoring.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(json.dumps(summary["issue_counts"], indent=2))


if __name__ == "__main__":
    main()
