from __future__ import annotations

from typing import Any, Dict, List

# Canonical label options aligned with current taxonomy.
ROLE_OPTIONS = ["cybersecurity", "frontend", "backend", "data_analyst", "uiux"]
BLOCKER_OPTIONS = [
    "no_roadmap",
    "no_portfolio",
    "no_foundation",
    "no_time",
    "no_confidence",
    "too_many_options",
    "unclear",
]

ROLE_FOUNDATION_OPTIONS = {
    "cybersecurity": [
        "paham konsep CIA triad dan contoh penerapannya",
        "pernah baca log sederhana (login/access)",
        "bisa pakai command Linux dasar",
        "belum yakin fondasi cybersecurity-ku",
    ],
    "frontend": [
        "bisa buat layout responsif HTML/CSS",
        "paham JavaScript dasar (array/object/function)",
        "pernah bikin komponen React sederhana",
        "belum yakin fondasi frontend-ku",
    ],
    "backend": [
        "paham alur request-response HTTP",
        "pernah buat endpoint CRUD sederhana",
        "bisa query database dasar",
        "belum yakin fondasi backend-ku",
    ],
    "data_analyst": [
        "bisa filter/agregasi data di spreadsheet",
        "bisa SQL SELECT, GROUP BY, JOIN dasar",
        "pernah buat visualisasi tren sederhana",
        "belum yakin fondasi data analyst-ku",
    ],
    "uiux": [
        "bisa bikin user flow sederhana",
        "pernah bikin wireframe low-fidelity",
        "paham prinsip visual hierarchy dasar",
        "belum yakin fondasi UIUX-ku",
    ],
}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _contains_multi_role_signal(pretext_analysis: Dict[str, Any]) -> bool:
    matched_roles = pretext_analysis.get("matched_signals", {}).get("roles", {})
    return len(matched_roles) > 1


def _is_ambiguous(
    pretext_analysis: Dict[str, Any],
    target_role: str,
    problem_category: str,
    blocker_type: str,
) -> bool:
    pretext_confidence = _as_float(pretext_analysis.get("confidence"), default=0.0)
    pretext_clarification_flag = bool(pretext_analysis.get("clarification_needed", False))

    return (
        pretext_clarification_flag
        or pretext_confidence < 0.6
        or target_role == "unclear"
        or problem_category == "unclear"
        or blocker_type == "unclear"
        or _contains_multi_role_signal(pretext_analysis)
    )


def _q(
    qid: str,
    prompt: str,
    answer_type: str,
    options: List[str],
    goal: str,
    why_asked: str,
) -> Dict[str, Any]:
    return {
        "id": qid,
        "prompt": prompt,
        "answer_type": answer_type,
        "options": options,
        "required": True,
        "goal": goal,
        "why_asked": why_asked,
    }


def _role_commitment_question(target_role: str) -> Dict[str, Any]:
    if target_role in ROLE_OPTIONS:
        return _q(
            qid="role_commitment_4_weeks",
            prompt=f"Untuk 4 minggu ke depan, apakah kamu mau fokus di role {target_role}?",
            answer_type="single_choice",
            options=[
                f"Ya, fokus di {target_role}",
                "Masih ingin bandingkan dengan role lain",
                "Belum yakin sama sekali",
            ],
            goal="role_clarity",
            why_asked="Konfirmasi komitmen role agar action plan tidak melebar.",
        )

    return _q(
        qid="role_pick_primary",
        prompt="Role utama mana yang paling ingin kamu fokuskan dalam 4 minggu ke depan?",
        answer_type="single_choice",
        options=ROLE_OPTIONS + ["belum_tahu"],
        goal="role_clarity",
        why_asked="Input masih ambigu, jadi sistem perlu menetapkan satu role prioritas.",
    )


def _foundation_question(target_role: str) -> Dict[str, Any]:
    role_key = target_role if target_role in ROLE_FOUNDATION_OPTIONS else "frontend"
    options = ROLE_FOUNDATION_OPTIONS.get(role_key, [])
    role_name = target_role if target_role in ROLE_FOUNDATION_OPTIONS else "target_role"

    return _q(
        qid="foundation_check",
        prompt=f"Dari daftar berikut, mana yang sudah bisa kamu lakukan sendiri untuk {role_name}?",
        answer_type="multi_choice",
        options=options,
        goal="foundation_check",
        why_asked="Sistem perlu mengukur fondasi aktual sebelum memberi task lanjutan.",
    )


def _blocker_question(blocker_type: str) -> Dict[str, Any]:
    return _q(
        qid="main_blocker_confirm",
        prompt="Pilih blocker utama kamu saat ini (pilih yang paling dominan).",
        answer_type="single_choice",
        options=BLOCKER_OPTIONS,
        goal="blocker_identification",
        why_asked=(
            "Blocker utama mengubah prioritas pertanyaan lanjutan dan rekomendasi task. "
            f"Sinyal awal: {blocker_type}."
        ),
    )


