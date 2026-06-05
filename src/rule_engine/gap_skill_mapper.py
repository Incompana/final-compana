from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

POSITIVE_CUES = [
    "sudah",
    "bisa",
    "mampu",
    "pernah",
    "ya",
    "cukup paham",
]

NEGATIVE_CUES = [
    "belum",
    "tidak",
    "ga",
    "nggak",
    "kurang",
    "lemah",
    "sulit",
    "bingung",
    "belum yakin",
]

# Keyword map keeps matching logic explicit and editable.
ROLE_SKILL_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "cybersecurity": {
        "security_fundamentals": ["security", "keamanan", "cia", "2fa", "firewall"],
        "networking_basics": ["network", "jaringan", "ip", "tcp", "dns", "log login"],
        "linux_cli_basics": ["linux", "terminal", "command", "bash", "cli"],
        "vulnerability_assessment_basics": ["vulnerability", "scan", "owasp", "pentest"],
        "incident_reporting": ["incident", "report", "insiden", "laporan"],
    },
    "frontend": {
        "html_css_basics": ["html", "css", "layout", "responsive"],
        "javascript_basics": ["javascript", "js", "array", "object", "function"],
        "react_component_basics": ["react", "component", "props", "state"],
        "api_fetch_state": ["api", "fetch", "axios", "loading", "error state"],
        "ui_testing_basics": ["test", "testing", "jest", "rtl", "cypress"],
    },
    "backend": {
        "http_api_basics": ["http", "endpoint", "rest", "api", "request", "response"],
        "database_crud": ["database", "crud", "sql", "insert", "update", "delete"],
        "input_validation_auth_basics": ["validation", "auth", "jwt", "middleware"],
        "error_handling_logging": ["error handling", "logging", "log", "try catch"],
        "api_testing_basics": ["api test", "postman", "pytest", "integration test"],
    },
    "data_analyst": {
        "spreadsheet_sql_basics": ["spreadsheet", "excel", "sql", "group by", "join"],
        "data_cleaning": ["cleaning", "missing", "duplicate", "outlier", "rapihin data"],
        "exploratory_analysis": ["eda", "exploratory", "analisis awal", "trend"],
        "visualization_storytelling": ["visual", "chart", "dashboard", "grafik", "storytelling"],
        "metric_definition": ["metric", "kpi", "definisi metrik"],
    },
    "uiux": {
        "problem_framing": ["problem statement", "pain point", "user problem"],
        "wireframing_user_flow": ["wireframe", "user flow", "flow"],
        "visual_hierarchy_basics": ["hierarchy", "typography", "spacing", "layout visual"],
        "prototyping_basics": ["prototype", "figma", "clickable"],
        "usability_testing_basics": ["usability", "testing", "user test", "heuristic"],
    },
}

DETECTED_SKILL_ALIASES: Dict[str, str] = {
    "html": "html_css_basics",
    "css": "html_css_basics",
    "javascript": "javascript_basics",
    "js": "javascript_basics",
    "react": "react_component_basics",
    "api": "api_fetch_state",
    "sql": "spreadsheet_sql_basics",
    "excel": "spreadsheet_sql_basics",
    "figma": "prototyping_basics",
    "wireframe": "wireframing_user_flow",
    "cybersecurity": "security_fundamentals",
    "linux": "linux_cli_basics",
    "network": "networking_basics",
    "backend": "http_api_basics",
    "database": "database_crud",
}

BASE_DIR = Path(__file__).resolve().parents[2]
ROLE_KB_DIR = BASE_DIR / "knowledge_base" / "role_skill_task"


@lru_cache(maxsize=1)
def _load_role_index() -> Dict[str, str]:
    index_file = ROLE_KB_DIR / "index.json"
    payload = json.loads(index_file.read_text(encoding="utf-8"))
    role_to_file: Dict[str, str] = {}

    for row in payload.get("roles", []):
        role_id = str(row.get("role_id", "")).strip()
        file_value = str(row.get("file", "")).strip()
        if not role_id or not file_value:
            continue
        filename = Path(file_value).name
        role_to_file[role_id] = filename
    return role_to_file


