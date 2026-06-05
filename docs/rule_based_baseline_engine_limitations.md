# Rule-Based Baseline Engine: Limitations and Failure Modes

This baseline is intentionally simple (keyword + regex heuristics). It is suitable for early-stage experiments, but has known limitations.

## Key Limitations

- Heavy dependence on explicit keywords:
  - If users describe intent indirectly, role/problem can be missed.
- Vocabulary sensitivity:
  - Slang, typos, and uncommon phrasing can reduce accuracy.
- Context blindness:
  - The engine does not understand long conversational history.
- No semantic understanding:
  - Similar meaning with different wording may be classified differently.
- Tie handling is conservative:
  - Multi-signal inputs often become `unclear` and trigger clarification.

## Likely Failure Modes

1. Multi-role intent in one sentence
- Example: user mentions `frontend` and `data analyst` equally.
- Result: role becomes `unclear` even if human reader can infer preference.

2. Overlapping keyword domains
- Example: `API` and `SQL` can indicate multiple roles depending on context.
- Result: wrong role or low confidence.

3. Emotional wording dominates
- Example: intense anxiety language plus concrete skill issues.
- Result: `confidence_issue` may be chosen over `skill_gap`.

4. Very short input
- Example: "bingung", "tolong".
- Result: low confidence, almost always clarification needed.

5. Keyword negation and sarcasm
- Example: "bukan backend" or sarcastic statements.
- Result: rules may still match the negated keyword.

## Practical Mitigations

- Keep rules in one file and update with observed phrases.
- Log false positives/negatives and add targeted patterns monthly.
- Maintain clarification fallback for low-confidence cases.
- Use this baseline as a deterministic guardrail before introducing lightweight ML.
