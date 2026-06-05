from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[2]
RUBRIC_CONFIG_PATH = BASE_DIR / "configs" / "task_rubrics.v1.json"

DIMENSIONS = [
    "correctness",
    "completeness",
    "clarity",
    "technical_accuracy",
    "best_practice",
]

STATUS_PASSED = "passed"
STATUS_NEED_REVISION = "need_revision"
STATUS_PENDING = "pending"


def _normalize(text: str) -> str:
    return str(text).strip().lower()


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_\-]+", text)


def _contains_any(text: str, cues: List[str]) -> bool:
    return any(cue in text for cue in cues)


def _sentence_count(text: str) -> int:
    chunks = re.split(r"[\.\!\?\n]+", text)
    return len([chunk for chunk in chunks if chunk.strip()])


@lru_cache(maxsize=1)
def _load_rubric_config() -> Dict[str, Any]:
    return json.loads(RUBRIC_CONFIG_PATH.read_text(encoding="utf-8"))


def _task_map() -> Dict[str, Dict[str, Any]]:
    payload = _load_rubric_config()
    return {row["task_id"]: row for row in payload.get("tasks", [])}


def _score_cybersecurity_nmap(normalized: str) -> Dict[str, Tuple[int, str]]:
    words = _tokenize(normalized)
    word_count = len(words)

    has_nmap = "nmap" in normalized
    has_scan_intent = _contains_any(
        normalized,
        ["scan", "scanning", "memindai", "pemindaian", "port scanning", "cek port"],
    )
    has_target_context = _contains_any(
        normalized,
        ["port", "host", "ip", "network", "jaringan", "service", "layanan"],
    )

    if has_nmap and has_scan_intent and has_target_context:
        correctness = (2, "Penjelasan inti fungsi nmap sudah tepat untuk level pemula.")
    elif has_nmap and (has_scan_intent or has_target_context):
        correctness = (1, "Fungsi nmap sudah disebut, tapi konteks penggunaannya masih bisa dipertegas.")
    else:
        correctness = (0, "Fungsi dasar nmap belum terlihat jelas di submission ini.")

    has_command_example = bool(re.search(r"\bnmap\b\s+[-\w\s\.\/]+", normalized))
    has_result_interpretation = _contains_any(
        normalized,
        ["open", "closed", "filtered", "hasil scan", "output", "service", "version"],
    )

    completeness_points = 0
    completeness_points += 1 if (has_nmap and has_scan_intent) else 0
    completeness_points += 1 if has_command_example else 0
    completeness_points += 1 if has_result_interpretation else 0

    if completeness_points >= 3:
        completeness = (2, "Komponen utama sudah lengkap: fungsi, contoh command, dan cara baca hasil.")
    elif completeness_points == 2:
        completeness = (1, "Sudah cukup baik, tinggal lengkapi satu komponen penting agar lebih utuh.")
    else:
        completeness = (0, "Masih perlu melengkapi fungsi dasar, contoh command, dan interpretasi hasil scan.")

    sentence_count = _sentence_count(normalized)
    if word_count >= 25 and sentence_count >= 2:
        clarity = (2, "Penjelasan sudah cukup rapi dan mudah diikuti.")
    elif word_count >= 12:
        clarity = (1, "Tulisan sudah mulai jelas, bisa lebih rapi dengan pemisahan poin.")
    else:
        clarity = (0, "Teks masih terlalu singkat untuk dipahami secara utuh.")

    positive_accuracy_signals = 0
    positive_accuracy_signals += 1 if _contains_any(normalized, ["-sv", "service detection", "version detection"]) else 0
    positive_accuracy_signals += 1 if _contains_any(normalized, ["-sn", "host discovery", "ping sweep"]) else 0
    positive_accuracy_signals += 1 if _contains_any(normalized, ["-p", "specific port", "port tertentu"]) else 0

    severe_misconception = _contains_any(
        normalized,
        ["hack wifi", "bobol", "merusak", "langsung ambil alih", "mencuri data", "virus"],
    )

    if severe_misconception and positive_accuracy_signals == 0:
        technical_accuracy = (0, "Ada istilah yang berpotensi menyesatkan; nmap bukan alat eksploitasi langsung.")
    elif positive_accuracy_signals >= 2 and not severe_misconception:
        technical_accuracy = (2, "Istilah teknis utama sudah digunakan dengan cukup akurat.")
    elif has_nmap and not severe_misconception:
        technical_accuracy = (1, "Arah teknisnya sudah benar, detail istilah masih bisa diperkuat.")
    else:
        technical_accuracy = (0, "Ketepatan teknis belum cukup jelas pada penjelasan saat ini.")

    has_permission = _contains_any(
        normalized,
        ["izin", "otorisasi", "authorized", "permission", "legal", "etis", "consent"],
    )
    has_safe_scope = _contains_any(
        normalized,
        ["jaringan sendiri", "target sendiri", "lab", "localhost", "127.0.0.1", "staging"],
    )

    if has_permission and has_safe_scope:
        best_practice = (2, "Aspek etika dan batasan penggunaan aman sudah dijelaskan dengan baik.")
    elif has_permission or has_safe_scope:
        best_practice = (1, "Sudah menyinggung praktik aman, tinggal dipertegas konteks penggunaannya.")
    else:
        best_practice = (0, "Tambahkan catatan izin/otorisasi agar penggunaan nmap tetap aman dan etis.")

    return {
        "correctness": correctness,
        "completeness": completeness,
        "clarity": clarity,
        "technical_accuracy": technical_accuracy,
        "best_practice": best_practice,
    }


