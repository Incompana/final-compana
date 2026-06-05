AI Engines 5-8 — Data Collection & Preprocessing (MVP)

Bahasa: Indonesia

Proyek ini menyiapkan struktur data dan skrip pra-pemrosesan untuk Engine:

- Engine 5: Skill Gap Engine
- Engine 6: Action Plan / Task Recommendation Engine
- Engine 7: Task Evaluation Engine
- Engine 8: Progress Tracking Engine

Struktur direktori:

ai_engines_5_8/
├── data/
│ ├── raw/
│ ├── processed/
│ └── seed/
├── src/
│ ├── scraping/
│ ├── preprocessing/
│ ├── taxonomy/
│ └── utils/
├── outputs/
├── requirements.txt
└── README.md

Aturan penting untuk scraper:

- Jangan scraping LinkedIn.
- Hanya ambil halaman publik yang menyertakan JSON-LD `JobPosting` (schema.org) atau halaman karir publik yang diizinkan.
- Gunakan Python dengan `requests`, `beautifulsoup4`, `json`, dan `pandas`.

Contoh penggunaan singkat:

1. Instal dependensi:

```
pip install -r ai_engines_5_8/requirements.txt
```

2. Menjalankan scraper (contoh):

```
python ai_engines_5_8/src/scraping/scraper.py --output ai_engines_5_8/outputs/job_postings_raw.jsonl https://example.com/job-page
```

3. Menjalankan preprocessing:

```
python ai_engines_5_8/src/preprocessing/process_jobpostings.py --input ai_engines_5_8/outputs/job_postings_raw.jsonl --output-dir ai_engines_5_8/outputs
```

Semua output berbahasa Indonesia bila memungkinkan, namun istilah teknis tetap dipertahankan dalam bahasa Inggris.

Lisensi: internal — gunakan sesuai kebijakan privasi dan ketentuan situs sumber data.
