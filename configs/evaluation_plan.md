# Evaluation Plan (Placeholder)

## Goal

Validate that baseline logic is useful, explainable, and safe before any ML upgrade.

## Datasets

- `train`: labeled examples for optional baseline ML
- `dev`: tuning and error inspection
- `test`: locked evaluation
- `scenario_cases`: fixed regression scenarios (must always run)

## Metrics

For classification steps:

- Accuracy
- Macro F1
- Per-class precision/recall
- Confusion matrix

For deterministic modules:

- Scenario pass rate
- Fallback trigger correctness
- Contract/schema validation pass rate

## Minimum acceptance criteria (starter)

- Scenario tests: 100% pass
- API contract tests: 100% pass
- No silent failure on low-confidence input

## Error analysis checklist

- Ambiguous intent mistakes
- Multi-interest role confusion
- Emotional wording misclassification
- Short input fallback behavior
