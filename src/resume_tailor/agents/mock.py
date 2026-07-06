"""Mock agent backend for testing without an LLM."""

import json

from resume_tailor.agents.base import Agent
from resume_tailor.schemas import (
    JDAnalysis,
    ProfileMatch,
    TailoredResume,
    TailorResult,
)


class MockAgent(Agent):
    """Returns the baseline resume with dummy JD analysis and profile match.

    Useful for testing the pipeline end-to-end without calling an LLM.
    """

    def tailor(self, job_description: str, profile: str, baseline: str) -> TailorResult:
        tailored_resume = (
            TailoredResume.model_validate(json.loads(baseline))
            if baseline
            else TailoredResume(experience=[], skills={}, projects=[])
        )

        return TailorResult(
            jd_analysis=JDAnalysis(
                role_title="Mock Role",
                company="Mock Company",
                responsibilities=["Responsibility 1"],
                required_skills=["Python"],
                seniority="mid",
            ),
            profile_match=ProfileMatch(
                strong_matches=["Python"],
                recommended_experience=["Mock Experience"],
            ),
            tailored_resume=tailored_resume,
        )
