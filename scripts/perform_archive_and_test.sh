#!/usr/bin/env bash
set -euo pipefail

# Safe archive and test script
# Moves archival candidates into _archive_unused/ (preserving path), runs demo,
# restores on failure and writes reports under outputs/.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

ARCHIVE_DIR="_archive_unused"
OUT_DIR="outputs"
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$OUT_DIR"

MOVED_LIST_FILE="$OUT_DIR/moved_files_list.txt"
ERROR_REPORT="$OUT_DIR/cleanup_error_report.md"
FINAL_REPORT="$OUT_DIR/cleanup_final_report.md"

rm -f "$MOVED_LIST_FILE" "$ERROR_REPORT" "$FINAL_REPORT"

echo "Starting archival (excluding venv to avoid breaking environment)..."

# Helper: move a path to archive preserving prefix
move_to_archive() {
  src="$1"
  if [ ! -e "$src" ]; then
    return 0
  fi
  dest="$ARCHIVE_DIR/${src#./}"
  mkdir -p "$(dirname "$dest")"
  mv "$src" "$dest"
  echo "$src" >> "$MOVED_LIST_FILE"
}

# 1) Move evaluation outputs (if present)
if [ -d "evaluation/outputs/problem_category_baseline" ]; then
  mkdir -p "$ARCHIVE_DIR/evaluation/outputs"
  mv evaluation/outputs/problem_category_baseline "$ARCHIVE_DIR/evaluation/outputs/"
  echo "evaluation/outputs/problem_category_baseline" >> "$MOVED_LIST_FILE"
fi

# 2) Move notebook(s)
if [ -f "notebooks/problem_category_baseline_experiment.ipynb" ]; then
  mkdir -p "$ARCHIVE_DIR/notebooks"
  mv notebooks/problem_category_baseline_experiment.ipynb "$ARCHIVE_DIR/notebooks/"
  echo "notebooks/problem_category_baseline_experiment.ipynb" >> "$MOVED_LIST_FILE"
fi

# 3) Move top-level .pytest_cache
if [ -d ".pytest_cache" ]; then
  mkdir -p "$ARCHIVE_DIR/.pytest_cache"
  mv .pytest_cache "$ARCHIVE_DIR/.pytest_cache"
  echo ".pytest_cache" >> "$MOVED_LIST_FILE"
fi

# 4) Move any __pycache__ directories found (preserve structure)
find . -type d -name "__pycache__" -print0 | while IFS= read -r -d '' d; do
  # skip archive dir
  if [[ "$d" == "./$ARCHIVE_DIR"* ]]; then
    continue
  fi
  dest="$ARCHIVE_DIR/${d#./}"
  mkdir -p "$(dirname "$dest")"
  mv "$d" "$dest"
  echo "$d" >> "$MOVED_LIST_FILE"
done

# 5) Move temporary files matching patterns
find . -type f \( -name ".DS_Store" -o -name "temp.csv" -o -name "old_*.py" -o -name "copy_*.py" -o -name "*backup*" -o -name "*~" \) -print0 | while IFS= read -r -d '' f; do
  # skip files inside archive dir
  if [[ "$f" == "./$ARCHIVE_DIR"* ]]; then
    continue
  fi
  dest="$ARCHIVE_DIR/${f#./}"
  mkdir -p "$(dirname "$dest")"
  mv "$f" "$dest"
  echo "$f" >> "$MOVED_LIST_FILE"
done

echo "Archival moves completed. Moved files list:"
cat "$MOVED_LIST_FILE" || true

echo "Running demo to verify Engines 5-8..."

set +e
PYTHONPATH=. python3 ai_ml_module/run_engine_5_8_demo.py
RET=$?
set -e

if [ $RET -ne 0 ]; then
  echo "Demo failed (exit $RET). Restoring moved files..."
  echo "Demo failed with exit code $RET" > "$ERROR_REPORT"
  echo "Restoring archived files..." >> "$ERROR_REPORT"
  # restore by moving back (depth-first)
  find "$ARCHIVE_DIR" -mindepth 1 -depth -print0 | while IFS= read -r -d '' p; do
    orig="${p#$ARCHIVE_DIR/}"
    mkdir -p "$(dirname "$orig")"
    mv "$p" "$orig"
  done
  echo "Restoration complete." >> "$ERROR_REPORT"
  echo "See $ERROR_REPORT"
  exit 1
fi

echo "Demo succeeded. Writing final report..."

echo "# Cleanup Final Report" > "$FINAL_REPORT"
echo >> "$FINAL_REPORT"
echo "Demo run: SUCCESS" >> "$FINAL_REPORT"
echo >> "$FINAL_REPORT"
echo "Moved files (relative paths):" >> "$FINAL_REPORT"
echo >> "$FINAL_REPORT"
sed 's/^/- /' "$MOVED_LIST_FILE" >> "$FINAL_REPORT"

echo "Cleanup and verification complete. See $FINAL_REPORT"
exit 0
