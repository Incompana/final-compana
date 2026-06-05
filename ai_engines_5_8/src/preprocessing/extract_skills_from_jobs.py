"""Ekstraksi skill dari job postings raw -> role_skill_mapping + skill_aliases

Input: data/raw/job_postings_raw.jsonl
Output:
- data/processed/role_skill_mapping.csv
- data/processed/skill_aliases.csv

Metode: dictionary keyword matching untuk 4 role (tanpa ML).
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO)

# Manual skill dictionary per role
ROLE_SKILLS: Dict[str, List[Dict]] = {
    "frontend_developer": [
        {"id": "js", "name": "JavaScript", "aliases": ["javascript", "js"], "level": "basic"},
        {"id": "react", "name": "React", "aliases": ["react", "react.js", "reactjs"], "level": "intermediate"},
        {"id": "html", "name": "HTML", "aliases": ["html"], "level": "beginner"},
        {"id": "css", "name": "CSS", "aliases": ["css", "scss", "sass"], "level": "beginner"},
        {"id": "vue", "name": "Vue.js", "aliases": ["vue", "vue.js"], "level": "intermediate"},
        {"id": "angular", "name": "Angular", "aliases": ["angular", "angularjs"], "level": "intermediate"}
    ],
    "backend_developer": [
        {"id": "python", "name": "Python", "aliases": ["python"], "level": "basic"},
        {"id": "java", "name": "Java", "aliases": ["java"], "level": "basic"},
        {"id": "node", "name": "Node.js", "aliases": ["node", "nodejs", "node.js"], "level": "intermediate"},
        {"id": "sql", "name": "SQL", "aliases": ["sql", "database"], "level": "basic"},
        {"id": "docker", "name": "Docker", "aliases": ["docker"], "level": "intermediate"}
    ],
    "cyber_security_analyst": [
        {"id": "siem", "name": "SIEM", "aliases": ["siem"], "level": "intermediate"},
        {"id": "linux", "name": "Linux", "aliases": ["linux"], "level": "basic"},
        {"id": "forensic", "name": "Forensic", "aliases": ["forensic", "forensics"], "level": "intermediate"},
        {"id": "pentest", "name": "Penetration Testing", "aliases": ["penetration", "pentest", "penetration testing"], "level": "intermediate"}
    ],
    "data_analyst": [
        {"id": "pandas", "name": "Pandas", "aliases": ["pandas"], "level": "intermediate"},
        {"id": "sql", "name": "SQL", "aliases": ["sql"], "level": "basic"},
        {"id": "tableau", "name": "Tableau", "aliases": ["tableau"], "level": "intermediate"},
        {"id": "powerbi", "name": "Power BI", "aliases": ["powerbi", "power bi"], "level": "intermediate"}
    ]
}


PRIORITY_HIGH_FIELDS = ["title", "skills", "qualifications"]
PRIORITY_MEDIUM_FIELDS = ["description", "responsibilities"]


def read_raw_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        logging.warning(f"File input tidak ditemukan: {path}")
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        # expect obj to have either top-level normalized fields or raw
        # try to extract fields
        record = {}
        # normalized fields if present
        for f in ["title", "company", "description", "qualifications", "responsibilities", "skills", "source_url"]:
            record[f] = obj.get(f) or (obj.get("raw") or {}).get(f) or obj.get(f + "_") or ""
        # fallback title/company from raw wrapper
        if not record.get("title"):
            record["title"] = obj.get("title") or ""
        if not record.get("company"):
            record["company"] = obj.get("company") or ""
        if not record.get("source_url"):
            record["source_url"] = obj.get("source_url") or ""
        out.append(record)
    return out


def find_skill_in_text(text: str, aliases: List[str]) -> bool:
    t = (text or "").lower()
    for a in aliases:
        if a.lower() in t:
            return True
    return False


def classify_priority(record: Dict, aliases: List[str]) -> str:
    # high if appears in title/skills/qualifications
    for f in PRIORITY_HIGH_FIELDS:
        if find_skill_in_text(record.get(f, ""), aliases):
            return "high"
    for f in PRIORITY_MEDIUM_FIELDS:
        if find_skill_in_text(record.get(f, ""), aliases):
            return "medium"
    # otherwise low if appears anywhere
    combined = " ".join([record.get(k, "") for k in ["title", "description", "qualifications", "responsibilities", "skills"]])
    if find_skill_in_text(combined, aliases):
        return "low"
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path ke data/raw/job_postings_raw.jsonl", default=None)
    parser.add_argument("--out-role-skill", help="Path output role_skill_mapping.csv", default=None)
    parser.add_argument("--out-skill-aliases", help="Path output skill_aliases.csv", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    input_path = Path(args.input) if args.input else root / "data" / "raw" / "job_postings_raw.jsonl"
    out_role_skill = Path(args.out_role_skill) if args.out_role_skill else root / "data" / "processed" / "role_skill_mapping.csv"
    out_skill_aliases = Path(args.out_skill_aliases) if args.out_skill_aliases else root / "data" / "processed" / "skill_aliases.csv"

    records = read_raw_jsonl(input_path)
    logging.info(f"Membaca {len(records)} entri dari {input_path}")

    mappings = []

    # build skill aliases list for output
    skill_alias_rows = []
    canonical_map = {}
    for role, skills in ROLE_SKILLS.items():
        for s in skills:
            skill_id = s["id"]
            canonical_map[skill_id] = {"name": s["name"], "aliases": s["aliases"], "level": s.get("level", "basic")}

    # write skill_aliases
    for skill_id, info in canonical_map.items():
        skill_alias_rows.append({"keahlian": info["name"], "skill_id": skill_id, "aliases": ";".join(info["aliases"])})

    # scan each job posting
    for rec in records:
        for role, skills in ROLE_SKILLS.items():
            for s in skills:
                aliases = s["aliases"]
                prio = classify_priority(rec, aliases)
                if not prio:
                    continue
                mappings.append({
                    "peran": role,
                    "skill_id": s["id"],
                    "keahlian": s["name"],
                    "priority": prio,
                    "required_level": s.get("level", "basic"),
                    "source_url": rec.get("source_url", ""),
                    "title": rec.get("title", ""),
                    "company": rec.get("company", "")
                })

    # deduplicate mappings
    df_map = pd.DataFrame(mappings)
    if not df_map.empty:
        df_map = df_map.drop_duplicates(subset=["peran", "skill_id", "source_url"])
    else:
        df_map = pd.DataFrame(columns=["peran", "skill_id", "keahlian", "priority", "required_level", "source_url", "title", "company"])

    out_role_skill.parent.mkdir(parents=True, exist_ok=True)
    df_map.to_csv(out_role_skill, index=False)
    logging.info(f"Tersimpan role_skill_mapping ke {out_role_skill} ({len(df_map)} baris)")

    df_alias = pd.DataFrame(skill_alias_rows)
    out_skill_aliases.parent.mkdir(parents=True, exist_ok=True)
    df_alias.to_csv(out_skill_aliases, index=False)
    logging.info(f"Tersimpan skill_aliases ke {out_skill_aliases} ({len(df_alias)} baris)")


if __name__ == "__main__":
    import argparse

    main()
