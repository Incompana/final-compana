# Data Dictionary — Compana Synthetic Pretext v1

Dataset file: `data/labels/compana_synthetic_pretext_id_v1.csv`

## Overview

- Total rows: 120
- Language: Indonesian
- Audience profile: mahasiswa, fresh graduate, dan career switcher ke bidang tech
- Use case: baseline experiments untuk pretext understanding dan classification

## Columns

| Column | Type | Required | Description | Example |
|---|---|---|---|---|
| `pretext_text` | string | Yes | Teks bebas user yang menjelaskan kebingungan/masalah karier | `Aku fresh graduate jurusan informatika, aku mau jadi backend developer...` |
| `target_role` | enum | Yes | Target role utama user saat ini | `backend` |
| `problem_category` | enum | Yes | Kategori masalah dominan user | `direction_confused` |
| `current_level` | enum | Yes | Perkiraan level kesiapan user | `basic` |
| `blocker_type` | enum | Yes | Hambatan paling utama yang mengunci progres | `no_roadmap` |

## Allowed Labels

### `target_role`

- `cybersecurity`
- `frontend`
- `backend`
- `data_analyst`
- `uiux`
- `unclear`

### `problem_category`

- `beginner_lost`
- `direction_confused`
- `skill_gap`
- `overwhelmed`
- `confidence_issue`
- `unclear`

### `current_level`

- `zero`
- `basic`
- `intermediate`
- `unclear`

### `blocker_type`

- `no_roadmap`
- `no_portfolio`
- `no_foundation`
- `no_time`
- `no_confidence`
- `too_many_options`
- `unclear`

## Quality Notes

- Dataset mengandung campuran input:
  - pendek (singkat)
  - medium (2-3 kalimat)
  - messy/colloquial (slang, typo ringan)
- Terdapat kasus ambigu dan emosional untuk menguji fallback behavior.
- Ini dataset sintetis untuk baseline, bukan representasi statistik populasi riil.

## Validation

Jalankan validator:

```bash
python3 scripts/validate_synthetic_dataset.py
```

Opsional path custom:

```bash
python3 scripts/validate_synthetic_dataset.py --csv data/labels/compana_synthetic_pretext_id_v1.csv --taxonomy configs/taxonomy.json --expected-count 120
```