@lru_cache(maxsize=16)
def _load_role_payload(role_id: str) -> Optional[Dict[str, Any]]:
    role_map = _load_role_index()
    filename = role_map.get(role_id)
    if not filename:
        return None

    role_file = ROLE_KB_DIR / filename
    if not role_file.exists():
        return None

    return json.loads(role_file.read_text(encoding="utf-8"))


def _normalize_text(text: str) -> str:
    lowered = str(text).lower().strip()
    return re.sub(r"\s+", " ", lowered)


def _extract_answer_texts(assessment_answers: Any) -> List[str]:
    texts: List[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
            return
        if isinstance(value, list):
            for child in value:
                visit(child)
            return
        if isinstance(value, bool):
            texts.append("ya" if value else "tidak")
            return
        if isinstance(value, (int, float)):
            texts.append(str(value))
            return
        texts.append(str(value))

    visit(assessment_answers)
    return [_normalize_text(text) for text in texts if str(text).strip()]


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _assessment_signal(answer_texts: List[str], skill_keywords: List[str]) -> Tuple[int, List[str], bool]:
    score = 0
    evidence: List[str] = []
    has_negative = False

    for answer in answer_texts:
        if not _contains_any(answer, skill_keywords):
            continue

        positive = _contains_any(answer, POSITIVE_CUES)
        negative = _contains_any(answer, NEGATIVE_CUES)

        if positive and not negative:
            score += 1
            evidence.append(f"Assessment indicates strength: '{answer[:120]}'")
        if negative:
            score -= 1
            has_negative = True
            evidence.append(f"Assessment indicates weakness: '{answer[:120]}'")

    # Clamp so one category cannot dominate by repeated wording.
    score = max(-1, min(1, score))
    return score, evidence, has_negative


def _detected_skill_ids(target_role: str, detected_skills: Optional[List[str]]) -> List[str]:
    if not detected_skills:
        return []

    allowed_skill_ids = set(ROLE_SKILL_KEYWORDS.get(target_role, {}).keys())
    mapped: List[str] = []

    for raw in detected_skills:
        token = _normalize_text(raw).replace("_", " ")

        # Direct alias mapping first.
        if token in DETECTED_SKILL_ALIASES:
            skill_id = DETECTED_SKILL_ALIASES[token]
            if skill_id in allowed_skill_ids:
                mapped.append(skill_id)
            continue

        # Fallback: keyword overlap against role skill keywords.
        for skill_id, keywords in ROLE_SKILL_KEYWORDS.get(target_role, {}).items():
            if any(keyword in token or token in keyword for keyword in keywords):
                mapped.append(skill_id)
                break

    # Keep deterministic order.
    return sorted(set(mapped))


def _suggest_task(role_payload: Dict[str, Any], skill_id: str) -> Optional[Dict[str, str]]:
    for task in role_payload.get("beginner_tasks", []):
        if skill_id in task.get("focus_skills", []):
            return {
                "task_id": str(task.get("task_id", "")),
                "title": str(task.get("title", "")),
            }
    return None


def _safe_unclear_response(target_role: str, current_level: str) -> Dict[str, Any]:
    return {
        "mapper_version": "gap_skill_mapper_rule_v1",
        "target_role": target_role,
        "current_level": current_level,
        "clarification_needed": True,
        "fallback_triggered": True,
        "safe_next_action": "ask_user_to_confirm_single_target_role",
        "missing_skills": [],
        "weak_skills": [],
        "prioritized_next_skills": [],
        "rationale": [
            "Target role is unclear or not found in knowledge base.",
            "Gap mapping is deferred to avoid misleading recommendations.",
        ],
    }


def map_gap_skills(
    target_role: str,
    current_level: str,
    assessment_answers: Any,
    detected_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Deterministic gap skill mapper.

    Inputs:
    - target_role
    - current_level
    - assessment_answers (any nested dict/list/scalar)
    - detected_skills (optional list from pretext)

    Output:
    - missing_skills
    - weak_skills
    - prioritized_next_skills
    plus deterministic rationale for explainability.
    """
    role_id = _normalize_text(target_role)

    if role_id in {"", "unclear", "unknown", "none"}:
        return _safe_unclear_response(target_role=target_role, current_level=current_level)

    role_payload = _load_role_payload(role_id)
    if role_payload is None:
        return _safe_unclear_response(target_role=target_role, current_level=current_level)

    answer_texts = _extract_answer_texts(assessment_answers)
    detected_ids = _detected_skill_ids(role_id, detected_skills)

    missing_skills: List[Dict[str, Any]] = []
    weak_skills: List[Dict[str, Any]] = []
    strong_skills: List[str] = []

    for row in role_payload.get("required_skills", []):
        skill_id = str(row.get("skill_id", "")).strip()
        skill_name = str(row.get("skill_name", skill_id)).strip()
        priority = str(row.get("priority", "low")).strip().lower()

        keywords = ROLE_SKILL_KEYWORDS.get(role_id, {}).get(skill_id, [skill_id.replace("_", " ")])

        signal_score = 0
        evidence: List[str] = []
        if skill_id in detected_ids:
            signal_score += 1
            evidence.append("Detected from pretext skill signal.")

        assessment_score, assessment_evidence, has_negative = _assessment_signal(answer_texts, keywords)
        signal_score += assessment_score
        evidence.extend(assessment_evidence)

        item = {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "priority": priority,
            "evidence": evidence,
        }

        if signal_score <= 0:
            item["reason"] = "No strong evidence that this skill is currently mastered."
            missing_skills.append(item)
        elif signal_score == 1:
            item["reason"] = "Partial evidence only; skill appears present but not stable yet."
            if has_negative:
                item["reason"] = "Mixed or weak evidence from assessment answers."
            weak_skills.append(item)
        else:
            strong_skills.append(skill_id)

    def sort_key(row: Dict[str, Any]) -> Tuple[int, str]:
        return PRIORITY_ORDER.get(str(row.get("priority", "low")), 99), str(row.get("skill_id", ""))

    missing_skills.sort(key=sort_key)
    weak_skills.sort(key=sort_key)

    prioritized_next_skills: List[Dict[str, Any]] = []
    for gap_type, rows in [("missing", missing_skills), ("weak", weak_skills)]:
        for row in rows:
            suggestion = _suggest_task(role_payload, row["skill_id"])
            prioritized_next_skills.append(
                {
                    "skill_id": row["skill_id"],
                    "skill_name": row["skill_name"],
                    "priority": row["priority"],
                    "gap_type": gap_type,
                    "reason": row["reason"],
                    "suggested_task": suggestion,
                }
            )

    prioritized_next_skills.sort(
        key=lambda row: (PRIORITY_ORDER.get(str(row.get("priority", "low")), 99), row.get("gap_type", ""))
    )
    prioritized_next_skills = prioritized_next_skills[:3]

    confidence = 0.35
    if role_payload.get("required_skills"):
        total_skills = len(role_payload.get("required_skills", []))
        strong_ratio = len(strong_skills) / max(1, total_skills)
        confidence = round(max(0.3, min(0.9, 0.45 + (0.45 * strong_ratio))), 2)

    return {
        "mapper_version": "gap_skill_mapper_rule_v1",
        "target_role": role_id,
        "current_level": current_level,
        "clarification_needed": False,
        "fallback_triggered": False,
        "confidence": confidence,
        "detected_skill_ids": detected_ids,
        "missing_skills": missing_skills,
        "weak_skills": weak_skills,
        "prioritized_next_skills": prioritized_next_skills,
        "rationale": [
            f"Loaded {len(role_payload.get('required_skills', []))} required skills from role knowledge base.",
            f"Assessment evidence fragments processed: {len(answer_texts)}.",
            f"Detected pretext skills used: {len(detected_ids)}.",
            "Skills are classified deterministically using keyword evidence and fixed thresholds.",
        ],
    }
