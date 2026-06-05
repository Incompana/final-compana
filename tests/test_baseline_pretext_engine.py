from __future__ import annotations

import pytest

from src.rule_engine.baseline_pretext_engine import inspect_pretext


@pytest.mark.parametrize(
    "text,expected_role,expected_problem,expected_clarification",
    [
        (
            "Aku mau jadi frontend developer React tapi sering mentok karena skill JavaScript belum kuat.",
            "frontend",
            "skill_gap",
            False,
        ),
        (
            "Aku baru mulai backend API, belum tahu mulai dari mana dan level nol.",
            "backend",
            "beginner_lost",
            False,
        ),
        (
            "Targetku data analyst, to-do belajar numpuk dan aku kewalahan tiap minggu.",
            "data_analyst",
            "overwhelmed",
            False,
        ),
        (
            "Aku mau jadi UI/UX designer tapi minder dan kurang percaya diri waktu presentasi.",
            "uiux",
            "confidence_issue",
            False,
        ),
        (
            "Aku tertarik cybersecurity tapi masih bingung antara SOC atau pentest.",
            "cybersecurity",
            "direction_confused",
            False,
        ),
        (
            "Aku bingung antara frontend dan data analyst, belum yakin pilih jalur.",
            "unclear",
            "direction_confused",
            True,
        ),
        (
            "Bingung banget.",
            "unclear",
            "unclear",
            True,
        ),
        (
            "Aku panik dan overthinking, takut gagal terus.",
            "unclear",
            "confidence_issue",
            True,
        ),
        (
            "Aku mau jadi backend API.",
            "backend",
            "unclear",
            True,
        ),
        (
            "Aku frontend React, task numpuk dan skillku belum cukup.",
            "frontend",
            "unclear",
            True,
        ),
        (
            "gw mau backend tp baru mulai, ga tau mulai dari mana, roadmap kosong",
            "backend",
            "beginner_lost",
            False,
        ),
        (
            "Butuh bantuan karier tech dong.",
            "unclear",
            "unclear",
            True,
        ),
    ],
)
def test_inspect_pretext_expected_outputs(
    text: str,
    expected_role: str,
    expected_problem: str,
    expected_clarification: bool,
) -> None:
    result = inspect_pretext(text)

    assert result["target_role"] == expected_role
    assert result["problem_category"] == expected_problem
    assert result["clarification_needed"] == expected_clarification
    assert 0.0 <= result["confidence"] <= 1.0

    # Structured JSON-friendly contract checks.
    assert isinstance(result["reasons"], list)
    assert isinstance(result["matched_signals"], dict)
    assert set(result["matched_signals"].keys()) == {"roles", "problem_categories", "ambiguity"}


def test_low_confidence_for_very_short_input() -> None:
    result = inspect_pretext("help")
    assert result["confidence"] < 0.6
    assert result["clarification_needed"] is True


def test_high_confidence_for_clear_signal_input() -> None:
    result = inspect_pretext(
        "Saya mau jadi frontend React dan sekarang mentok karena skill JavaScript belum kuat."
    )
    assert result["target_role"] == "frontend"
    assert result["problem_category"] == "skill_gap"
    assert result["confidence"] >= 0.6
    assert result["clarification_needed"] is False
