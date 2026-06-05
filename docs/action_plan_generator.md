# Action Plan Generator (Rule-Based v1)

Module: `src/rule_engine/action_plan_generator.py`

## Purpose

Generate beginner-friendly action plans from:

- `target_role`
- `problem_category`
- `current_level`
- `blocker_type`
- `gap_skills`

The generator is deterministic and template-driven so output is explainable, testable, and easy to revise.

## Output Contract (JSON)

```json
{
  "planner_version": "action_plan_rule_v1",
  "input_snapshot": {
    "target_role": "frontend",
    "problem_category": "skill_gap",
    "current_level": "basic",
    "blocker_type": "no_portfolio",
    "gap_skills": ["react_component_basics", "api_fetch_state"]
  },
  "clarification_needed": false,
  "title": "Rencana Aksi 4 Minggu - Frontend",
  "steps": [
    {
      "order": 1,
      "title": "Tetapkan Outcome Minggu Ini",
      "task_suggestion": "...",
      "expected_output": "...",
      "success_criteria": "..."
    }
  ],
  "rationale": [
    "Plan uses deterministic templates aligned to role, level, and blocker."
  ],
  "markdown_view": "# Rencana Aksi ..."
}
```

## Step Rules

1. Always start with a kickoff step (`role focus` or `weekly outcome`).
2. Add one level-calibrated foundation step.
3. Add one blocker-specific step.
4. Convert up to 2 `gap_skills` into practical steps.
- If role/task mapping exists in KB, use that task suggestion.
- If not, generate a generic mini-practice step.
5. Always end with a weekly review step.
6. Keep total steps between 3 and 6.

## Markdown View

`markdown_view` is generated from the same JSON payload.
This keeps frontend and human review outputs consistent without extra formatting logic.

## Required Examples

See: `docs/action_plan_examples.json`

Examples included:

- cybersecurity beginner
- frontend user with no portfolio
- overwhelmed user with unclear role

## Known Limitations (v1)

- Templates are static and not personalized by detailed assessment history.
- Only top 2 gap skills are turned into steps to keep plans lightweight.
- Time allocation is not estimated numerically yet.
- If labels are weak (`unclear`), plan prioritizes clarification and safe next actions.
