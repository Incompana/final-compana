"""Simple scraper untuk mengekstrak JSON-LD JobPosting.

Aturan:
- Jangan scrap LinkedIn.
- Hanya simpan JSON-LD dengan "@type": "JobPosting".

Contoh:
python scraper.py --output ../../outputs/job_postings_raw.jsonl https://example.com/job
"""
import argparse
import json
import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

DISALLOWED_DOMAINS = ["linkedin.com", "www.linkedin.com"]


def is_allowed_url(url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    for d in DISALLOWED_DOMAINS:
        if d in domain:
            return False
    return True


def fetch_page(url: str) -> str:
    if not is_allowed_url(url):
        raise ValueError("Sumber tidak diizinkan (LinkedIn dilarang).")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text


def extract_jobposting_jsonld(html: str):
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for s in scripts:
        try:
            data = json.loads(s.string)
        except Exception:
            continue
        # data could be dict or list
        items = data if isinstance(data, list) else [data]
        for it in items:
            if not isinstance(it, dict):
                continue
            t = it.get("@type") or it.get("type")
            # handle case list of types
            if isinstance(t, list):
                types = t
            else:
                types = [t]
            if any((typ == "JobPosting" or (isinstance(typ, str) and "JobPosting" in typ)) for typ in types if typ):
                yield it


def save_jsonl(path: str, items):
    with open(path, "a", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+", help="Daftar URL halaman job publik (dilarang: LinkedIn)")
    parser.add_argument("--output", required=True, help="Path ke file .jsonl output")
    args = parser.parse_args()

    all_items = []
    for url in args.urls:
        logging.info(f"Mengambil: {url}")
        try:
            html = fetch_page(url)
        except Exception as e:
            logging.error(f"Gagal mengambil {url}: {e}")
            continue
        items = list(extract_jobposting_jsonld(html))
        if not items:
            logging.info("Tidak menemukan JobPosting JSON-LD pada halaman ini.")
        else:
            logging.info(f"Menemukan {len(items)} JobPosting pada {url}")
            all_items.extend(items)

    if all_items:
        save_jsonl(args.output, all_items)
        logging.info(f"Tersimpan ke {args.output}")
    else:
        logging.info("Tidak ada data disimpan.")


if __name__ == "__main__":
    main()
