# Compana FastAPI Service Guide

This service exposes the current rule-based Compana AI/ML modules.
No authentication is enabled in this baseline.

## Run Locally

```bash
cd ai-ml
python3 -m pip install -r requirements.txt
uvicorn src.main:app --reload
```

Open API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Endpoints

### 1) `POST /analyze-pretext`

Request example:

```json
{
  "pretext_text": "Aku mau jadi frontend, tapi masih bingung mulai dari mana dan sering stuck pas bikin project."
}
```

### 2) `POST /generate-assessment`

Request example:

```json
{
  "pretext_analysis": {
    "confidence": 0.78,
    "clarification_needed": false,
    "matched_signals": {
      "roles": {
        "frontend": ["\\breact\\b"]
      }
    }
  },
  "problem_category": "skill_gap",
  "target_role": "frontend",
  "current_level": "basic",
  "blocker_type": "no_portfolio"
}
```

### 3) `POST /map-gap-skills`

Request example:

```json
{
  "target_role": "cybersecurity",
  "current_level": "zero",
  "assessment_answers": {
    "foundation_check": [
      "Saya belum paham network",
      "Saya baru belajar Linux command dasar"
    ]
  },
  "detected_skills": ["linux"]
}
```

### 4) `POST /generate-action-plan`

Request example:

```json
{
  "target_role": "frontend",
  "problem_category": "skill_gap",
  "current_level": "basic",
  "blocker_type": "no_portfolio",
  "gap_skills": ["react_component_basics", "api_fetch_state"]
}
```

### 5) `POST /evaluate-task`

Request example:

```json
{
  "task_id": "cybersecurity_basic_nmap_explanation",
  "submission_text": "Nmap dipakai untuk scan host/port. Contoh: nmap -sV 192.168.1.10. Saya hanya scan target lab sendiri dengan izin."
}
```

## Quick API Test

```bash
python3 -m pytest -q tests/test_api.py
```
