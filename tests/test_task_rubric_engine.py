from __future__ import annotations

from src.rule_engine.task_rubric_engine import (
    STATUS_NEED_REVISION,
    STATUS_PASSED,
    STATUS_PENDING,
    evaluate_task_submission_with_rubric,
)


def _assert_response_shape(payload: dict) -> None:
    assert payload["status"] in {STATUS_PASSED, STATUS_NEED_REVISION, STATUS_PENDING}
    assert "strengths" in payload and isinstance(payload["strengths"], list)
    assert "weaknesses" in payload and isinstance(payload["weaknesses"], list)
    assert "suggestions" in payload and isinstance(payload["suggestions"], list)
    assert "assistive_note" in payload and payload["assistive_note"]



def test_cybersecurity_nmap_good_submission_passed() -> None:
    submission = (
        "Nmap digunakan untuk memindai host dan port terbuka pada jaringan. "
        "Contoh sederhana: nmap -sV 192.168.1.10 untuk melihat service dan version. "
        "Dari output, kita bisa membaca port open/closed lalu menentukan tindak lanjut. "
        "Scanning dilakukan di lab sendiri dengan izin agar tetap legal dan etis."
    )

    payload = evaluate_task_submission_with_rubric(
        task_id="cybersecurity_basic_nmap_explanation",
        submission_text=submission,
    )

    _assert_response_shape(payload)
    assert payload["status"] == STATUS_PASSED
    assert len(payload["dimension_scores"]) == 5
    assert any("Best Practice" in row for row in payload["strengths"])



def test_cybersecurity_nmap_misconception_need_revision() -> None:
    submission = (
        "Menurut saya nmap dipakai untuk hack wifi dan bobol jaringan orang lain dengan cepat. "
        "Saya biasanya langsung scan target tanpa membahas izin penggunaan."
    )

    payload = evaluate_task_submission_with_rubric(
        task_id="cybersecurity_basic_nmap_explanation",
        submission_text=submission,
    )

    _assert_response_shape(payload)
    assert payload["status"] == STATUS_NEED_REVISION
    assert any("izin" in suggestion.lower() for suggestion in payload["suggestions"])



def test_frontend_dashboard_good_submission_passed() -> None:
    submission = """
<!doctype html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Dashboard Penjualan</title>
    <style>
      .card { border: 1px solid #ddd; padding: 8px; }
    </style>
  </head>
  <body>
    <header><h1>Dashboard Mingguan</h1></header>
    <main>
      <section class="card">Total Orders: 120</section>
      <section class="card">Revenue: Rp 12.000.000</section>
      <table>
        <tr><th>Produk</th><th>Qty</th></tr>
        <tr><td>Produk A</td><td>20</td></tr>
      </table>
    </main>
  </body>
</html>
""".strip()

    payload = evaluate_task_submission_with_rubric(
        task_id="frontend_simple_html_dashboard",
        submission_text=submission,
    )

    _assert_response_shape(payload)
    assert payload["status"] == STATUS_PASSED
    assert payload["weighted_score"] > 7.0



def test_frontend_dashboard_incomplete_need_revision() -> None:
    submission = "<html><body><h1>Dashboard</h1><table><tr><td>Data</td></tr></table></body></html>"

    payload = evaluate_task_submission_with_rubric(
        task_id="frontend_simple_html_dashboard",
        submission_text=submission,
    )

    _assert_response_shape(payload)
    assert payload["status"] == STATUS_NEED_REVISION
    assert any("viewport" in suggestion.lower() for suggestion in payload["suggestions"])



def test_unknown_task_returns_pending() -> None:
    payload = evaluate_task_submission_with_rubric(
        task_id="unknown_task",
        submission_text="Ini submission saya.",
    )

    _assert_response_shape(payload)
    assert payload["status"] == STATUS_PENDING
    assert payload["dimension_scores"] == []



def test_too_short_text_returns_pending() -> None:
    payload = evaluate_task_submission_with_rubric(
        task_id="cybersecurity_basic_nmap_explanation",
        submission_text="nmap itu tools",
    )

    _assert_response_shape(payload)
    assert payload["status"] == STATUS_PENDING
    assert payload["dimension_scores"] == []