def _score_frontend_dashboard(normalized: str, raw_text: str) -> Dict[str, Tuple[int, str]]:
    words = _tokenize(normalized)
    word_count = len(words)

    has_html = "<html" in normalized
    has_head = "<head" in normalized
    has_body = "<body" in normalized
    has_closing_core = "</html>" in normalized and "</body>" in normalized

    if has_html and has_head and has_body and has_closing_core:
        correctness = (2, "Struktur dasar HTML sudah lengkap dan sesuai tujuan task.")
    elif has_html or has_body:
        correctness = (1, "Struktur dasar sudah mulai terlihat, masih ada bagian inti yang perlu dilengkapi.")
    else:
        correctness = (0, "Struktur HTML inti belum terlihat jelas pada submission.")

    component_points = 0
    has_title_or_heading = _contains_any(normalized, ["<title", "<h1", "<header"])
    has_dashboard_block = _contains_any(normalized, ["card", "widget", "metric", "summary", "<section", "<article"])
    has_table_or_list = _contains_any(normalized, ["<table", "<ul", "<ol"])
    has_style = _contains_any(normalized, ["<style", "rel=\"stylesheet\"", "rel='stylesheet'"])

    component_points += 1 if has_title_or_heading else 0
    component_points += 1 if (has_dashboard_block or has_table_or_list) else 0
    component_points += 1 if has_style else 0

    if component_points >= 3:
        completeness = (2, "Elemen dashboard utama sudah cukup lengkap untuk baseline pemula.")
    elif component_points == 2:
        completeness = (1, "Komponen inti sudah ada sebagian, tambahkan satu elemen lagi agar lebih utuh.")
    else:
        completeness = (0, "Dashboard masih minim komponen penting (judul, blok data, dan styling dasar).")

    non_empty_lines = [line for line in raw_text.splitlines() if line.strip()]
    has_indentation = any(line.startswith("  ") or line.startswith("\t") for line in non_empty_lines)

    if len(non_empty_lines) >= 8 and has_indentation:
        clarity = (2, "Susunan kode cukup rapi sehingga mudah direview.")
    elif len(non_empty_lines) >= 4 or word_count >= 20:
        clarity = (1, "Keterbacaan sudah lumayan, bisa dirapikan lagi dengan struktur konsisten.")
    else:
        clarity = (0, "Kodenya masih terlalu ringkas sehingga sulit dibaca reviewer.")

    has_viewport = "viewport" in normalized
    uses_semantic = _contains_any(normalized, ["<main", "<section", "<header", "<nav", "<footer"])
    has_table_header = "<th" in normalized if "<table" in normalized else True
    uses_deprecated = _contains_any(normalized, ["<center", "<font"])

    technical_points = 0
    technical_points += 1 if has_viewport else 0
    technical_points += 1 if uses_semantic else 0
    technical_points += 1 if has_table_header else 0

    if uses_deprecated and technical_points <= 1:
        technical_accuracy = (0, "Ada penggunaan elemen lama; coba gunakan tag HTML modern agar lebih tepat.")
    elif technical_points >= 2 and not uses_deprecated:
        technical_accuracy = (2, "Implementasi teknis dasar sudah cukup tepat untuk submission awal.")
    elif technical_points >= 1:
        technical_accuracy = (1, "Arah teknis sudah benar, masih ada detail HTML yang bisa ditingkatkan.")
    else:
        technical_accuracy = (0, "Akurasi teknis HTML masih perlu diperkuat.")

    image_count = normalized.count("<img")
    image_with_alt_count = len(re.findall(r"<img[^>]*\salt=", normalized))
    has_aria = "aria-" in normalized

    practice_points = 0
    practice_points += 1 if has_viewport else 0
    practice_points += 1 if (image_count == 0 or image_with_alt_count == image_count) else 0
    practice_points += 1 if (uses_semantic or has_aria) else 0

    if practice_points >= 3:
        best_practice = (2, "Praktik responsif dan aksesibilitas dasar sudah diterapkan dengan baik.")
    elif practice_points == 2:
        best_practice = (1, "Praktik baik sudah mulai ada, masih bisa ditambah agar lebih solid.")
    else:
        best_practice = (0, "Tambahkan praktik baik seperti viewport, alt text, atau semantic tags.")

    return {
        "correctness": correctness,
        "completeness": completeness,
        "clarity": clarity,
        "technical_accuracy": technical_accuracy,
        "best_practice": best_practice,
    }


