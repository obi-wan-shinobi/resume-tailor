"""Pydantic schemas for the tailoring pipeline."""

from pydantic import BaseModel


# ── JD Analysis ──────────────────────────────────────────────────────


class JDAnalysis(BaseModel):
    """Structured analysis of a job description."""

    role_title: str
    company: str = ""
    responsibilities: list[str] = []
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    domain_keywords: list[str] = []
    seniority: str = ""


# ── Profile Match ────────────────────────────────────────────────────


class ProfileMatch(BaseModel):
    """How well a candidate profile matches a job description."""

    strong_matches: list[str] = []
    partial_matches: list[str] = []
    missing_requirements: list[str] = []
    recommended_experience: list[str] = []
    recommended_projects: list[str] = []
    recommended_skills: list[str] = []


# ── Tailored Resume ─────────────────────────────────────────────────


class ExperienceEntry(BaseModel):
    """A single experience entry in the tailored resume."""

    company: str
    role: str
    dates: str
    location: str
    bullets: list[str]


class ProjectEntry(BaseModel):
    """A single project entry in the tailored resume."""

    name: str
    kind: str
    url: str
    bullets: list[str]


class TailoredResume(BaseModel):
    """Dynamic resume content shaped for the Typst template.

    This is the JSON contract between the LLM pipeline and the renderer.
    It contains only the dynamic sections — static sections (name, education,
    publications, languages) live in the Typst template itself.
    """

    summary: str = ""
    experience: list[ExperienceEntry]
    skills: dict[str, list[str]]
    projects: list[ProjectEntry]


# ── Pipeline Result ──────────────────────────────────────────────────


class TailorResult(BaseModel):
    """Full result of a tailoring run, including all intermediate artifacts."""

    jd_analysis: JDAnalysis
    profile_match: ProfileMatch
    tailored_resume: TailoredResume
    raw_prompt: str | None = None
    raw_response: str | None = None
