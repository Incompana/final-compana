from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
ROLE_KB_DIR = BASE_DIR / "knowledge_base" / "role_skill_task"

ROLE_LABELS = {"cybersecurity", "frontend", "backend", "data_analyst", "uiux"}


def _normalize(value: str) -> str:
    return str(value).strip().lower()


def _display_role(role_id: str) -> str:
    return role_id.replace("_", " ").title()


@lru_cache(maxsize=1)
def _load_role_index() -> Dict[str, str]:
    index_file = ROLE_KB_DIR / "index.json"
    payload = json.loads(index_file.read_text(encoding="utf-8"))
    mapping: Dict[str, str] = {}

    for row in payload.get("roles", []):
        role_id = str(row.get("role_id", "")).strip()
        file_value = str(row.get("file", "")).strip()
        if not role_id or not file_value:
            continue
        mapping[role_id] = Path(file_value).name

    return mapping


@lru_cache(maxsize=16)
def _load_role_payload(role_id: str) -> Optional[Dict[str, Any]]:
    role_file = _load_role_index().get(role_id)
    if not role_file:
        return None

    path = ROLE_KB_DIR / role_file
    if not path.exists():
        return None

    return json.loads(path.read_text(encoding="utf-8"))


def _dedupe_gap_skills(gap_skills: List[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for raw in gap_skills:
        token = _normalize(raw)
        if not token:
            continue
        if token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized


def _new_step(
    title: str,
    task_suggestion: str,
    expected_output: str,
    success_criteria: str,
) -> Dict[str, str]:
    return {
        "title": title,
        "task_suggestion": task_suggestion,
        "expected_output": expected_output,
        "success_criteria": success_criteria,
    }


def _kickoff_step(target_role: str) -> Dict[str, str]:
    if target_role == "unclear":
        return _new_step(
            title="Tentukan Satu Role Fokus 4 Minggu",
            task_suggestion=(
                "Pilih 1 role utama dari 3 opsi teratas yang kamu minati, lalu tulis alasan "
                "pemilihan dalam 3 kalimat."
            ),
            expected_output="Dokumen singkat role_decision.md berisi 1 role terpilih + alasannya.",
            success_criteria="Satu role dipilih secara tegas dan tidak berubah selama 7 hari pertama.",
        )

    return _new_step(
        title="Tetapkan Outcome Minggu Ini",
        task_suggestion=(
            f"Tetapkan satu output kecil yang relevan dengan role {target_role}, lalu pecah menjadi "
            "3 tugas harian yang realistis."
        ),
        expected_output="Rencana 7 hari berisi output utama + checklist tugas harian.",
        success_criteria="Minimal 3 sesi kerja terjadwal dengan target output yang jelas.",
    )


def _foundation_step(target_role: str, current_level: str) -> Dict[str, str]:
    role_text = _display_role(target_role) if target_role in ROLE_LABELS else "target role"

    if current_level == "zero":
        return _new_step(
            title="Bangun Fondasi Dasar",
            task_suggestion=(
                f"Selesaikan 2 latihan dasar {role_text} dari materi pemula dan tulis catatan konsep kunci."
            ),
            expected_output="2 file latihan dasar + catatan ringkas konsep inti.",
            success_criteria="Kamu bisa menjelaskan kembali konsep dasar tanpa membaca ulang materi.",
        )

    if current_level == "basic":
        return _new_step(
            title="Perkuat Fondasi yang Belum Stabil",
            task_suggestion=(
                "Ulang 1 topik dasar yang sering bikin mentok, lalu praktikkan pada mini-task berdurasi <90 menit."
            ),
            expected_output="Satu mini-task selesai beserta catatan kendala dan solusi.",
            success_criteria="Mini-task selesai end-to-end dan tidak lagi tersendat di titik yang sama.",
        )

    if current_level == "intermediate":
        return _new_step(
            title="Konsolidasikan Skill Inti",
            task_suggestion=(
                "Pilih 1 skill inti untuk diperdalam lewat mini-project yang menuntut kualitas implementasi lebih rapi."
            ),
            expected_output="Mini-project revisi dengan struktur yang lebih rapi dari versi sebelumnya.",
            success_criteria="Ada peningkatan jelas pada kualitas output (struktur, konsistensi, dokumentasi).",
        )

    return _new_step(
        title="Validasi Level Saat Ini",
        task_suggestion=(
            "Kerjakan 1 self-check sederhana: tulis apa yang sudah bisa, yang belum bisa, dan contoh bukti kerja."
        ),
        expected_output="Checklist level berisi kemampuan saat ini + bukti untuk tiap poin.",
        success_criteria="Ada gambaran level yang cukup jelas untuk menentukan langkah berikutnya.",
    )


def _blocker_step(blocker_type: str, target_role: str) -> Dict[str, str]:
    role_text = _display_role(target_role) if target_role in ROLE_LABELS else "role terpilih"

    if blocker_type == "no_roadmap":
        return _new_step(
            title="Susun Roadmap 4 Minggu",
            task_suggestion=(
                "Buat urutan belajar mingguan (minggu 1-4) dengan 1 milestone terukur per minggu."
            ),
            expected_output="Roadmap 4 minggu dengan milestone dan batas waktu.",
            success_criteria="Setiap minggu punya target output yang spesifik dan dapat dicek selesai/tidak.",
        )

    if blocker_type == "no_portfolio":
        return _new_step(
            title="Bangun Bukti Portfolio Pertama",
            task_suggestion=(
                f"Pilih 1 mini-project {role_text} yang bisa selesai dalam 5-7 hari, lalu publikasi di GitHub/Notion."
            ),
            expected_output="1 link project publik + README singkat konteks, fitur, dan hasil.",
            success_criteria="Project bisa diakses publik dan menjelaskan kontribusi kamu secara jelas.",
        )

    if blocker_type == "no_foundation":
        return _new_step(
            title="Perbaiki Titik Fondasi Paling Lemah",
            task_suggestion=(
                "Pilih 1 konsep dasar yang belum paham, pelajari 45 menit, lalu praktikkan langsung dalam latihan kecil."
            ),
            expected_output="Ringkasan konsep + 1 latihan yang menerapkan konsep tersebut.",
            success_criteria="Latihan selesai dan kamu bisa menjelaskan cara kerjanya dengan bahasa sendiri.",
        )

    if blocker_type == "no_time":
        return _new_step(
            title="Aktifkan Jadwal Mikro yang Konsisten",
            task_suggestion=(
                "Blok 4 sesi singkat (30-45 menit) per minggu dan kunci jam tetap untuk eksekusi task utama."
            ),
            expected_output="Kalender mingguan berisi minimal 4 blok belajar/eksekusi.",
            success_criteria="Minimal 3 dari 4 blok waktu terlaksana dalam minggu berjalan.",
        )

    if blocker_type == "no_confidence":
        return _new_step(
            title="Bangun Kepercayaan Diri lewat Output Kecil",
            task_suggestion=(
                "Selesaikan 1 tugas kecil yang bisa ditunjukkan ke mentor/teman, lalu minta 1 feedback konkret."
            ),
            expected_output="Output tugas kecil + 1 umpan balik tertulis.",
            success_criteria="Feedback diterapkan ke versi revisi sehingga ada peningkatan nyata.",
        )

    if blocker_type == "too_many_options":
        return _new_step(
            title="Batasi Opsi Supaya Fokus",
            task_suggestion=(
                "Tuliskan semua opsi yang sedang dikejar, coret hingga tersisa 1 jalur utama dan 1 jalur cadangan."
            ),
            expected_output="Daftar opsi yang sudah dipangkas + alasan pemangkasan.",
            success_criteria="Selama 2 minggu tidak menambah jalur baru di luar pilihan utama.",
        )

    return _new_step(
        title="Klarifikasi Blocker Utama",
        task_suggestion=(
            "Catat 3 momen terakhir saat kamu berhenti progres, lalu identifikasi pola blocker yang paling sering muncul."
        ),
        expected_output="Jurnal blocker singkat berisi pola utama dan pemicu paling sering.",
        success_criteria="Satu blocker dominan berhasil diidentifikasi untuk ditangani terlebih dahulu.",
    )


def _task_from_kb(role_payload: Dict[str, Any], skill_id: str) -> Optional[Dict[str, Any]]:
    for task in role_payload.get("beginner_tasks", []):
        if skill_id in task.get("focus_skills", []):
            return task
    return None


def _gap_steps(
    target_role: str,
    role_payload: Optional[Dict[str, Any]],
    gap_skills: List[str],
    max_steps: int = 2,
) -> List[Dict[str, str]]:
    steps: List[Dict[str, str]] = []

    for skill_id in gap_skills[:max_steps]:
        readable = skill_id.replace("_", " ").title()

        if role_payload is not None:
            task = _task_from_kb(role_payload, skill_id)
            if task:
                expected_artifacts = ", ".join(task.get("expected_artifacts", [])) or "artifact tugas"
                steps.append(
                    _new_step(
                        title=f"Tutup Gap Skill: {readable}",
                        task_suggestion=(
                            f"Kerjakan task '{task.get('title', '')}' dan fokus pada skill {readable}."
                        ),
                        expected_output=f"Artifact: {expected_artifacts}.",
                        success_criteria="Artifact selesai dan dapat dijelaskan keputusan implementasinya.",
                    )
                )
                continue

        role_hint = _display_role(target_role) if target_role in ROLE_LABELS else "role pilihanmu"
        steps.append(
            _new_step(
                title=f"Latihan Terarah: {readable}",
                task_suggestion=(
                    f"Buat latihan mini 60-90 menit untuk skill {readable} yang relevan dengan {role_hint}."
                ),
                expected_output="Satu output mini (kode/desain/catatan) yang menunjukkan penggunaan skill.",
                success_criteria="Output berjalan/terbaca dan mencerminkan skill target secara nyata.",
            )
        )

    return steps


def _fallback_execution_step() -> Dict[str, str]:
    return _new_step(
        title="Kirim Satu Output Nyata Minggu Ini",
        task_suggestion=(
            "Pilih tugas paling kecil yang bisa selesai dalam 60 menit dan kirim hasilnya untuk di-review."
        ),
        expected_output="Satu artefak nyata (file/link/screenshot) yang bisa dievaluasi.",
        success_criteria="Output terkirim tepat waktu dan mendapatkan feedback awal.",
    )


def _closing_step() -> Dict[str, str]:
    return _new_step(
        title="Review Progres dan Tetapkan Langkah Lanjut",
        task_suggestion=(
            "Evaluasi langkah yang selesai vs rencana, lalu pilih 1 prioritas utama untuk minggu berikutnya."
        ),
        expected_output="Catatan review mingguan + prioritas tunggal minggu depan.",
        success_criteria="Ada keputusan jelas tentang langkah lanjut tanpa menambah target berlebihan.",
    )


def render_action_plan_markdown(plan: Dict[str, Any]) -> str:
    lines = [f"# {plan['title']}", ""]

    input_snapshot = plan.get("input_snapshot", {})
    lines.append("Input ringkas:")
    lines.append(
        "- "
        + ", ".join(
            [
                f"target_role={input_snapshot.get('target_role', 'unclear')}",
                f"problem_category={input_snapshot.get('problem_category', 'unclear')}",
                f"current_level={input_snapshot.get('current_level', 'unclear')}",
                f"blocker_type={input_snapshot.get('blocker_type', 'unclear')}",
            ]
        )
    )
    lines.append("")

    lines.append("## Steps")
    for step in plan.get("steps", []):
        lines.append(f"{step['order']}. **{step['title']}**")
        lines.append(f"Task suggestion: {step['task_suggestion']}")
        lines.append(f"Expected output: {step['expected_output']}")
        lines.append(f"Success criteria: {step['success_criteria']}")
        lines.append("")

    if plan.get("rationale"):
        lines.append("## Rationale")
        for reason in plan["rationale"]:
            lines.append(f"- {reason}")

    return "\n".join(lines).strip()


def generate_action_plan(
    target_role: str,
    problem_category: str,
    current_level: str,
    blocker_type: str,
    gap_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Deterministic action plan generator using templates + structured rules.

    Inputs:
    - target_role
    - problem_category
    - current_level
    - blocker_type
    - gap_skills

    Output:
    - JSON plan with 3-6 ordered steps
    - markdown_view for easy frontend rendering or export
    """
    role = _normalize(target_role) or "unclear"
    category = _normalize(problem_category) or "unclear"
    level = _normalize(current_level) or "unclear"
    blocker = _normalize(blocker_type) or "unclear"
    normalized_gaps = _dedupe_gap_skills(gap_skills or [])

    role_payload = _load_role_payload(role) if role in ROLE_LABELS else None
    clarification_needed = role == "unclear" or category == "unclear" or blocker == "unclear"

    if role == "unclear":
        title = "Rencana Aksi 2 Minggu untuk Menentukan Arah Karier"
    else:
        role_name = role_payload.get("display_name", _display_role(role)) if role_payload else _display_role(role)
        title = f"Rencana Aksi 4 Minggu - {role_name}"

    raw_steps: List[Dict[str, str]] = [
        _kickoff_step(role),
        _foundation_step(role, level),
        _blocker_step(blocker, role),
    ]

    if normalized_gaps:
        raw_steps.extend(_gap_steps(role, role_payload, normalized_gaps, max_steps=2))
    else:
        raw_steps.append(_fallback_execution_step())

    # Keep plan lightweight for beginner execution.
    raw_steps.append(_closing_step())

    # Cap to 6 steps while preserving closing review as the final step.
    if len(raw_steps) > 6:
        raw_steps = raw_steps[:5] + [raw_steps[-1]]

    # Safety: ensure minimum 3 steps.
    while len(raw_steps) < 3:
        raw_steps.append(_fallback_execution_step())

    steps: List[Dict[str, Any]] = []
    for idx, step in enumerate(raw_steps, start=1):
        steps.append({"order": idx, **step})

    plan = {
        "planner_version": "action_plan_rule_v1",
        "input_snapshot": {
            "target_role": role,
            "problem_category": category,
            "current_level": level,
            "blocker_type": blocker,
            "gap_skills": normalized_gaps,
        },
        "clarification_needed": clarification_needed,
        "title": title,
        "steps": steps,
        "rationale": [
            "Plan uses deterministic templates aligned to role, level, and blocker.",
            "Gap skills are converted into targeted practice steps (max 2) to keep scope realistic.",
            "Plan always ends with a review step to keep weekly iteration consistent.",
        ],
    }

    plan["markdown_view"] = render_action_plan_markdown(plan)
    return plan
