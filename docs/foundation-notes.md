# Minimal Foundation Notes

## Baseline decisions

- Deterministic rules are primary for classification, mapping, routing, and feedback.
- Knowledge base (`knowledge_base/roles.json`) is source of truth for role-to-skill mapping.
- Low confidence always triggers clarification-safe fallback.

## Why this is capstone-safe

- Single FastAPI service with explicit modules and tests.
- No deep learning dependency in baseline.
- Clear migration path to `TF-IDF + Logistic Regression` in `src/classifiers/baseline.py`.

## Next practical upgrade

1. Add 100-200 clean labeled pretext samples.
2. Train and evaluate ML baseline side-by-side with rule output.
3. Keep rules as fallback and explanation layer.
