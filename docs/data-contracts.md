# AI Service Data Contracts

All contracts are strict and schema-first through Pydantic models in `src/schemas.py`.

## `POST /analyze-pretext`

Request:

```json
{
  "user_id": "optional-user-id",
  "text": "I want to become a frontend developer but I keep getting stuck in portfolio projects.",
  "recent_context": []
}
```

Response:

```json
{
  "input_text": "...",
  "normalized_text": "...",
  "pretext_summary": "...",
  "signals": {
    "emotion": "distressed",
    "urgency": "normal"
  },
  "classification": {
    "target_role": "frontend_developer",
    "problem_category": "portfolio_execution",
    "current_level": "unclear",
    "blocker_type": "execution",
    "confidence": 0.75,
    "reasons": ["..."],
    "fallback_triggered": false,
    "clarification_prompt": null
  },
  "next_action": "generate_assessment"
}
```

## `POST /generate-assessment`

Request:

```json
{
  "target_role": "frontend_developer",
  "problem_category": "portfolio_execution",
  "current_level": "beginner",
  "blocker_type": "execution"
}
```

Response:

```json
{
  "questions": [
    {
      "id": "portfolio_stage",
      "prompt": "At which stage do you usually get stuck?",
      "answer_type": "single_choice",
      "options": ["planning", "implementation", "polishing", "publishing"],
      "required": true
    }
  ],
  "rationale": ["..."]
}
```

## `POST /map-gap-skills`

Request:

```json
{
  "target_role": "frontend_developer",
  "current_skills": ["html", "css"],
  "evidence": ["built a static landing page"]
}
```

Response:

```json
{
  "target_role": "frontend_developer",
  "current_skills_normalized": ["html css"],
  "missing_skills": [
    {
      "skill": "javascript_react",
      "priority": "high",
      "why_missing": "...",
      "example_task": "..."
    }
  ],
  "confidence": 0.5,
  "fallback_triggered": false,
  "rationale": ["..."]
}
```

## `POST /generate-action-plan`

Request:

```json
{
  "target_role": "frontend_developer",
  "problem_category": "portfolio_execution",
  "current_level": "beginner",
  "gap_skills": ["javascript_react", "api_integration"],
  "time_budget_hours_per_week": 6
}
```

Response:

```json
{
  "plan_title": "4-Week Execution Baseline for Frontend Developer",
  "steps": [
    {
      "step_number": 1,
      "title": "Set a Single Weekly Outcome",
      "objective": "...",
      "tasks": ["..."],
      "evidence_required": ["..."],
      "estimated_hours": 1
    }
  ],
  "rationale": ["..."]
}
```

## `POST /evaluate-task`

Request:

```json
{
  "target_role": "frontend_developer",
  "task_type": "resume_bullet",
  "submission_text": "Built a React dashboard used by 120 users and reduced report load time by 35%.",
  "rubric_id": null
}
```

Response:

```json
{
  "overall_score": 10,
  "max_score": 12,
  "status": "good",
  "criterion_scores": [
    {
      "criterion": "action_verb",
      "score": 3,
      "max_score": 3,
      "reason": "Starts with a strong action verb."
    }
  ],
  "feedback": ["..."],
  "next_attempt_focus": [],
  "confidence": 0.8,
  "fallback_triggered": false
}
```
