# Compana AI/ML Demo Deployment

## Backend

Required files must be deployed with the app:

- `ai_ml_module/data/*`
- `data/*`
- `ai_ml_module/models/problem_category_logreg.joblib`

Install:

```bash
pip install -r requirements.txt
```

Production command:

```bash
gunicorn ai_ml_module.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}
```

Environment:

```bash
APP_ENV=production
CORS_ORIGINS=https://your-frontend-domain.example.com
```

Smoke checks:

```bash
curl https://your-api-domain.example.com/health
curl https://your-api-domain.example.com/readiness
curl https://your-api-domain.example.com/model-status
```

Deploy gate before release:

```bash
python3 ai_ml_module/validate_alignment.py
python3 scripts/generate_data_quality_report.py
python3 -m pytest -q
```

## Frontend

`mvp_app/` is a static app. Before deploying, set the backend URL in:

```text
mvp_app/config.js
```

Example:

```javascript
window.COMPANA_CONFIG = {
  API_BASE_URL: "https://your-api-domain.example.com",
};
```

Then deploy the whole `mvp_app/` directory to any static host.

## Demo Flow

1. Open frontend.
2. Enter user pretext.
3. Answer assessment questions.
4. Submit assessment.
5. Review skill gap and recommended tasks.
6. Submit project task.
7. Review rubric evaluation.

## Current Production Caveats

- The model is demo-ready but not production-grade; dataset labels are imbalanced.
- No authentication or persistent user storage yet.
- Task copy is functional, but some capstone-generated task titles still need product copy polish.
