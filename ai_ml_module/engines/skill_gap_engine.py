"""Skill Gap Engine (Engine 5).

Implements generate_skill_gap(target_role, user_skill_profile) -> dict
using the official `role_skill_mapping.csv` contract.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional

import math

from ai_ml_module.utils.loader import load_role_skill_mapping, load_task_bank


PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def _to_int(v, default=9999):
  try:
    return int(v)
  except Exception:
    return default


def _status_label(score: int) -> str:
  if score <= 0:
    return "missing"
  if score == 1:
    return "weak"
  return "owned"


def _progress_percent(score: int) -> int:
  return max(0, min(100, int(score) * 50))


def _next_task_for_skill(target_role: str, skill_id: str, user_score: int) -> Optional[str]:
  try:
    df = load_task_bank()
  except Exception:
    return None
  rows = df[
    (df["target_role"].astype(str) == str(target_role))
    & (df["target_skill_id"].astype(str) == str(skill_id))
  ].copy()
  if rows.empty:
    return None

  level_order = {"beginner": 0, "basic": 1, "intermediate": 2, "advanced": 3}
  preferred = "beginner" if user_score <= 0 else "basic" if user_score == 1 else "intermediate"
  preferred_rank = level_order.get(preferred, 1)
  rows["_rank"] = rows["current_level"].astype(str).str.lower().map(level_order).fillna(1)
  rows["_distance"] = (rows["_rank"] - preferred_rank).abs()
  rows = rows.sort_values(["_distance", "_rank"])
  return str(rows.iloc[0].get("task_id") or "") or None


def _skill_evidence(
  target_role: str,
  skill_id: str,
  skill_name: str,
  user_score: int,
  priority: str,
) -> Dict[str, Any]:
  status = _status_label(user_score)
  progress = _progress_percent(user_score)
  priority_label = "prioritas tinggi" if priority == "high" else f"prioritas {priority}"
  next_task_id = _next_task_for_skill(target_role, skill_id, user_score)

  if status == "missing":
    reason = f"{skill_name} belum terlihat dari jawaban assessment atau task yang sudah dinilai."
    evidence = [
      "Score assessment untuk skill ini masih 0.",
      f"Skill ini termasuk {priority_label} untuk role {target_role}.",
      "Task latihan pertama perlu dikerjakan untuk membuat bukti skill.",
    ]
  elif status == "weak":
    reason = f"{skill_name} sudah ada sinyal dasar, tetapi belum cukup kuat untuk dianggap siap dipakai."
    evidence = [
      "Score assessment untuk skill ini berada di level dasar.",
      "Masih perlu task praktik agar output bisa dicek reviewer.",
      f"Skill ini tetap masuk daftar prioritas karena statusnya {priority_label}.",
    ]
  else:
    reason = f"{skill_name} sudah terkonfirmasi dari assessment atau hasil task sebelumnya."
    evidence = [
      "Score skill sudah mencapai level siap pakai.",
      "Skill bisa dipakai sebagai fondasi untuk task berikutnya.",
    ]

  return {
    "status": status,
    "score": progress,
    "progress": progress,
    "reason": reason,
    "evidence": evidence,
    "next_task_id": next_task_id,
  }


def generate_skill_gap(target_role: str, user_skill_profile: Dict[str, int]) -> Dict[str, Any]:
  """Generate skill gap report for a target role.

  Rules enforced:
  - Only skills present in `role_skill_mapping.csv` for the `target_role` are considered.
  - If a skill is missing in `user_skill_profile`, its score is 0.
  - readiness_score formula: sum(user_skill_score/2 * priority_weight) / sum(priority_weight)
    where user_skill_score in {0,1,2} and priority_weight maps high=3, medium=2, low=1.
  - priority_gap chosen according to rules in task description.
  """
  df = load_role_skill_mapping()
  # filter rows for target_role using role_id column
  if "role_id" not in df.columns:
    raise ValueError("role_skill_mapping missing 'role_id' column")
  role_rows = df[df["role_id"] == target_role]
  # ensure deterministic order by step_order
  if "step_order" in role_rows.columns:
    role_rows = role_rows.copy()
    role_rows["_step_order_int"] = role_rows["step_order"].apply(lambda x: _to_int(x))
    role_rows = role_rows.sort_values("_step_order_int")

  required_skills = []
  for _, r in role_rows.iterrows():
    sid = str(r.get("required_skill_id") or "").strip()
    sname = str(r.get("required_skill_name") or "").strip()
    priority = str(r.get("priority") or "").strip().lower() or "low"
    step_order = _to_int(r.get("step_order"))
    prerequisite = str(r.get("prerequisite_skill_id") or "").strip()
    if not sid:
      # skip rows without skill id to respect rule 1
      continue
    required_skills.append({"skill_id": sid, "skill_name": sname, "priority": priority, "step_order": step_order, "prerequisite_skill_id": prerequisite})

  # if no skills defined, return empty structured response
  if not required_skills:
    if target_role == "general_learner":
      return {
        "target_role": target_role,
        "skill_gap_summary": {"missing_count": 1, "weak_count": 0, "owned_count": 0},
        "missing_skills": [
          {
            "skill_id": "career_direction_clarity",
            "skill_name": "Career Direction Clarity",
            "priority": "high",
            "progress": 0,
            "score": 0,
            "status": "missing",
            "reason": "Arah role belum cukup jelas dari input user.",
            "evidence": ["Role masih general_learner.", "User perlu menjawab klarifikasi role dan blocker."],
            "next_task_id": None,
          }
        ],
        "weak_skills": [],
        "owned_skills": [],
        "readiness_score": 0.0,
        "priority_gap": "career_direction_clarity",
      }
    return {
      "target_role": target_role,
      "skill_gap_summary": {"missing_count": 0, "weak_count": 0, "owned_count": 0},
      "missing_skills": [],
      "weak_skills": [],
      "owned_skills": [],
      "readiness_score": 0.0,
      "priority_gap": None,
    }

  total_weight = 0.0
  weighted_score_sum = 0.0

  missing = []
  weak = []
  owned = []

  for s in required_skills:
    sid = s["skill_id"]
    pname = s["skill_name"]
    prio = s.get("priority", "low")
    weight = PRIORITY_WEIGHT.get(prio, 1)
    total_weight += weight
    user_score = int(user_skill_profile.get(sid, 0)) if user_skill_profile is not None else 0
    # clamp user_score to 0/1/2
    if user_score < 0:
      user_score = 0
    if user_score > 2:
      user_score = 2
    # accumulate weighted readiness component
    weighted_score_sum += (user_score / 2.0) * weight
    extra = _skill_evidence(target_role, sid, pname, user_score, prio)
    base = {
      "skill_id": sid,
      "skill_name": pname,
      "priority": prio,
      "step_order": s.get("step_order"),
      "prerequisite_skill_id": s.get("prerequisite_skill_id") or "",
      **extra,
    }

    # categorize
    if user_score == 0:
      missing.append(base)
    elif user_score == 1:
      weak.append(base)
    else:
      owned.append(base)

  readiness = 0.0
  if total_weight > 0:
    readiness = weighted_score_sum / total_weight
  # round to 2 decimal places
  readiness_rounded = round(readiness, 2)

  # determine priority_gap
  priority_gap: Optional[str] = None
  # choose missing with highest priority weight and earliest step_order
  if missing:
    # find highest priority among missing
    def prio_key(m):
      w = PRIORITY_WEIGHT.get(m.get("priority", "low"), 1)
      # find step_order from required_skills list
      step = next((x["step_order"] for x in required_skills if x["skill_id"] == m["skill_id"]), 9999)
      return (-w, step)

    missing_sorted = sorted(missing, key=prio_key)
    priority_gap = missing_sorted[0]["skill_id"]
  elif weak:
    def prio_key_weak(m):
      w = PRIORITY_WEIGHT.get(m.get("priority", "low"), 1)
      step = next((x["step_order"] for x in required_skills if x["skill_id"] == m["skill_id"]), 9999)
      return (-w, step)

    weak_sorted = sorted(weak, key=prio_key_weak)
    priority_gap = weak_sorted[0]["skill_id"]
  else:
    priority_gap = None

  summary = {"missing_count": len(missing), "weak_count": len(weak), "owned_count": len(owned)}

  return {
    "target_role": target_role,
    "skill_gap_summary": summary,
    "missing_skills": missing,
    "weak_skills": weak,
    "owned_skills": owned,
    "readiness_score": readiness_rounded,
    "priority_gap": priority_gap,
    "calculation": {
      "readiness_formula": "sum((skill_score/2) * priority_weight) / sum(priority_weight)",
      "priority_weight": PRIORITY_WEIGHT,
      "score_scale": {"missing": 0, "weak": 50, "owned": 100},
    },
  }


def run_skill_gap(input_data: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
  """Compatibility wrapper for pipeline usage.

  Expects input_data with keys: target_role, user_skill_profile
  """
  target_role = input_data.get("target_role")
  user_profile = input_data.get("user_skill_profile", {})
  return generate_skill_gap(target_role, user_profile)
