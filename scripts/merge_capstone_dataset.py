"""Merge the team capstone dataset into the MVP canonical data files."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "data" / "dataset_capstone-20260531T010643Z-3-001.zip"
RAW_OUT = ROOT / "data" / "dataset_capstone"
MODULE_DATA = ROOT / "ai_ml_module" / "data"
ROOT_DATA = ROOT / "data"

SKILL_ALIASES = {
    "html": "html_basic",
    "css": "css_basic",
    "javascript": "javascript_basic",
    "js": "javascript_basic",
    "python": "python_basic",
    "sql": "sql_basic",
    "spreadsheet": "spreadsheet_basic",
    "networking": "networking_fundamental",
}

DOMAIN_ALIASES = {
    "web_development": "frontend",
    "data_science": "data",
}

CANONICAL_ROLE_SKILLS = {
    "frontend_developer": {"html_basic", "css_basic", "javascript_basic"},
}

CANONICAL_ROLES = {
    "frontend_developer": "Frontend Developer",
    "backend_developer": "Backend Developer",
    "data_analyst": "Data Analyst",
    "machine_learning_engineer": "Machine Learning Engineer",
    "soc_analyst": "SOC Analyst",
    "ui_ux_designer": "UI/UX Designer",
}


def read_existing(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def read_zip_csv(name: str) -> pd.DataFrame:
    with zipfile.ZipFile(ZIP_PATH) as zf:
        with zf.open(f"dataset_capstone/{name}") as fh:
            return pd.read_csv(fh)


def normalize_skill(value: object) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    return SKILL_ALIASES.get(text, text)


def normalize_domain(value: object) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    return DOMAIN_ALIASES.get(text, text)


def normalize_role_skill(df: pd.DataFrame) -> pd.DataFrame:
    out = df.rename(columns={"role_skill_mapping_final": "role_skill_mapping"}).copy()
    if "domain_interest" in out:
        out["domain_interest"] = out["domain_interest"].map(normalize_domain)
    for col in ("required_skill_id", "prerequisite_skill_id"):
        if col in out:
            out[col] = out[col].map(normalize_skill)
    return out


def normalize_task_bank(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "domain_interest" in out:
        out["domain_interest"] = out["domain_interest"].map(normalize_domain)
    for col in ("target_skill_id", "prerequisite_skill_id"):
        if col in out:
            out[col] = out[col].map(normalize_skill)
    return out


def infer_question_skill(question_id: object, answer_map: pd.DataFrame) -> str:
    rows = answer_map[answer_map["question_id"].astype(str) == str(question_id)]
    if rows.empty:
        return ""
    rows = rows.copy()
    rows["skill_score"] = pd.to_numeric(rows.get("skill_score", 0), errors="coerce").fillna(0)
    best = rows.sort_values("skill_score", ascending=False).iloc[0]
    return normalize_skill(best.get("skill_id", ""))


def normalize_question_bank(df: pd.DataFrame, answer_map: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "domain_interest" in out:
        out["domain_interest"] = out["domain_interest"].map(normalize_domain)
    if "question" in out and "prompt" not in out:
        out["prompt"] = out["question"]
    if "current_level" in out and "difficulty" not in out:
        out["difficulty"] = out["current_level"]
    out["skill_id"] = out["question_id"].map(lambda qid: infer_question_skill(qid, answer_map))
    if "expected_keywords" not in out:
        out["expected_keywords"] = out.get("options", "").fillna("").astype(str).str.replace("|", "|", regex=False)
    return out


def normalize_answer_map(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "skill_id" in out:
        out["skill_id"] = out["skill_id"].map(normalize_skill)
    if "answer_value" in out:
        out = out[out["answer_value"].notna() & (out["answer_value"].astype(str).str.strip() != "")]
    return out


def concat_dedupe(first: pd.DataFrame, second: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    merged = pd.concat([first, second], ignore_index=True, sort=False)
    existing_subset = [col for col in subset if col in merged.columns]
    if existing_subset:
        merged = merged.drop_duplicates(subset=existing_subset, keep="first")
    return merged


def keep_canonical_role_contracts(df: pd.DataFrame) -> pd.DataFrame:
    """Keep MVP demo roles stable while allowing new capstone roles to be added."""
    if df.empty or "role_id" not in df or "required_skill_id" not in df:
        return df

    keep = df["role_id"].astype(str).isin(CANONICAL_ROLES)

    for role_id, skills in CANONICAL_ROLE_SKILLS.items():
        mask = (df["role_id"].astype(str) == role_id) & df["required_skill_id"].astype(str).isin(skills)
        keep = (keep & (df["role_id"].astype(str) != role_id)) | mask

    out = df[keep].copy()
    out["role_name"] = out["role_id"].map(CANONICAL_ROLES).fillna(out["role_name"])
    return out.drop_duplicates(subset=["role_id", "required_skill_id"], keep="first")


def skill_name(skill_id: str) -> str:
    return str(skill_id).replace("_", " ").title()


def ensure_task_role_skills(role_df: pd.DataFrame, task_df: pd.DataFrame) -> pd.DataFrame:
    if task_df.empty:
        return role_df

    existing = set()
    if not role_df.empty:
        existing = set(zip(role_df["role_id"].astype(str), role_df["required_skill_id"].astype(str)))

    additions = []
    grouped = task_df[task_df["target_role"].astype(str).isin(CANONICAL_ROLES)].groupby("target_role")
    for role_id, rows in grouped:
        current_role_rows = role_df[role_df["role_id"].astype(str) == str(role_id)] if not role_df.empty else pd.DataFrame()
        next_order = len(current_role_rows) + 1
        for _, row in rows.iterrows():
            target_skill = normalize_skill(row.get("target_skill_id", ""))
            if not target_skill or (str(role_id), target_skill) in existing:
                continue
            additions.append({
                "role_id": str(role_id),
                "role_name": CANONICAL_ROLES[str(role_id)],
                "domain_interest": normalize_domain(row.get("domain_interest", "")),
                "required_skill_id": target_skill,
                "required_skill_name": skill_name(target_skill),
                "skill_category": "core",
                "priority": "high",
                "minimum_level": row.get("current_level") or "basic",
                "step_order": next_order,
                "prerequisite_skill_id": normalize_skill(row.get("prerequisite_skill_id", "")),
            })
            existing.add((str(role_id), target_skill))
            next_order += 1

    if additions:
        role_df = pd.concat([role_df, pd.DataFrame(additions)], ignore_index=True, sort=False)
    return role_df.drop_duplicates(subset=["role_id", "required_skill_id"], keep="first")


def clean_pretext_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.rename(columns={col: str(col).strip() for col in df.columns}).copy()
    unnamed = [col for col in out.columns if str(col).startswith("Unnamed:") or str(col) == ""]
    return out.drop(columns=unnamed, errors="ignore")


def write_csv(df: pd.DataFrame, *paths: Path) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)


def build_label_taxonomy() -> dict[str, list[str]]:
    base = {}
    label_path = MODULE_DATA / "label_taxonomy.json"
    if label_path.exists():
        base = json.loads(label_path.read_text(encoding="utf-8"))

    role_df = read_existing(MODULE_DATA / "role_skill_mapping.csv")
    task_df = read_existing(MODULE_DATA / "task_bank.csv")
    question_df = read_existing(MODULE_DATA / "question_bank.csv")
    pretext_df = read_existing(MODULE_DATA / "dataset_pretext.csv")
    persona_df = read_existing(MODULE_DATA / "persona_taxonomy.csv")

    def values(column: str, *frames: pd.DataFrame) -> list[str]:
        found = set()
        for frame in frames:
            if column in frame:
                found.update(str(v).strip() for v in frame[column].dropna().unique() if str(v).strip())
        return sorted(found)

    taxonomy = {
        "intent": sorted(set(base.get("intent", [])) | {"learn_new", "build_portfolio", "switch_career", "validate_direction", "skill_gap", "action_plan", "evaluate_task"}),
        "domain_interest": sorted(set(base.get("domain_interest", [])) | set(values("domain_interest", role_df, task_df, question_df))),
        "target_role": sorted(CANONICAL_ROLES),
        "problem_category": sorted(set(base.get("problem_category", [])) | set(values("problem_category", pretext_df))),
        "current_level": sorted(set(base.get("current_level", [])) | set(values("current_level", task_df, question_df, pretext_df))),
        "blocker_type": sorted(set(base.get("blocker_type", [])) | set(values("blocker_type", question_df, pretext_df))),
        "persona_type": sorted(set(base.get("persona_type", [])) | set(values("persona_type", persona_df))),
    }

    for blocker in taxonomy["blocker_type"]:
        if blocker != "none":
            taxonomy["problem_category"].append(f"{blocker}_issue")
    for domain in taxonomy["domain_interest"]:
        taxonomy["problem_category"].append(f"{domain}_task")

    taxonomy["problem_category"] = sorted(set(taxonomy["problem_category"]))
    return taxonomy


def extract_raw_zip() -> None:
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue
            name = Path(member).name
            target = RAW_OUT / name
            target.write_bytes(zf.read(member))


def main() -> None:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Zip dataset not found: {ZIP_PATH}")

    extract_raw_zip()

    answer_zip = normalize_answer_map(read_zip_csv("answer_skill_mapping.csv"))
    question_zip = normalize_question_bank(read_zip_csv("question_bank.csv"), answer_zip)
    role_zip = normalize_role_skill(read_zip_csv("role_skill_mapping_final.csv"))
    task_zip = normalize_task_bank(read_zip_csv("task_bank.csv"))
    pretext_zip = clean_pretext_columns(read_zip_csv("dataset_pretext.csv"))
    persona_zip = read_zip_csv("persona_taxonomy.csv")

    role = concat_dedupe(read_existing(MODULE_DATA / "role_skill_mapping.csv"), role_zip, ["role_id", "required_skill_id"])
    role = keep_canonical_role_contracts(role)
    tasks = concat_dedupe(read_existing(MODULE_DATA / "task_bank.csv"), task_zip, ["task_id"])
    role = ensure_task_role_skills(role, tasks)
    questions = concat_dedupe(read_existing(MODULE_DATA / "question_bank.csv"), question_zip, ["question_id"])
    answers = concat_dedupe(read_existing(MODULE_DATA / "answer_skill_mapping.csv"), answer_zip, ["question_id", "answer_value", "skill_id"])
    answers = normalize_answer_map(answers)

    write_csv(role, MODULE_DATA / "role_skill_mapping.csv", ROOT_DATA / "role_skill_mapping.csv")
    write_csv(tasks, MODULE_DATA / "task_bank.csv", ROOT_DATA / "task_bank.csv")
    write_csv(questions, MODULE_DATA / "question_bank.csv")
    write_csv(answers, MODULE_DATA / "answer_skill_mapping.csv")
    write_csv(pretext_zip, MODULE_DATA / "dataset_pretext.csv", ROOT_DATA / "labels" / "dataset_pretext.csv")
    write_csv(persona_zip, MODULE_DATA / "persona_taxonomy_raw.csv")

    taxonomy = build_label_taxonomy()
    for path in (MODULE_DATA / "label_taxonomy.json", ROOT_DATA / "label_taxonomy.json"):
        path.write_text(json.dumps(taxonomy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Merged capstone dataset")
    print(f"role_skill_mapping rows: {len(role)}")
    print(f"task_bank rows: {len(tasks)}")
    print(f"question_bank rows: {len(questions)}")
    print(f"answer_skill_mapping rows: {len(answers)}")
    print(f"dataset_pretext rows: {len(pretext_zip)}")


if __name__ == "__main__":
    main()
