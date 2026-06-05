# Gap Skill Mapper (Rule-Based v1)

Module: `src/rule_engine/gap_skill_mapper.py`

## Purpose

Deterministically map skill gaps using:

- `target_role`
- `current_level`
- `assessment_answers`
- optional `detected_skills` from pretext

Knowledge source:

- `knowledge_base/role_skill_task/*.json`

## Output Structure (JSON)

```json
{
  "mapper_version": "gap_skill_mapper_rule_v1",
  "target_role": "frontend",
  "current_level": "basic",
  "clarification_needed": false,
  "fallback_triggered": false,
  "confidence": 0.63,
  "detected_skill_ids": ["html_css_basics", "javascript_basics"],
  "missing_skills": [
    {
      "skill_id": "api_fetch_state",
      "skill_name": "API Fetch and State Handling",
      "priority": "medium",
      "evidence": [],
      "reason": "No strong evidence that this skill is currently mastered."
    }
  ],
  "weak_skills": [
    {
      "skill_id": "react_component_basics",
      "skill_name": "React Component Basics",
      "priority": "medium",
      "evidence": ["Detected from pretext skill signal."],
      "reason": "Partial evidence only; skill appears present but not stable yet."
    }
  ],
  "prioritized_next_skills": [
    {
      "skill_id": "api_fetch_state",
      "skill_name": "API Fetch and State Handling",
      "priority": "medium",
      "gap_type": "missing",
      "reason": "No strong evidence that this skill is currently mastered.",
      "suggested_task": {
        "task_id": "fe_task_03",
        "title": "Daftar Data dari API Publik"
      }
    }
  ],
  "rationale": [
    "Loaded 5 required skills from role knowledge base.",
    "Assessment evidence fragments processed: 4.",
    "Detected pretext skills used: 3.",
    "Skills are classified deterministically using keyword evidence and fixed thresholds."
  ]
}
```

## Deterministic Rules

1. Parse role from KB file by `target_role`.
2. Flatten `assessment_answers` into plain text fragments.
3. Map `detected_skills` into role skill IDs via fixed alias table.
4. For each required skill:
- score +1 when detected from pretext skill signal,
- score +1/-1 from positive/negative assessment cues,
- classify:
  - `score <= 0` -> `missing_skills`
  - `score == 1` -> `weak_skills`
  - `score >= 2` -> treated as strong and omitted from gap lists.
5. Prioritize next skills by priority (`high -> medium -> low`), then gap type.

## Safe Response Rule

If `target_role` is `unclear` or not in KB:

- `clarification_needed = true`
- `fallback_triggered = true`
- return empty gap lists
- set `safe_next_action = ask_user_to_confirm_single_target_role`

This prevents misleading recommendations when role intent is not settled.
