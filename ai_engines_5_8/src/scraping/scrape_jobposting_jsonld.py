"""Scrape job postings JSON-LD (schema.org JobPosting) dari daftar URL.

Fitur:
- Baca URL dari data/seed/career_urls.txt
- Ambil halaman, temukan <script type="application/ld+json"> yang bertipe JobPosting
- Normalisasi field penting dan deteksi role sederhana (keyword matching)
- Dedup sederhana berdasarkan hash(title+company+source_url)
- Simpan output ke data/raw/job_postings_raw.jsonl (append) dan data/processed/job_postings_flat.csv (overwrite)

Catatan: Jangan scraping LinkedIn. Gunakan user-agent wajar dan timeout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

USER_AGENT = "Mozilla/5.0 (compatible; CompanaAI/1.0; +https://example.com)"
TIMEOUT = 15
DISALLOWED_DOMAINS = {"linkedin.com", "www.linkedin.com"}

ROLE_KEYWORDS = {
    "frontend_developer": ["frontend", "react", "javascript", "html", "css","vue","angular"],
    "backend_developer": ["backend", "api", "python", "java", "node", "database", "sql", "golang"],
    "cyber_security_analyst": ["security", "security analyst", "siem", "cyber", "keamanan", "forensic", "penetration"],
    "data_analyst": ["data analyst", "analytics", "analyst", "tableau", "powerbi", "power bi", "sql", "pandas"]
}

TECH_KEYWORDS = ["react", "javascript", "python", "sql", "siem", "linux", "docker", "kubernetes", "aws", "azure"]


def read_seed_urls(seed_file: Path) -> List[str]:
    if not seed_file.exists():
        logging.warning(f"Seed file tidak ditemukan: {seed_file}")
        return []
    urls = []
    for line in seed_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def is_allowed_domain(url: str) -> bool:
    try:
        host = requests.utils.urlparse(url).netloc.lower()
    except Exception:
        return False
    for d in DISALLOWED_DOMAINS:
        if d in host:
            return False
    return True


def fetch_html(url: str) -> Optional[str]:
    if not is_allowed_domain(url):
        logging.warning(f"Domain tidak diizinkan: {url}")
        return None
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.error(f"Gagal mengambil {url}: {e}")
        return None


def extract_jsonld_jobposting(html: str) -> Iterable[Dict]:
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for s in scripts:
        txt = s.string or s.get_text() or ""
        txt = txt.strip()
        if not txt:
            continue
        try:
            data = json.loads(txt)
        except Exception:
            # Banyak situs memuat komentar atau non-JSON
            continue
        # data bisa dict atau list
        items = data if isinstance(data, list) else [data]
        for it in items:
            if not isinstance(it, dict):
                continue
            t = it.get("@type") or it.get("type")
            if isinstance(t, list):
                types = t
            else:
                types = [t]
            if any((typ and (typ == "JobPosting" or "JobPosting" in str(typ))) for typ in types):
                yield it


def safe_get_name(obj) -> Optional[str]:
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("name") or obj.get("nama")
    return None


def parse_location(job_location) -> Optional[str]:
    if not job_location:
        return None
    if isinstance(job_location, dict):
        address = job_location.get("address") or {}
        if isinstance(address, dict):
            parts = [address.get(k) for k in ["streetAddress", "addressLocality", "addressRegion", "postalCode", "addressCountry"] if address.get(k)]
            return ", ".join(parts)
        return safe_get_name(job_location)
    if isinstance(job_location, list):
        out = [parse_location(x) for x in job_location]
        return "; ".join([o for o in out if o])
    return str(job_location)


def normalize_jobposting(item: Dict, source_url: str) -> Dict:
    title = item.get("title") or item.get("judul") or ""
    company = safe_get_name(item.get("hiringOrganization")) or ""
    location = parse_location(item.get("jobLocation"))
    date_posted = item.get("datePosted") or item.get("date_posted")
    valid_through = item.get("validThrough") or item.get("valid_through")
    employment_type = item.get("employmentType") or item.get("employment_type")
    description = item.get("description") or ""
    # qualifications / responsibilities / skills may be strings or lists
    qualifications = item.get("qualifications") or item.get("educationRequirements") or item.get("experienceRequirements") or ""
    responsibilities = item.get("responsibilities") or item.get("responsibility") or ""
    skills = item.get("skills") or item.get("skillRequirements") or ""

    # normalize lists -> strings
    def norm_field(v):
        if v is None:
            return ""
        if isinstance(v, list):
            return "; ".join([str(x) for x in v])
        return str(v)

    qualifications = norm_field(qualifications)
    responsibilities = norm_field(responsibilities)
    skills = norm_field(skills)

    combined_text = " ".join([title, company, description, qualifications, responsibilities, skills]).lower()

    # detect role via keyword matching; title hits are stronger than body hits.
    role_scores: Dict[str, int] = {}
    role_hits: Dict[str, List[str]] = {}
    title_text = str(title or "").lower()
    explicit_title_role = ""
    if "data analyst" in title_text:
        explicit_title_role = "data_analyst"
    elif "frontend" in title_text or "front-end" in title_text:
        explicit_title_role = "frontend_developer"
    elif "backend" in title_text or "back-end" in title_text:
        explicit_title_role = "backend_developer"
    elif "security" in title_text or "cyber" in title_text:
        explicit_title_role = "cyber_security_analyst"

    for role, kws in ROLE_KEYWORDS.items():
        for kw in kws:
            kw_lower = kw.lower()
            if kw_lower in title_text:
                role_scores[role] = role_scores.get(role, 0) + 3
                role_hits.setdefault(role, []).append(kw)
            elif kw_lower in combined_text:
                role_scores[role] = role_scores.get(role, 0) + 1
                role_hits.setdefault(role, []).append(kw)

    detected_role = ""
    detected_keywords: List[str] = []
    if explicit_title_role:
        detected_role = explicit_title_role
        detected_keywords = role_hits.get(detected_role, [])
    elif role_scores:
        detected_role, _score = sorted(
            role_scores.items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        detected_keywords = role_hits.get(detected_role, [])

    if not detected_role:
        # try tech keywords
        for kw in TECH_KEYWORDS:
            if kw in combined_text and kw not in detected_keywords:
                detected_keywords.append(kw)

    # language hint simple heuristic
    language_hint = "id" if re.search(r"\b(kualifikasi|persyaratan|pengalaman|keahlian)\b", combined_text) else ("en" if re.search(r"\b(experience|skills|responsibilities)\b", combined_text) else "und")

    norm = {
        "source_url": source_url,
        "title": title,
        "company": company,
        "location": location,
        "date_posted": date_posted,
        "valid_through": valid_through,
        "employment_type": employment_type,
        "description": description,
        "qualifications": qualifications,
        "responsibilities": responsibilities,
        "skills": skills,
        "detected_role": detected_role,
        "detected_keywords": ";".join(detected_keywords),
        "language_hint": language_hint,
    }
    return norm


def make_hash(record: Dict) -> str:
    key = (record.get("title", "") + "|" + record.get("company", "") + "|" + record.get("source_url", "")).strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def load_existing_hashes(raw_path: Path) -> set:
    hashes = set()
    if not raw_path.exists():
        return hashes
    try:
        for line in raw_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            h = make_hash({"title": obj.get("title", ""), "company": obj.get("company", ""), "source_url": obj.get("source_url", "")})
            hashes.add(h)
    except Exception:
        logging.warning("Gagal membaca file raw untuk deduplikasi.")
    return hashes


def append_jsonl(path: Path, items: Iterable[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")


def write_flat_csv(path: Path, records: List[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    # normalize column order
    cols = ["source_url", "title", "company", "location", "date_posted", "valid_through", "employment_type", "description", "qualifications", "responsibilities", "skills", "detected_role", "detected_keywords", "language_hint"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    df.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="Path ke career_urls.txt", default=None)
    parser.add_argument("--raw-out", help="Path ke job_postings_raw.jsonl", default=None)
    parser.add_argument("--processed-out", help="Path ke job_postings_flat.csv", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    seed_file = Path(args.seed) if args.seed else root / "data" / "seed" / "career_urls.txt"
    raw_out = Path(args.raw_out) if args.raw_out else root / "data" / "raw" / "job_postings_raw.jsonl"
    processed_out = Path(args.processed_out) if args.processed_out else root / "data" / "processed" / "job_postings_flat.csv"

    urls = read_seed_urls(seed_file)
    if not urls:
        logging.info("Tidak ada URL seed ditemukan. Selesai.")
        return

    existing_hashes = load_existing_hashes(raw_out)
    logging.info(f"Memuat {len(existing_hashes)} entri existing untuk deduplikasi.")

    new_normalized = []
    new_raw_objects = []
    seen_hashes = set()

    for url in urls:
        logging.info(f"Memproses: {url}")
        html = fetch_html(url)
        if not html:
            continue
        for jp in extract_jsonld_jobposting(html):
            norm = normalize_jobposting(jp, url)
            h = make_hash(norm)
            if h in existing_hashes or h in seen_hashes:
                logging.info("Duplicate ditemukan, dilewati.")
                continue
            seen_hashes.add(h)
            new_normalized.append(norm)
            # preserve raw payload with metadata
            raw_obj = {"source_url": url, "raw": jp}
            # add normalized top-level keys for convenience
            raw_obj.update({k: norm.get(k, "") for k in ["title", "company"]})
            new_raw_objects.append(raw_obj)

    if new_raw_objects:
        append_jsonl(raw_out, new_raw_objects)
        logging.info(f"Menambahkan {len(new_raw_objects)} entri ke {raw_out}")
    else:
        logging.info("Tidak ada entri baru untuk ditambahkan ke raw.")

    # tulis processed csv: gabungkan existing CSV (jika ada) dengan baru
    processed_records = []
    if processed_out.exists():
        try:
            existing_df = pd.read_csv(processed_out)
            processed_records = existing_df.to_dict(orient="records")
        except Exception:
            processed_records = []

    processed_records.extend(new_normalized)
    if processed_records:
        write_flat_csv(processed_out, processed_records)
        logging.info(f"Tersimpan processed CSV: {processed_out} ({len(processed_records)} baris)")
    else:
        logging.info("Tidak ada data processed untuk disimpan.")


if __name__ == "__main__":
    main()
