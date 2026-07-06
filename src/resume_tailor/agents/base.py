"""Agent base class — defines the interface all LLM backends must implement."""

import json
from abc import ABC

from resume_tailor.agents.prompts import TAILOR_SYSTEM_PROMPT, TAILOR_USER_PROMPT
from resume_tailor.schemas import (
    JDAnalysis,
    ProfileMatch,
    TailoredResume,
    TailorResult,
)


class Agent(ABC):
    """Base class for LLM agent backends.

    Each backend (agy, claude, codex, an API-based backend, etc.) implements
    `_complete()` — given a prompt, return the model's raw text output. The
    pipeline in `tailor()` builds the prompt, calls `_complete()`, and
    validates the result. This is the only method a backend must implement;
    how the text is produced (subprocess writing a file, stdout, an API
    response) is entirely up to the backend.
    """

    def _complete(self, prompt: str) -> str:
        """Send `prompt` to the backend and return its raw text output."""
        raise NotImplementedError(
            f"{type(self).__name__} does not implement _complete()."
        )

    def _build_prompt(self, job_description: str, profile: str, baseline: str) -> str:
        """Assemble the full tailoring prompt from its components."""
        return TAILOR_SYSTEM_PROMPT + "\n\n" + TAILOR_USER_PROMPT.format(
            job_description=job_description,
            profile=profile,
            baseline_json=baseline,
        )

    @staticmethod
    def _extract_json(raw_output: str) -> dict:
        """Extract a JSON object from LLM output that may contain extra text.

        Handles common cases: raw JSON, markdown-fenced JSON, JSON with
        leading/trailing text.
        """
        text = raw_output.strip()

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strip markdown fences
        if "```json" in text:
            text = text.split("```json", 1)[1]
            text = text.split("```", 1)[0].strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        if "```" in text:
            text = text.split("```", 1)[1]
            text = text.split("```", 1)[0].strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # Find first { and last }
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw_output[start : end + 1])
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Could not extract valid JSON from LLM output:\n{raw_output[:500]}"
        )

    def tailor(self, job_description: str, profile: str, baseline: str) -> TailorResult:
        """Run the full tailoring pipeline in a single LLM call."""
        prompt = self._build_prompt(job_description, profile, baseline)
        raw = self._complete(prompt)
        parsed = self._extract_json(raw)

        return TailorResult(
            jd_analysis=JDAnalysis.model_validate(parsed["jd_analysis"]),
            profile_match=ProfileMatch.model_validate(parsed["profile_match"]),
            tailored_resume=TailoredResume.model_validate(parsed["tailored_resume"]),
            raw_prompt=prompt,
            raw_response=raw,
        )
