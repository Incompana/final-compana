from __future__ import annotations

from fastapi.testclient import TestClient

from ai_ml_module.app import app
from ai_ml_module.utils import model_loader


def test_model_status_reports_active_classifier():
    client = TestClient(app)

    response = client.get("/model-status")

    assert response.status_code == 200
    models = response.json()["models"]
    assert "tensorflow_problem_category_model" in models
    assert "problem_category_model" in models
    assert models["active_classifier"] in {"tensorflow", "sklearn", "rule_based"}


def test_predict_problem_category_contract():
    client = TestClient(app)

    response = client.post(
        "/predict-problem-category",
        json={"text": "Saya ingin jadi backend developer tapi belum punya portofolio."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["label"]
    assert "confidence" in body
    assert isinstance(body["top_k"], list)
    assert body["classifier_type"] in {"tensorflow", "sklearn", "rule_based"}


def test_tensorflow_status_priority_when_artifacts_exist(tmp_path, monkeypatch):
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / model_loader.TENSORFLOW_PROBLEM_CATEGORY_MODEL).write_text("placeholder", encoding="utf-8")
    (model_dir / model_loader.TENSORFLOW_PROBLEM_CATEGORY_LABELS).write_text("{}", encoding="utf-8")

    monkeypatch.setattr(model_loader, "MODEL_SEARCH_PATHS", [model_dir])

    status = model_loader.get_model_status()

    assert status["tensorflow_problem_category_model"]["available"] is True
    assert status["active_classifier"] == "tensorflow"