def _dimension_label(dimension: str) -> str:
    labels = {
        "correctness": "Correctness",
        "completeness": "Completeness",
        "clarity": "Clarity",
        "technical_accuracy": "Technical Accuracy",
        "best_practice": "Best Practice",
    }
    return labels.get(dimension, dimension)


def _suggestions_for(dimension: str, task_id: str) -> str:
    generic = {
        "correctness": "Mulai dari kalimat pembuka yang langsung menjawab inti tugas.",
        "completeness": "Lengkapi satu komponen kunci yang belum ada agar hasil lebih utuh.",
        "clarity": "Rapikan menjadi poin atau bagian pendek supaya reviewer mudah mengikuti.",
        "technical_accuracy": "Perkuat istilah teknis dasar dan beri contoh kecil yang relevan.",
        "best_practice": "Tambahkan catatan praktik aman/baik yang relevan dengan konteks tugas.",
    }

    task_specific = {
        ("best_practice", "cybersecurity_basic_nmap_explanation"): (
            "Tambahkan pernyataan bahwa scanning dilakukan hanya dengan izin pada target yang sah."
        ),
        ("technical_accuracy", "cybersecurity_basic_nmap_explanation"): (
            "Sertakan contoh flag nmap sederhana (mis. -sV atau -sn) beserta tujuan masing-masing."
        ),
        ("best_practice", "frontend_simple_html_dashboard"): (
            "Tambahkan `meta viewport` dan cek alt text jika ada gambar untuk aksesibilitas dasar."
        ),
        ("completeness", "frontend_simple_html_dashboard"): (
            "Tambahkan satu blok data lagi (mis. card metrik atau tabel ringkas) agar dashboard lebih informatif."
        ),
    }

    return task_specific.get((dimension, task_id), generic.get(dimension, "Perbaiki bagian ini secara bertahap."))


