"""Validate dataset files and produce a markdown report.

Checks performed:
- Tidak ada role di luar 4 role MVP
- Tidak ada skill_id kosong
- Tidak ada task tanpa role_id (inferred)
- Tidak ada rubric tanpa task_id (must reference task)
- Tidak ada duplicate task_id
- Semua task punya minimal 3 rubric criteria
- Semua role punya minimal 10 skill
- Semua role punya minimal 5 task

Output: outputs/dataset_validation_report.md
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[2]
RAW_JSONL = ROOT / "data" / "raw" / "job_postings_raw.jsonl"
ROLE_SKILL_CSV = ROOT / "data" / "processed" / "role_skill_mapping.csv"
SKILL_ALIASES_CSV = ROOT / "data" / "processed" / "skill_aliases.csv"
TASK_BANK_CSV = ROOT / "data" / "processed" / "task_bank.csv"
RUBRIC_BANK_CSV = ROOT / "data" / "processed" / "rubric_bank.csv"
REPORT_MD = ROOT / "outputs" / "dataset_validation_report.md"

ALLOWED_ROLES = {"frontend_developer", "backend_developer", "cyber_security_analyst", "data_analyst"}


def read_jsonl(path: Path) -> List[Dict]:
    out = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def infer_task_role(task_row: Dict, role_skill_map: Dict[str, List[str]], skill_name_to_roles: Dict[str, List[str]]) -> List[str]:
    # task_row: expects 'keahlian_terkait' column with semicolon separated names
    k = task_row.get("keahlian_terkait") or task_row.get("keahlian") or ""
    names = [x.strip().lower() for x in str(k).split(";") if x.strip()]
    roles_found = {}
    for name in names:
        # direct match to skill_name_to_roles
        if name in skill_name_to_roles:
            for r in skill_name_to_roles[name]:
                roles_found[r] = roles_found.get(r, 0) + 1
    # return roles sorted by match count
    return sorted(roles_found.keys(), key=lambda x: -roles_found[x])


def count_rubric_criteria(kriteria_field: str) -> int:
    if not kriteria_field or pd.isna(kriteria_field):
        return 0
    parts = [p.strip() for p in str(kriteria_field).split(";") if p.strip()]
    return len(parts)


def validate() -> Tuple[str, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    raw = read_jsonl(RAW_JSONL)
    df_role_skill = load_csv(ROLE_SKILL_CSV)
    df_skill_alias = load_csv(SKILL_ALIASES_CSV)
    df_tasks = load_csv(TASK_BANK_CSV)
    df_rubric = load_csv(RUBRIC_BANK_CSV)

    # counts
    counts = {
        "job_postings_raw.jsonl": len(raw),
        "role_skill_mapping.csv": len(df_role_skill) if not df_role_skill.empty else 0,
        "skill_aliases.csv": len(df_skill_alias) if not df_skill_alias.empty else 0,
        "task_bank.csv": len(df_tasks) if not df_tasks.empty else 0,
        "rubric_bank.csv": len(df_rubric) if not df_rubric.empty else 0,
    }

    # roles validation
    roles_in_file = set()
    if not df_role_skill.empty and "peran" in df_role_skill.columns:
        roles_in_file = set(df_role_skill["peran"].dropna().unique().tolist())
    # check roles outside allowed
    extra_roles = roles_in_file - ALLOWED_ROLES
    if extra_roles:
        errors.append(f"Ditemukan role di luar MVP: {', '.join(sorted(extra_roles))}")

    # skill_id empty check
    if not df_role_skill.empty:
        if "skill_id" in df_role_skill.columns:
            empty_skill_id = df_role_skill[df_role_skill["skill_id"].isna() | (df_role_skill["skill_id"].astype(str).str.strip() == "")]
            if len(empty_skill_id) > 0:
                errors.append(f"Ditemukan {len(empty_skill_id)} baris di role_skill_mapping dengan skill_id kosong")
        else:
            errors.append("Kolom 'skill_id' tidak ditemukan di role_skill_mapping.csv")

    if not df_skill_alias.empty:
        if "skill_id" in df_skill_alias.columns:
            empty_skill_id_alias = df_skill_alias[df_skill_alias["skill_id"].isna() | (df_skill_alias["skill_id"].astype(str).str.strip() == "")]
            if len(empty_skill_id_alias) > 0:
                errors.append(f"Ditemukan {len(empty_skill_id_alias)} baris di skill_aliases dengan skill_id kosong")
        else:
            warnings.append("Kolom 'skill_id' tidak ditemukan di skill_aliases.csv")

    # skill counts per role
    skill_counts = {}
    if not df_role_skill.empty and "peran" in df_role_skill.columns:
        for r in ALLOWED_ROLES:
            if "skill_id" in df_role_skill.columns:
                skill_counts[r] = df_role_skill[df_role_skill["peran"] == r]["skill_id"].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique()
            else:
                skill_counts[r] = df_role_skill[df_role_skill["peran"] == r].shape[0]
            if skill_counts[r] < 10:
                warnings.append(f"Role '{r}' hanya memiliki {skill_counts[r]} skill (<10)")

    # prepare skill name -> roles mapping from role_skill and skill_aliases
    skill_name_to_roles: Dict[str, List[str]] = {}
    if not df_role_skill.empty:
        # use 'keahlian' column if exists
        name_col = "keahlian" if "keahlian" in df_role_skill.columns else ("skill_name" if "skill_name" in df_role_skill.columns else None)
        for _, row in df_role_skill.iterrows():
            role = row.get("peran")
            name = None
            if name_col:
                name = str(row.get(name_col) or "").strip().lower()
            sid = str(row.get("skill_id") or "").strip().lower()
            if name:
                skill_name_to_roles.setdefault(name, []).append(role)
            if sid:
                skill_name_to_roles.setdefault(sid, []).append(role)

    # include aliases
    if not df_skill_alias.empty:
        # columns: keahlian, skill_id, aliases
        for _, row in df_skill_alias.iterrows():
            aliases = str(row.get("aliases") or "")
            sid = str(row.get("skill_id") or "").strip().lower()
            for a in [x.strip().lower() for x in aliases.split(";") if x.strip()]:
                if sid:
                    # map alias to roles via skill_id if available
                    # find roles that include this skill_id
                    roles_for_sid = df_role_skill[df_role_skill["skill_id"].astype(str).str.lower() == sid]["peran"].dropna().unique().tolist() if (not df_role_skill.empty and "skill_id" in df_role_skill.columns) else []
                    for r in roles_for_sid:
                        skill_name_to_roles.setdefault(a, []).append(r)
                else:
                    # fallback: map alias to keahlian name
                    skill_name_to_roles.setdefault(a, []).append("unknown")

    # tasks per role inference
    task_counts = {r: 0 for r in ALLOWED_ROLES}
    task_without_role = []
    if not df_tasks.empty:
        if "id_tugas" not in df_tasks.columns:
            errors.append("Kolom 'id_tugas' tidak ditemukan di task_bank.csv")
        else:
            # duplicate task_id
            dup = df_tasks[df_tasks["id_tugas"].duplicated(keep=False)]
            if not dup.empty:
                errors.append(f"Ditemukan duplicate task_id: {dup['id_tugas'].unique().tolist()}")

        for _, row in df_tasks.iterrows():
            inferred = infer_task_role(row, {}, skill_name_to_roles)
            if not inferred:
                task_without_role.append(row.get("id_tugas") or row.get("judul") or "(tanpa id)")
            else:
                # assign first inferred
                primary = inferred[0]
                if primary in task_counts:
                    task_counts[primary] += 1
    # check tasks per role
    for r in ALLOWED_ROLES:
        if task_counts.get(r, 0) < 5:
            warnings.append(f"Role '{r}' hanya memiliki {task_counts.get(r,0)} task (<5)")

    if task_without_role:
        errors.append(f"Ditemukan {len(task_without_role)} task yang tidak dapat di-infer ke role: {task_without_role[:10]}")

    # rubric checks
    if df_rubric.empty:
        warnings.append("Rubric bank kosong atau tidak ditemukan")
    else:
        # check if rubric references task id via a column
        task_ref_cols = [c for c in df_rubric.columns if c.lower() in ("task_id", "id_tugas", "taskid")] 
        if not task_ref_cols:
            errors.append("Rubric tidak memiliki kolom referensi ke tugas (task_id / id_tugas)")
        else:
            # group rubrics by task id and count criteria
            ref_col = task_ref_cols[0]
            grouped = df_rubric.groupby(ref_col)
            for task_id, grp in grouped:
                # aggregate criteria field (kriteria)
                total_criteria = 0
                for _, r in grp.iterrows():
                    total_criteria += count_rubric_criteria(r.get("kriteria") or r.get("criteria") or "")
                if total_criteria < 3:
                    errors.append(f"Task {task_id} memiliki kurang dari 3 kriteria rubrik ({total_criteria})")

    # build report markdown
    lines = []
    lines.append("# Dataset Validation Report\n")
    lines.append("## Ringkasan jumlah baris per file\n")
    for k, v in counts.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("\n")

    lines.append("## Roles\n")
    lines.append(f"- Jumlah role unik pada role_skill_mapping: {len(roles_in_file)}")
    lines.append(f"- Role yang terdeteksi: {', '.join(sorted(roles_in_file)) if roles_in_file else 'Tidak ada'}\n")

    lines.append("## Skill per role\n")
    for r in sorted(ALLOWED_ROLES):
        lines.append(f"- {r}: {skill_counts.get(r,0)} skill")
    lines.append("\n")

    lines.append("## Task per role (inferred)\n")
    for r in sorted(ALLOWED_ROLES):
        lines.append(f"- {r}: {task_counts.get(r,0)} task")
    lines.append("\n")

    lines.append("## Errors\n")
    if errors:
        for e in errors:
            lines.append(f"- ERROR: {e}")
    else:
        lines.append("- Tidak ada error ditemukan.")
    lines.append("\n")

    lines.append("## Warnings\n")
    if warnings:
        for w in warnings:
            lines.append(f"- WARNING: {w}")
    else:
        lines.append("- Tidak ada warning.")
    lines.append("\n")

    return "\n".join(lines), errors, warnings


def main():
    report_text, errors, warnings = validate()
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(report_text, encoding="utf-8")
    logging.info(f"Validation report ditulis ke {REPORT_MD}")
    if errors:
        logging.error(f"Ditemukan {len(errors)} error. Lihat report untuk detail.")
    else:
        logging.info("Tidak ada error kritis yang ditemukan.")


if __name__ == "__main__":
    main()
