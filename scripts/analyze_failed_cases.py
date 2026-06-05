from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.pipeline_logger import FAILED_CASE_LOG_FILE, PIPELINE_LOG_FILE, read_jsonl


def _parse_timestamp(value: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _filter_by_days(rows: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    if days <= 0:
        return rows

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filtered: List[Dict[str, Any]] = []
    for row in rows:
        timestamp = _parse_timestamp(str(row.get("timestamp_utc", "")))
        if timestamp is None:
            continue
        if timestamp >= cutoff:
            filtered.append(row)
    return filtered


def _print_section(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Compana failed cases from local JSONL logs.")
    parser.add_argument("--days", type=int, default=30, help="Only include rows from the last N days (default: 30).")
    parser.add_argument("--limit", type=int, default=10, help="How many recent failed cases to print (default: 10).")
    parser.add_argument("--failed-log", type=Path, default=FAILED_CASE_LOG_FILE)
    parser.add_argument("--pipeline-log", type=Path, default=PIPELINE_LOG_FILE)
    args = parser.parse_args()

    failed_rows = read_jsonl(args.failed_log)
    pipeline_rows = read_jsonl(args.pipeline_log)

    failed_rows = _filter_by_days(failed_rows, args.days)
    pipeline_rows = _filter_by_days(pipeline_rows, args.days)

    print(f"Window: last {args.days} day(s)")
    print(f"Pipeline log: {args.pipeline_log}")
    print(f"Failed-case log: {args.failed_log}")

    _print_section("High-level Counts")
    print(f"Total pipeline rows: {len(pipeline_rows)}")
    print(f"Total failed rows: {len(failed_rows)}")

    if not failed_rows:
        print("No failed-case rows found in selected window.")
        return

    step_counter: Counter[str] = Counter(row.get("step", "unknown") for row in failed_rows)
    reason_counter: Counter[str] = Counter()
    step_reason_counter: Dict[str, Counter[str]] = defaultdict(Counter)

    for row in failed_rows:
        step = str(row.get("step", "unknown"))
        reasons = row.get("failed_case_reasons", []) or []
        for reason in reasons:
            reason_text = str(reason)
            reason_counter[reason_text] += 1
            step_reason_counter[step][reason_text] += 1

    _print_section("Failed Cases by Step")
    for step, count in step_counter.most_common():
        print(f"{step}: {count}")

    _print_section("Failed Reasons (All Steps)")
    for reason, count in reason_counter.most_common():
        print(f"{reason}: {count}")

    _print_section("Failed Reasons by Step")
    for step, counter in step_reason_counter.items():
        print(step)
        for reason, count in counter.most_common():
            print(f"  - {reason}: {count}")

    _print_section(f"Recent Failed Cases (max {args.limit})")
    for row in failed_rows[-args.limit :]:
        timestamp = row.get("timestamp_utc", "n/a")
        step = row.get("step", "unknown")
        reasons = ", ".join(row.get("failed_case_reasons", []))
        confidence = row.get("confidence")
        print(f"[{timestamp}] step={step} reasons={reasons} confidence={confidence}")


if __name__ == "__main__":
    main()
