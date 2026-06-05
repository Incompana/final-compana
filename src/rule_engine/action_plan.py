from __future__ import annotations

from src.schemas import ActionPlanStep, CurrentLevel, GenerateActionPlanResponse, ProblemCategory


def _skill_title(skill: str) -> str:
    return skill.replace("_", " ").replace("-", " ").title()


def generate_action_plan(
    target_role: str,
    problem_category: ProblemCategory,
    current_level: CurrentLevel,
    gap_skills: list[str],
    time_budget_hours_per_week: int,
) -> GenerateActionPlanResponse:
    focus_skills = gap_skills[:3]
    if not focus_skills:
        focus_skills = ["execution_consistency"]

    steps: list[ActionPlanStep] = []
    hours_for_core = max(1, time_budget_hours_per_week // max(len(focus_skills), 1))

    steps.append(
        ActionPlanStep(
            step_number=1,
            title="Set a Single Weekly Outcome",
            objective="Convert broad career intent into one concrete weekly output.",
            tasks=[
                "Define one output you can ship in 7 days.",
                "Break the output into 3 small tasks.",
                "Block calendar time for task execution.",
            ],
            evidence_required=[
                "Written weekly outcome statement",
                "Task checklist with schedule",
            ],
            estimated_hours=max(1, time_budget_hours_per_week // 4),
        )
    )

    for index, skill in enumerate(focus_skills, start=2):
        steps.append(
            ActionPlanStep(
                step_number=index,
                title=f"Close Gap: {_skill_title(skill)}",
                objective=f"Build observable proof for {_skill_title(skill)}.",
                tasks=[
                    f"Complete one micro-task focused on {_skill_title(skill)}.",
                    "Capture what was hard and how you resolved it.",
                    "Share output for feedback using Compana evaluation flow.",
                ],
                evidence_required=[
                    "Task artifact (file, link, or screenshot)",
                    "Short reflection: what improved",
                ],
                estimated_hours=hours_for_core,
            )
        )

    steps.append(
        ActionPlanStep(
            step_number=len(steps) + 1,
            title="Review and Retarget",
            objective="Measure completion and adjust next week plan with one new priority.",
            tasks=[
                "Score your completion rate (done/total tasks).",
                "Identify the single highest-impact next gap.",
                "Prepare next weekly outcome based on feedback.",
            ],
            evidence_required=[
                "Completion score",
                "Next-week target statement",
            ],
            estimated_hours=max(1, time_budget_hours_per_week // 5),
        )
    )

    rationale = [
        f"Template plan generated for role {target_role}.",
        f"Problem category routing: {problem_category.value}.",
        f"Level calibration: {current_level.value}.",
        "Gap skills were converted into one step each to keep execution focused.",
    ]

    plan_title = f"4-Week Execution Baseline for {target_role.replace('_', ' ').title()}"
    return GenerateActionPlanResponse(plan_title=plan_title, steps=steps, rationale=rationale)
