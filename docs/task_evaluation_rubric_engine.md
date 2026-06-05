# Task Evaluation Rubric Engine (Rule-Based v1)

Module: `src/rule_engine/task_rubric_engine.py`

## Goal

Assist beginner users by evaluating submissions with structured, supportive feedback.

This is **assistive evaluation**, not absolute grading.

## Rubric Dimensions

- `correctness`
- `completeness`
- `clarity`
- `technical_accuracy`
- `best_practice`

## Rubric Schema

- Schema file: `configs/task_rubric.schema.json`
- Rubric config: `configs/task_rubrics.v1.json`

The rubric config defines task-level metadata, dimension weights, and editable hints.

## Evaluator Output (JSON)

```json
{
  "evaluator_version": "task_rubric_rule_v1",
  "task_id": "cybersecurity_basic_nmap_explanation",
  "status": "need_revision",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestions": ["..."],
  "dimension_scores": [
    {
      "dimension": "correctness",
      "label": "Correctness",
      "score": 1,
      "max_score": 2,
      "weight": 1.0,
      "comment": "..."
    }
  ],
  "weighted_score": 6.2,
  "weighted_max_score": 10.8,
  "confidence": 0.85,
  "assistive_note": "Umpan balik ini bersifat pendamping untuk membantu iterasi, bukan penilaian absolut."
}
```

## Status Semantics

- `passed`: baseline submission cukup baik untuk lanjut ke task berikutnya.
- `need_revision`: submission sudah punya arah, tapi perlu perbaikan spesifik.
- `pending`: input terlalu minim/invalid atau task rubric belum tersedia.

## Supported Example Tasks (v1)

1. `cybersecurity_basic_nmap_explanation`
2. `frontend_simple_html_dashboard`

Concrete outputs for both tasks are provided in:

- `docs/task_evaluation_examples.json`

## Rule Baseline Notes

- Scoring is deterministic and keyword/pattern based.
- Dimension score range is `0..2`.
- Weighted ratio controls `passed` vs `need_revision`.
- Supportive phrasing is used intentionally to encourage iteration.
