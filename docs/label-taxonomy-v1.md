# Compana Label Taxonomy v1

This guide defines how to label one user input with four fields:

- `target_role`
- `problem_category`
- `current_level`
- `blocker_type`

Each field is single-label. Use `unclear` when evidence is insufficient.

## Labeling Principles

1. Label from explicit user evidence first, not assumptions.
2. Assign exactly one label per field.
3. If two labels are equally plausible and no tie-breaker applies, use `unclear`.
4. Prioritize the user's primary blocker now (next 30 days), not long-term history.
5. Keep label names unchanged for dataset consistency.

## 1) `target_role`

| Label | Use when | Example user text |
|---|---|---|
| `cybersecurity` | User targets security roles/tasks | "I want to move into SOC analyst work." |
| `frontend` | User targets UI/web client development | "I want to be a frontend dev and build React apps." |
| `backend` | User targets server/API/database development | "I am aiming for backend roles with Node and APIs." |
| `data_analyst` | User targets analytics/reporting/SQL roles | "I want a data analyst role and improve SQL." |
| `uiux` | User targets UX/UI design roles | "I want to become a UI/UX designer using Figma." |
| `unclear` | No clear role or many roles without commitment | "I am interested in many tech jobs but not sure." |

## 2) `problem_category`

| Label | Use when | Example user text |
|---|---|---|
| `beginner_lost` | New starter feels lost on where to begin | "I am totally new and have no idea what first step to take." |
| `direction_confused` | User cannot decide path/role/focus | "I cannot decide between frontend and data analyst." |
| `skill_gap` | User knows path but lacks specific skills | "I know I want backend but my SQL and API skills are weak." |
| `overwhelmed` | User has too much workload/info and cannot execute | "There is too much to do and I freeze every week." |
| `confidence_issue` | Main issue is anxiety/self-doubt/fear | "I avoid interviews because I feel not good enough." |
| `unclear` | Category cannot be decided from text | "Please help my career." |

## 3) `current_level`

| Label | Use when | Example user text |
|---|---|---|
| `zero` | No practical exposure yet | "I have never built a project before." |
| `basic` | Some fundamentals/practice, limited independence | "I finished tutorials and built one simple project." |
| `intermediate` | Can build independently, but still has targeted gaps | "I built several projects and now want to improve for interviews." |
| `unclear` | Experience level not stated | "I need guidance for next steps." |

## 4) `blocker_type`

| Label | Use when | Example user text |
|---|---|---|
| `no_roadmap` | Lacks clear plan/sequence | "I do not know the order of what to learn." |
| `no_portfolio` | Missing project evidence/portfolio | "I understand basics but have no portfolio to show." |
| `no_foundation` | Core fundamentals are missing | "I still do not understand basic JS and CSS concepts." |
| `no_time` | Time/schedule is the main blocker | "I work full-time and cannot find study time." |
| `no_confidence` | Confidence/fear blocks action | "I panic before coding tests and give up." |
| `too_many_options` | Too many choices prevent focus | "I keep switching between AI, web, and design." |
| `unclear` | Blocker not identifiable | "Something is wrong but I cannot explain it." |

## Edge-Case Guidance for Ambiguous Input

1. Multi-role mention without commitment:
Use `target_role=unclear` and likely `problem_category=direction_confused`.

2. Emotional + skill statements together:
Choose `problem_category=confidence_issue` only when fear/anxiety is dominant.
If lack of skill is dominant, choose `skill_gap`.

3. Overwhelmed vs no_time:
- `overwhelmed` = cognitive overload, too many tasks/info.
- `no_time` = schedule/resource constraint.
Use `problem_category=overwhelmed` and `blocker_type=no_time` together only when both are explicit.

4. Beginner_lost vs direction_confused:
- `beginner_lost` = does not know how to start.
- `direction_confused` = cannot choose among multiple directions.

5. Unclear short inputs:
For very short or vague text ("help", "confused"), assign `unclear` for uncertain fields.

## Inter-Annotator Consistency Rules

Use this sequence for every sample:

1. Read the full text once without labeling.
2. Highlight evidence phrases for each field.
3. Assign `target_role` first.
4. Assign `problem_category` using dominant current issue.
5. Assign `current_level` from explicit evidence only.
6. Assign `blocker_type` from root cause language.
7. If no direct evidence for a field, set `unclear`.

Tie-breakers:

- Direct first-person statements beat implied hints.
- Recent/now statements beat past history.
- If still tied after tie-breakers, use `unclear`.

Recommended annotation metadata per record:

```json
{
  "annotator_id": "ann_01",
  "evidence_spans": {
    "target_role": "frontend dev",
    "problem_category": "cannot decide",
    "current_level": "finished one tutorial",
    "blocker_type": "no roadmap"
  },
  "notes": "secondary mention of data analyst ignored because user commits to frontend"
}
```
