from __future__ import annotations

from src.schemas import (
    AssessmentQuestion,
    BlockerType,
    CurrentLevel,
    GenerateAssessmentResponse,
    ProblemCategory,
)

CATEGORY_QUESTIONS = {
    ProblemCategory.ROLE_CLARITY: [
        ("role_goal", "Which role do you want to prioritize for the next 4 weeks?", "single_choice", []),
        (
            "role_reason",
            "Why is this role your top priority right now?",
            "text",
            [],
        ),
    ],
    ProblemCategory.SKILL_GAP: [
        (
            "skill_missing",
            "Which specific skill feels most missing today?",
            "text",
            [],
        ),
        (
            "skill_evidence",
            "What recent task exposed this gap?",
            "text",
            [],
        ),
    ],
    ProblemCategory.PORTFOLIO_EXECUTION: [
        (
            "portfolio_stage",
            "At which stage do you usually get stuck?",
            "single_choice",
            ["planning", "implementation", "polishing", "publishing"],
        ),
        (
            "portfolio_scope",
            "What is the smallest project output you can ship this week?",
            "text",
            [],
        ),
    ],
    ProblemCategory.INTERVIEW_PREP: [
        (
            "interview_type",
            "Which interview type is currently hardest?",
            "single_choice",
            ["behavioral", "technical", "case", "mixed"],
        ),
        (
            "interview_example",
            "Share one recent question you struggled to answer.",
            "text",
            [],
        ),
    ],
    ProblemCategory.JOB_SEARCH_STRATEGY: [
        (
            "job_target",
            "How many relevant jobs are you applying to per week?",
            "single_choice",
            ["0-2", "3-5", "6-10", "10+"],
        ),
        (
            "job_block",
            "What is the biggest friction in your application flow?",
            "text",
            [],
        ),
    ],
    ProblemCategory.UNCLEAR: [
        (
            "clarify_outcome",
            "What single career outcome do you want within the next 30 days?",
            "text",
            [],
        ),
        (
            "clarify_blocker",
            "Which blocker is most true right now?",
            "single_choice",
            ["knowledge", "execution", "confidence", "time", "focus"],
        ),
    ],
}

BLOCKER_OPTIONS = ["knowledge", "execution", "confidence", "time", "focus"]
LEVEL_OPTIONS = ["beginner", "intermediate", "advanced"]


def generate_assessment(
    problem_category: ProblemCategory,
    blocker_type: BlockerType,
    current_level: CurrentLevel,
) -> GenerateAssessmentResponse:
    category_questions = CATEGORY_QUESTIONS.get(problem_category, CATEGORY_QUESTIONS[ProblemCategory.UNCLEAR])
    questions: list[AssessmentQuestion] = []

    for question_id, prompt, answer_type, options in category_questions:
        questions.append(
            AssessmentQuestion(
                id=question_id,
                prompt=prompt,
                answer_type=answer_type,
                options=options,
                required=True,
            )
        )

    questions.append(
        AssessmentQuestion(
            id="primary_blocker",
            prompt="Confirm your main blocker to optimize your next action plan.",
            answer_type="single_choice",
            options=BLOCKER_OPTIONS,
            required=True,
        )
    )

    questions.append(
        AssessmentQuestion(
            id="current_level",
            prompt="Confirm your current level for this target role.",
            answer_type="single_choice",
            options=LEVEL_OPTIONS,
            required=True,
        )
    )

    questions.append(
        AssessmentQuestion(
            id="weekly_hours",
            prompt="How many hours per week can you consistently commit?",
            answer_type="single_choice",
            options=["2", "4", "6", "8", "10+"],
            required=True,
        )
    )

    rationale = [
        f"Category-first routing used for {problem_category.value}.",
        f"Blocker confirmation included for {blocker_type.value}.",
        f"Level calibration included for {current_level.value}.",
    ]
    return GenerateAssessmentResponse(questions=questions, rationale=rationale)
