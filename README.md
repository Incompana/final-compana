# Compana AI/ML

Practical AI/ML scaffold for Compana's learning-path assistant. The current MVP contains deterministic Engines 1-8, a FastAPI demo service, canonical CSV/JSON datasets, alignment validation, and a synthetic-data baseline classifier experiment.

## Current Scope

- Engine 1: Pretext analysis from user free text.
- Engine 2: Assessment question selection.
- Engine 3: Assessment scoring.
- Engine 4: Skill profile building.
- Engine 5: Skill gap mapping.
- Engine 6: Action plan recommendation.
- Engine 7: Task evaluation.
- Engine 8: Progress tracking.

The production-facing MVP code lives in `ai_ml_module/`. The older `src/` tree is still present for previous rule-engine/API experiments and existing tests.

Engine 1 can use a TensorFlow Functional API classifier for `problem_category` when the `.keras` artifact exists. If it is missing or fails to load, the service falls back to the existing scikit-learn baseline, then to rule-based logic.

## Repository Layout

```text
ai_ml_module/
  app.py                         # FastAPI MVP for Engines 1-8
  engines/                       # Engine implementations
  deep_learning/                 # TensorFlow training, custom callback, inference
  data/                          # Canonical MVP datasets
  utils/                         # Loaders/scoring/text helpers
  run_full_pipeline_demo.py      # End-to-end Engine 1-8 demo
  run_engine_5_8_demo.py         # Focused Engine 5-8 demo
  validate_alignment.py          # Dataset and output contract checks

data/
  label_taxonomy.json
  role_skill_mapping.csv
  task_bank.csv
  rubric_feedback_bank.csv
  labels/                        # Synthetic labeled data

scripts/
  generate_synthetic_data.py
  train_problem_category_baseline.py
  validate_synthetic_dataset.py

tests/
  test_ai_ml_module_pipeline.py
  test_*.py                      # Existing rule-engine/API tests

notebooks/
  compana_ai_ml_training_overview.ipynb
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For commands that import local packages directly, run from the repository root and set `PYTHONPATH=.` when needed.

## Run The API

```bash
uvicorn ai_ml_module.app:app --reload
```

Open the docs at:

```text
http://127.0.0.1:8000/docs
```

Important endpoints:

- `GET /`
- `GET /model-status`
- `POST /full-pipeline-demo`
- `POST /predict-problem-category`
- `POST /generate-skill-gap`
- `POST /generate-action-plan`
- `POST /evaluate-task`
- `POST /update-progress`

Example:

```bash
curl -X POST http://127.0.0.1:8000/full-pipeline-demo \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","user_input_text":"I want to become a frontend developer. I know HTML and CSS but not JavaScript."}'
```

## Run Demos

Full Engine 1-8 demo:

```bash
PYTHONPATH=. python3 ai_ml_module/run_full_pipeline_demo.py
```

Focused Engine 5-8 demo:

```bash
PYTHONPATH=. python3 ai_ml_module/run_engine_5_8_demo.py
```

Generated reports are written under ignored output folders such as `ai_ml_module/outputs/` or `outputs/`.

## Validate Alignment

```bash
python3 ai_ml_module/validate_alignment.py
```

This checks taxonomy values, dataset relationships, rubric/task consistency, and Engine 5-8 output contracts.

## Tests

```bash
python3 -m pytest -q
```

## TensorFlow Problem Category Classifier

Train the optional TensorFlow classifier:

```bash
python3 -m ai_ml_module.deep_learning.train_problem_category_tf \
  --data data/labels/dataset_pretext.csv \
  --epochs 12 \
  --batch-size 32
```

Training uses TensorFlow Functional API with `TextVectorization`, `Embedding`, `GlobalAveragePooling1D`, a dense softmax classifier, and the custom `ConfidenceLoggingCallback`.

Generated artifacts:

```text
ai_ml_module/models/problem_category_tf.keras
ai_ml_module/models/problem_category_tf_labels.json
evaluation/outputs/problem_category_tensorflow/classification_report.csv
evaluation/outputs/problem_category_tensorflow/confusion_matrix.csv
evaluation/outputs/problem_category_tensorflow/metrics.json
evaluation/outputs/problem_category_tensorflow/confidence_history.json
```

Run inference directly:

```bash
python3 -m ai_ml_module.deep_learning.inference_tf \
  --text "Saya ingin menjadi backend developer tapi belum punya portofolio"
```

Check the active classifier:

```bash
curl http://127.0.0.1:8000/model-status
```

If `tensorflow_problem_category_model.available` is `true`, Engine 1 uses the `.keras` model first. Rule-based role validation, skill gap mapping, action plan generation, and rubric evaluation remain deterministic.

## Synthetic ML Baseline

Synthetic pretext/problem-category data and model training scripts are available for experimentation:

Open the executed notebook for a visible AI/ML walkthrough:

```text
notebooks/compana_ai_ml_training_overview.ipynb
```

```bash
PYTHONPATH=. python3 scripts/generate_synthetic_data.py --num-samples 1000

PYTHONPATH=. python3 scripts/train_problem_category_baseline.py \
  --data data/labels/compana_synthetic_expanded_v1.csv \
  --model logreg \
  --output-dir evaluation/outputs/problem_category_baseline_expanded
```

The scikit-learn baseline remains as fallback when the TensorFlow artifact is not available.

## Git Hygiene

The repository intentionally ignores local virtual environments, runtime logs, generated reports, model outputs, caches, and source PDFs. Keep source code, tests, configs, and canonical small datasets tracked; regenerate outputs locally when needed.

## Next Engineering Work

- Expand tests around less common roles and incomplete dataset rows.
- Replace demo answer simulation with real user assessment submissions in the API flow.
- Add model-quality gates before enabling TensorFlow artifacts in hosted production.