def _extra_questions(
    problem_category: str,
    blocker_type: str,
    target_role: str,
) -> List[Dict[str, Any]]:
    extras: List[Dict[str, Any]] = []

    if problem_category in {"direction_confused", "unclear"} or target_role == "unclear":
        extras.append(
            _q(
                qid="role_decision_anchor",
                prompt="Kriteria apa yang paling penting buat kamu saat memilih role?",
                answer_type="single_choice",
                options=[
                    "paling cepat dapat kerja",
                    "paling cocok dengan kemampuan sekarang",
                    "paling saya suka dikerjakan harian",
                    "gaji/peluang karier jangka panjang",
                ],
                goal="role_clarity",
                why_asked="Membantu memutuskan role saat user punya multi-interest.",
            )
        )

    if problem_category in {"beginner_lost", "skill_gap"}:
        extras.append(
            _q(
                qid="weakest_foundation_area",
                prompt="Bagian fondasi mana yang paling sering bikin kamu mentok?",
                answer_type="single_choice",
                options=[
                    "konsep dasar",
                    "praktik kecil berulang",
                    "mengerjakan project dari awal",
                    "tidak yakin bagian mana",
                ],
                goal="foundation_check",
                why_asked="Menentukan gap fondasi paling kritis untuk prioritas task awal.",
            )
        )

    if blocker_type == "no_portfolio":
        extras.append(
            _q(
                qid="portfolio_evidence_state",
                prompt="Bukti kerja yang saat ini paling siap kamu tunjukkan apa?",
                answer_type="single_choice",
                options=[
                    "belum ada project selesai",
                    "ada 1 project tapi belum rapi",
                    "ada >1 project tapi belum dipublikasikan",
                    "sudah ada portfolio link yang bisa dibagikan",
                ],
                goal="blocker_identification",
                why_asked="Memvalidasi apakah hambatan utamanya benar di bukti portfolio.",
            )
        )

    if blocker_type in {"no_time"} or problem_category == "overwhelmed":
        extras.append(
            _q(
                qid="weekly_time_budget",
                prompt="Berapa jam realistis per minggu yang bisa kamu jaga konsisten 4 minggu ke depan?",
                answer_type="single_choice",
                options=["<2", "2-4", "5-7", "8+"],
                goal="blocker_identification",
                why_asked="Menentukan kapasitas eksekusi nyata agar task tidak over-commit.",
            )
        )

    if blocker_type in {"no_confidence"} or problem_category == "confidence_issue":
        extras.append(
            _q(
                qid="confidence_trigger",
                prompt="Situasi apa yang paling sering bikin rasa tidak percaya diri muncul?",
                answer_type="single_choice",
                options=[
                    "saat mulai task baru",
                    "saat membandingkan diri dengan orang lain",
                    "saat harus submit/di-review",
                    "saat interview atau presentasi",
                ],
                goal="blocker_identification",
                why_asked="Menangkap trigger spesifik agar strategi feedback lebih tepat.",
            )
        )

    if blocker_type == "no_roadmap":
        extras.append(
            _q(
                qid="roadmap_gap_point",
                prompt="Bagian roadmap mana yang paling tidak jelas buat kamu sekarang?",
                answer_type="single_choice",
                options=[
                    "urutan belajar",
                    "milestone mingguan",
                    "kriteria lulus tiap tahap",
                    "cara evaluasi progress",
                ],
                goal="blocker_identification",
                why_asked="Mengunci titik kabur pada roadmap supaya next step bisa konkret.",
            )
        )

    if blocker_type == "too_many_options":
        extras.append(
            _q(
                qid="option_sprawl_source",
                prompt="Pilihan yang membuat kamu paling sulit fokus datang dari mana?",
                answer_type="single_choice",
                options=[
                    "terlalu banyak resource belajar",
                    "terlalu banyak role yang menarik",
                    "terlalu banyak ide project",
                    "input dari banyak mentor/teman",
                ],
                goal="blocker_identification",
                why_asked="Mengidentifikasi sumber distraksi utama untuk dipangkas.",
            )
        )

    return extras


def route_assessment_questions(
    pretext_analysis: Dict[str, Any],
    problem_category: str,
    target_role: str,
    current_level: str,
    blocker_type: str,
) -> Dict[str, Any]:
    """Return 3-5 rule-routed follow-up questions in frontend-ready JSON format."""
    clarification_needed = _is_ambiguous(
        pretext_analysis=pretext_analysis,
        target_role=target_role,
        problem_category=problem_category,
        blocker_type=blocker_type,
    )

    # Core trio: always collect role clarity + foundation + main blocker.
    questions: List[Dict[str, Any]] = [
        _role_commitment_question(target_role=target_role),
        _foundation_question(target_role=target_role),
        _blocker_question(blocker_type=blocker_type),
    ]

    decision_path: List[str] = [
        "core.role_clarity",
        "core.foundation_check",
        "core.blocker_identification",
    ]

    for extra in _extra_questions(problem_category, blocker_type, target_role):
        if len(questions) >= 5:
            break
        if any(existing["id"] == extra["id"] for existing in questions):
            continue
        questions.append(extra)
        decision_path.append(f"extra.{extra['id']}")

    # Safety: keep 3-5 only.
    questions = questions[:5]

    if len(questions) < 3:
        # Should not happen, but keep deterministic safety fallback.
        questions.append(
            _q(
                qid="fallback_goal_check",
                prompt="Apa outcome paling penting yang ingin kamu capai dalam 30 hari ke depan?",
                answer_type="text",
                options=[],
                goal="role_clarity",
                why_asked="Fallback agar rute assessment tetap bisa dilanjutkan.",
            )
        )

    return {
        "router_version": "question_router_rule_v1",
        "input_snapshot": {
            "problem_category": problem_category,
            "target_role": target_role,
            "current_level": current_level,
            "blocker_type": blocker_type,
            "pretext_confidence": _as_float(pretext_analysis.get("confidence"), 0.0),
        },
        "clarification_needed": clarification_needed,
        "decision_path": decision_path,
        "question_count": len(questions),
        "questions": questions,
    }
