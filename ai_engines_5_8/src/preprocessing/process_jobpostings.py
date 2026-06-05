"""Proses minimal job_postings_raw.jsonl -> beberapa CSV schema minimal.

Tujuan: menghasilkan file:
- role_skill_mapping.csv
- skill_aliases.csv
- task_bank.csv
- rubric_bank.csv

Semua kolom header berbahasa Indonesia.
"""
import argparse
import logging
import os
from collections import defaultdict

import pandas as pd

from ..utils.io import read_jsonl

logging.basicConfig(level=logging.INFO)


def extract_basic_fields(item: dict) -> dict:
    # Ambil field utama dari JobPosting JSON-LD
    return {
        "title": item.get("title") or item.get("judul"),
        "description": item.get("description"),
        "datePosted": item.get("datePosted"),
        "hiringOrganization": (item.get("hiringOrganization") or {}).get("name") if isinstance(item.get("hiringOrganization"), dict) else item.get("hiringOrganization"),
        "employmentType": item.get("employmentType"),
        "jobLocation": item.get("jobLocation")
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path ke job_postings_raw.jsonl")
    parser.add_argument("--output-dir", required=True, help="Direktori output CSV")
    args = parser.parse_args()

    items = list(read_jsonl(args.input))
    logging.info(f"Membaca {len(items)} job posting dari {args.input}")

    # Buat DataFrame utama
    records = [extract_basic_fields(it) for it in items]
    df = pd.DataFrame(records)

    os.makedirs(args.output_dir, exist_ok=True)

    # Simpan salinan raw (ringkas) sebagai referensi
    df.to_json(os.path.join(args.output_dir, "job_postings_summary.json"), orient="records", force_ascii=False)

    # Buat CSV minimal: role_skill_mapping (kosong—berisi header jika tidak ada ekstraksi)
    rsm = pd.DataFrame(columns=["peran", "keahlian", "sumber"])

    # Contoh heuristik sederhana: jika title mengandung kata kunci
    role_keywords = {
        "frontend_developer": ["frontend", "react", "javascript"],
        "backend_developer": ["backend", "api", "python", "java", "database", "sql"],
        "cyber_security_analyst": ["security", "siem", "cyber", "keamanan"],
        "data_analyst": ["data", "analyst", "sql", "pandas", "analisis"]
    }

    gathered = []
    for it in items:
        title = (it.get("title") or "").lower()
        text = ((it.get("description") or "") + " " + title).lower()
        for role, kws in role_keywords.items():
            if any(k in text for k in kws):
                skills = []
                # coba ambil skills jika ada field 'skills' atau 'qualifications'
                if "skills" in it and isinstance(it["skills"], list):
                    skills = it["skills"]
                elif isinstance(it.get("occupationalCategory"), list):
                    skills = it.get("occupationalCategory")
                else:
                    # fallback: cari keyword teknis dalam text
                    for k in ["react", "javascript", "python", "sql", "siem", "linux"]:
                        if k in text and k not in skills:
                            skills.append(k)
                gathered.append({"peran": role, "keahlian": ";".join(map(str, skills)) if skills else "", "sumber": it.get("title")})

    if gathered:
        rsm = pd.DataFrame(gathered)

    rsm.to_csv(os.path.join(args.output_dir, "role_skill_mapping.csv"), index=False)

    # Skill aliases: kosong/template
    sa = pd.DataFrame(columns=["keahlian", "alias"])
    sa.to_csv(os.path.join(args.output_dir, "skill_aliases.csv"), index=False)

    # Task bank: kosong/template
    tb = pd.DataFrame(columns=["id_tugas", "judul", "deskripsi", "keahlian_terkait", "sumber"])
    tb.to_csv(os.path.join(args.output_dir, "task_bank.csv"), index=False)

    # Rubric bank: kosong/template
    rb = pd.DataFrame(columns=["id_rubrik", "keahlian", "kriteria", "skor_min", "skor_max"])
    rb.to_csv(os.path.join(args.output_dir, "rubric_bank.csv"), index=False)

    logging.info("Pra-pemrosesan selesai. File CSV minimal dibuat di %s" % args.output_dir)


if __name__ == "__main__":
    main()