def evaluate_task_submission_with_rubric(task_id: str, submission_text: str) -> Dict[str, Any]:
    """
    Assistive, rule-based rubric evaluator for beginner tasks.

    Returns structured output with supportive feedback:
    - status: passed / need_revision / pending
    - strengths
    - weaknesses
    - suggestions
    """
    normalized = _normalize(submission_text)
    words = _tokenize(normalized)

    rubrics = _task_map()
    task_rubric = rubrics.get(task_id)

    if task_rubric is None:
        return {
            "evaluator_version": "task_rubric_rule_v1",
            "task_id": task_id,
            "status": STATUS_PENDING,
            "strengths": [],
            "weaknesses": ["Task rubric belum terdaftar, jadi evaluasi belum bisa dilakukan dengan aman."],
            "suggestions": [
                "Pilih task_id yang tersedia pada `configs/task_rubrics.v1.json` agar evaluasi konsisten."
            ],
            "dimension_scores": [],
            "confidence": 0.2,
            "assistive_note": "Ini evaluasi pendamping, bukan penilaian final.",
        }

    if len(words) < 6 and "<" not in normalized:
        return {
            "evaluator_version": "task_rubric_rule_v1",
            "task_id": task_id,
            "status": STATUS_PENDING,
            "strengths": [],
            "weaknesses": ["Submisi masih terlalu singkat untuk dinilai secara adil."],
            "suggestions": [
                "Tambahkan detail inti tugas dalam 3-5 kalimat agar evaluator bisa memberi umpan balik yang lebih berguna."
            ],
            "dimension_scores": [],
            "confidence": 0.25,
            "assistive_note": "Kamu sudah mulai. Tambahkan sedikit detail lagi, lalu kirim ulang.",
        }

    if task_id == "cybersecurity_basic_nmap_explanation":
        scored = _score_cybersecurity_nmap(normalized)
    elif task_id == "frontend_simple_html_dashboard":
        scored = _score_frontend_dashboard(normalized, submission_text)
    else:
        scored = {dim: (1, "Rubric khusus belum tersedia; diberikan skor baseline konservatif.") for dim in DIMENSIONS}

    weights = task_rubric.get("dimension_weights", {})

    dimension_scores: List[Dict[str, Any]] = []
    weighted_total = 0.0
    weighted_max = 0.0

    for dimension in DIMENSIONS:
        score, reason = scored.get(dimension, (0, "Belum ada sinyal cukup untuk dimensi ini."))
        weight = float(weights.get(dimension, 1.0))
        weighted_total += score * weight
        weighted_max += 2.0 * weight

        dimension_scores.append(
            {
                "dimension": dimension,
                "label": _dimension_label(dimension),
                "score": int(score),
                "max_score": 2,
                "weight": round(weight, 2),
                "comment": reason,
            }
        )

    ratio = weighted_total / weighted_max if weighted_max else 0.0

    if ratio >= 0.75:
        status = STATUS_PASSED
    else:
        status = STATUS_NEED_REVISION

    strengths = [
        f"{row['label']}: {row['comment']}"
        for row in dimension_scores
        if row["score"] == 2
    ]

    weaknesses = [
        f"{row['label']}: {row['comment']}"
        for row in dimension_scores
        if row["score"] <= 1
    ]

    suggestions = [
        _suggestions_for(row["dimension"], task_id)
        for row in dimension_scores
        if row["score"] <= 1
    ]

    # Keep suggestion list concise and deterministic.
    deduped_suggestions: List[str] = []
    for suggestion in suggestions:
        if suggestion not in deduped_suggestions:
            deduped_suggestions.append(suggestion)

    confidence = 0.85 if task_id in {
        "cybersecurity_basic_nmap_explanation",
        "frontend_simple_html_dashboard",
    } else 0.55

    return {
        "evaluator_version": "task_rubric_rule_v1",
        "task_id": task_id,
        "status": status,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": deduped_suggestions[:5],
        "dimension_scores": dimension_scores,
        "weighted_score": round(weighted_total, 2),
        "weighted_max_score": round(weighted_max, 2),
        "confidence": confidence,
        "assistive_note": (
            "Umpan balik ini bersifat pendamping untuk membantu iterasi, bukan penilaian absolut."
        ),
    }
