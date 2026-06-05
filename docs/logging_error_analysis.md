# Logging and Error Analysis (Compana AI/ML)

Compana uses a lightweight file-based logging layer (JSONL) for each AI pipeline step.
No external logging service is required.

## Log Files

Generated under `ai-ml/logs/`:

- `pipeline_steps.jsonl`
- `failed_cases.jsonl`
- `pipeline_errors.jsonl`

## What Gets Logged

For each endpoint step (`/analyze-pretext`, `/generate-assessment`, `/map-gap-skills`, `/generate-action-plan`, `/evaluate-task`):

- `timestamp_utc`
- `request_id`
- `step`
- `confidence` (when available)
- `clarification_needed` (when available)
- `fallback_triggered` (when available)
- `status` (when available)
- `failed_case` + `failed_case_reasons`
- full `request` and `response` payloads

## Failed-Case Capture Rules

A response is copied to `failed_cases.jsonl` when one or more of these signals are present:

- `confidence < 0.6`
- `clarification_needed = true`
- `fallback_triggered = true`
- `status` is `pending` or `need_revision`
- unhandled exception inside endpoint execution

## Quick Inspection

Run summary script:

```bash
cd ai-ml
python3 scripts/analyze_failed_cases.py --days 14 --limit 15
```

Useful options:

- `--days 30` to change time window
- `--limit 20` to print more recent failed rows
- `--failed-log <path>` to inspect alternate log file

## Manual Inspection Examples

Show latest 5 failed rows:

```bash
tail -n 5 logs/failed_cases.jsonl
```

Count failed rows by step (quick Python one-liner):

```bash
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path

path = Path('logs/failed_cases.jsonl')
counter = Counter()
if path.exists():
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            row = json.loads(line)
            counter[row.get('step', 'unknown')] += 1
print(counter)
PY
```

## Notes

- This layer is intended for baseline observability and error analysis.
- Keep logs local for now; rotate/archive periodically if files grow too large.
