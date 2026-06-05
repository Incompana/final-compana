"""Alignment Validation Script.

Checks dataset contracts and pipeline output against Tugas AI/ML and Tugas Data Science.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Set

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUT_DIR.mkdir(exist_ok=True)


class AlignmentValidator:
    def __init__(self):
        self.checks: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_label_taxonomy(self) -> Dict[str, List[str]]:
        p = DATA_DIR / "label_taxonomy.json"
        if not p.exists():
            self.errors.append(f"label_taxonomy.json not found at {p}")
            return {}
        try:
            data = json.loads(p.read_text())
            return data
        except Exception as e:
            self.errors.append(f"Failed to load label_taxonomy.json: {e}")
            return {}

    def load_role_skill_mapping(self) -> pd.DataFrame:
        p = DATA_DIR / "role_skill_mapping.csv"
        if not p.exists():
            self.errors.append(f"role_skill_mapping.csv not found at {p}")
            return pd.DataFrame()
        try:
            return pd.read_csv(p)
        except Exception as e:
            self.errors.append(f"Failed to load role_skill_mapping.csv: {e}")
            return pd.DataFrame()

    def load_task_bank(self) -> pd.DataFrame:
        p = DATA_DIR / "task_bank.csv"
        if not p.exists():
            self.errors.append(f"task_bank.csv not found at {p}")
            return pd.DataFrame()
        try:
            return pd.read_csv(p)
        except Exception as e:
            self.errors.append(f"Failed to load task_bank.csv: {e}")
            return pd.DataFrame()

    def load_rubric_feedback_bank(self) -> pd.DataFrame:
        p = DATA_DIR / "rubric_feedback_bank.csv"
        if not p.exists():
            self.errors.append(f"rubric_feedback_bank.csv not found at {p}")
            return pd.DataFrame()
        try:
            return pd.read_csv(p)
        except Exception as e:
            self.errors.append(f"Failed to load rubric_feedback_bank.csv: {e}")
            return pd.DataFrame()

    def load_pipeline_output(self) -> Dict[str, Any]:
        # Check both outputs/ and ai_ml_module/outputs/
        possible_paths = [
            Path("ai_ml_module/outputs/full_pipeline_demo_result.json"),
            Path("outputs/full_pipeline_demo_result.json"),
        ]
        for p in possible_paths:
            if p.exists():
                try:
                    return json.loads(p.read_text())
                except Exception as e:
                    self.errors.append(f"Failed to load full_pipeline_demo_result.json: {e}")
                    return {}
        self.warnings.append(f"full_pipeline_demo_result.json not found in {possible_paths}")
        return {}

    def check_1_output_target_role_in_taxonomy(self, output: Dict[str, Any], taxonomy: Dict[str, List[str]]) -> None:
        """Check: All target_role in output are in label_taxonomy.json."""
        if not output or not taxonomy:
            return

        valid_roles = taxonomy.get("target_role", [])
        target_role = output.get("pretext_analysis", {}).get("target_role")

        if target_role and target_role not in valid_roles:
            self.errors.append(f"target_role '{target_role}' not in label_taxonomy target_roles: {valid_roles}")
        else:
            self.checks.append({"check": "1. Output target_role in taxonomy", "status": "PASS"})

    def check_2_output_current_level_valid(self, output: Dict[str, Any], taxonomy: Dict[str, List[str]]) -> None:
        """Check: All current_level valid."""
        if not output or not taxonomy:
            return

        valid_levels = taxonomy.get("current_level", [])
        current_level = output.get("pretext_analysis", {}).get("current_level")

        if current_level and current_level not in valid_levels:
            self.errors.append(f"current_level '{current_level}' not in valid levels: {valid_levels}")
        else:
            self.checks.append({"check": "2. Output current_level valid", "status": "PASS"})

    def check_3_output_problem_category_valid(self, output: Dict[str, Any], taxonomy: Dict[str, List[str]]) -> None:
        """Check: All problem_category valid."""
        if not output or not taxonomy:
            return

        valid_categories = taxonomy.get("problem_category", [])
        problem_category = output.get("pretext_analysis", {}).get("problem_category")

        if problem_category and problem_category not in valid_categories:
            self.errors.append(f"problem_category '{problem_category}' not in valid categories: {valid_categories}")
        else:
            self.checks.append({"check": "3. Output problem_category valid", "status": "PASS"})

    def check_4_output_blocker_type_valid(self, output: Dict[str, Any], taxonomy: Dict[str, List[str]]) -> None:
        """Check: All blocker_type valid."""
        if not output or not taxonomy:
            return

        valid_blockers = taxonomy.get("blocker_type", [])
        blocker_type = output.get("pretext_analysis", {}).get("blocker_type")

        if blocker_type and blocker_type not in valid_blockers:
            self.errors.append(f"blocker_type '{blocker_type}' not in valid blockers: {valid_blockers}")
        else:
            self.checks.append({"check": "4. Output blocker_type valid", "status": "PASS"})

    def check_5_output_persona_type_valid(self, output: Dict[str, Any], taxonomy: Dict[str, List[str]]) -> None:
        """Check: All persona_type valid."""
        if not output or not taxonomy:
            return

        valid_personas = taxonomy.get("persona_type", [])
        persona_type = output.get("pretext_analysis", {}).get("persona_type")

        if persona_type and persona_type not in valid_personas:
            self.errors.append(f"persona_type '{persona_type}' not in valid personas: {valid_personas}")
        else:
            self.checks.append({"check": "5. Output persona_type valid", "status": "PASS"})

    def check_6_role_skill_mapping_valid(self, role_skill_df: pd.DataFrame, taxonomy: Dict[str, List[str]]) -> None:
        """Check: All role_id in role_skill_mapping.csv valid."""
        if role_skill_df.empty or not taxonomy:
            return

        valid_roles = taxonomy.get("target_role", [])
        role_ids = set(role_skill_df["role_id"].astype(str).unique())

        invalid_roles = [r for r in role_ids if r not in valid_roles]
        if invalid_roles:
            self.errors.append(f"Invalid role_ids in role_skill_mapping: {invalid_roles}")
        else:
            self.checks.append({"check": "6. role_skill_mapping role_ids valid", "status": "PASS"})

    def check_7_task_bank_target_role_in_taxonomy(self, task_bank_df: pd.DataFrame, taxonomy: Dict[str, List[str]]) -> None:
        """Check: All target_role in task_bank.csv are in label_taxonomy.json."""
        if task_bank_df.empty or not taxonomy:
            return

        valid_roles = taxonomy.get("target_role", [])
        if "target_role" in task_bank_df.columns:
            task_roles = set(task_bank_df["target_role"].astype(str).unique())
            invalid_roles = [r for r in task_roles if r not in valid_roles]
            if invalid_roles:
                self.errors.append(f"Invalid target_roles in task_bank: {invalid_roles}")
            else:
                self.checks.append({"check": "7. task_bank target_roles in taxonomy", "status": "PASS"})
        else:
            self.warnings.append("task_bank.csv missing 'target_role' column")

    def check_8_rubric_task_ids_in_task_bank(self, rubric_df: pd.DataFrame, task_bank_df: pd.DataFrame) -> None:
        """Check: All task_id in rubric_feedback_bank.csv are in task_bank.csv."""
        if rubric_df.empty or task_bank_df.empty:
            return

        rubric_task_ids = set()
        task_bank_task_ids = set()

        if "task_id" in rubric_df.columns:
            rubric_task_ids = set(rubric_df["task_id"].astype(str).unique())
        if "task_id" in task_bank_df.columns:
            task_bank_task_ids = set(task_bank_df["task_id"].astype(str).unique())

        missing_tasks = rubric_task_ids - task_bank_task_ids
        if missing_tasks:
            self.errors.append(f"task_ids in rubric not in task_bank: {missing_tasks}")
        else:
            self.checks.append({"check": "8. rubric task_ids in task_bank", "status": "PASS"})

    def check_9_priority_valid(self, role_skill_df: pd.DataFrame) -> None:
        """Check: All priority only high, medium, low."""
        if role_skill_df.empty:
            return

        valid_priorities = {"high", "medium", "low"}
        if "priority" in role_skill_df.columns:
            priorities = set(role_skill_df["priority"].astype(str).str.lower().unique())
            invalid_priorities = priorities - valid_priorities
            if invalid_priorities:
                self.errors.append(f"Invalid priority values: {invalid_priorities}")
            else:
                self.checks.append({"check": "9. All priority values valid", "status": "PASS"})
        else:
            self.warnings.append("role_skill_mapping.csv missing 'priority' column")

    def check_10_engine_5_8_output_contract(self, output: Dict[str, Any]) -> None:
        """Check: All task output follows contract Engine 5-8."""
        if not output:
            return

        checks_passed = []

        # Engine 5 contract
        gap = output.get("skill_gap", {})
        gap_required = ["target_role", "skill_gap_summary", "missing_skills", "weak_skills", "owned_skills", "readiness_score", "priority_gap"]
        gap_ok = all(k in gap for k in gap_required)
        if gap_ok:
            checks_passed.append("Engine 5 contract")
        else:
            missing = [k for k in gap_required if k not in gap]
            self.errors.append(f"Engine 5 missing contract fields: {missing}")

        # Engine 6 contract
        plan = output.get("action_plan", {})
        if "recommended_tasks" in plan:
            checks_passed.append("Engine 6 contract")
        else:
            self.errors.append("Engine 6 missing 'recommended_tasks'")

        # Engine 7 contract
        eval_res = output.get("evaluation", {})
        eval_required = ["task_id", "score", "status", "feedback", "validated_skill"]
        eval_ok = all(k in eval_res for k in eval_required)
        if eval_ok:
            checks_passed.append("Engine 7 contract")
        else:
            missing = [k for k in eval_required if k not in eval_res]
            self.errors.append(f"Engine 7 missing contract fields: {missing}")

        # Engine 8 contract
        prog = output.get("progress", {})
        if "dashboard" in prog:
            dashboard = prog["dashboard"]
            dashboard_required = ["current_path", "current_level", "readiness_score", "completed_tasks", "average_score", "validated_skills", "weak_skills", "next_action"]
            dashboard_ok = all(k in dashboard for k in dashboard_required)
            if dashboard_ok:
                checks_passed.append("Engine 8 contract")
            else:
                missing = [k for k in dashboard_required if k not in dashboard]
                self.errors.append(f"Engine 8 dashboard missing fields: {missing}")
        else:
            self.errors.append("Engine 8 missing 'dashboard'")

        if checks_passed:
            self.checks.append({"check": f"10. Engine 5-8 contracts: {', '.join(checks_passed)}", "status": "PASS"})

    def run_all_checks(self) -> None:
        taxonomy = self.load_label_taxonomy()
        role_skill_df = self.load_role_skill_mapping()
        task_bank_df = self.load_task_bank()
        rubric_df = self.load_rubric_feedback_bank()
        output = self.load_pipeline_output()

        self.check_1_output_target_role_in_taxonomy(output, taxonomy)
        self.check_2_output_current_level_valid(output, taxonomy)
        self.check_3_output_problem_category_valid(output, taxonomy)
        self.check_4_output_blocker_type_valid(output, taxonomy)
        self.check_5_output_persona_type_valid(output, taxonomy)
        self.check_6_role_skill_mapping_valid(role_skill_df, taxonomy)
        self.check_7_task_bank_target_role_in_taxonomy(task_bank_df, taxonomy)
        self.check_8_rubric_task_ids_in_task_bank(rubric_df, task_bank_df)
        self.check_9_priority_valid(role_skill_df)
        self.check_10_engine_5_8_output_contract(output)

    def generate_report(self) -> str:
        lines = []
        lines.append("# Alignment Validation Report\n")
        lines.append(f"## Summary\n")
        lines.append(f"- Total checks: {len(self.checks)}")
        lines.append(f"- Errors: {len(self.errors)}")
        lines.append(f"- Warnings: {len(self.warnings)}\n")

        lines.append("## Dataset Files\n")
        for f in [DATA_DIR / "label_taxonomy.json", DATA_DIR / "role_skill_mapping.csv", DATA_DIR / "task_bank.csv", DATA_DIR / "rubric_feedback_bank.csv"]:
            status = "✓" if f.exists() else "✗"
            lines.append(f"- {status} {f.name}")
        lines.append("")

        lines.append("## Checks\n")
        for check in self.checks:
            lines.append(f"- ✓ {check['check']}")
        lines.append("")

        if self.errors:
            lines.append("## Errors\n")
            for error in self.errors:
                lines.append(f"- ✗ {error}")
            lines.append("")

        if self.warnings:
            lines.append("## Warnings\n")
            for warning in self.warnings:
                lines.append(f"- ⚠ {warning}")
            lines.append("")

        lines.append("## Status\n")
        if self.errors:
            lines.append("**FAILED** — validation has errors.")
        else:
            lines.append("**PASSED** — all validation checks successful.")

        return "\n".join(lines)


def main():
    validator = AlignmentValidator()
    validator.run_all_checks()
    report = validator.generate_report()

    report_path = OUT_DIR / "alignment_report.md"
    report_path.write_text(report)

    print(report)
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
