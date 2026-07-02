# Resume Tailor

Resume Tailor is a standalone tool for generating job-specific resumes from a structured candidate profile, a resume template, and a job description.

The project is designed to be independent of any job board, application tracker, or recruitment platform. It should be possible to use Resume Tailor either:

- manually by pasting a job description and generating a resume, or
- as a component integrated into a larger job intelligence or application management system.

The primary output of the system is a tailored resume in PDF format.

---

## Goals

### Primary Goals

- Generate high-quality tailored resumes for specific job descriptions.
- Maintain a single source of truth for candidate information.
- Avoid hallucinating experience, skills, or achievements.
- Produce deterministic, reproducible resume documents.
- Support multiple LLM backends (Claude Code, Gemini CLI, Codex, etc.).
- Remain usable as a standalone command-line application.

### Non-Goals

- Tracking job applications.
- Managing interview pipelines.
- Scraping job boards.
- Acting as an applicant tracking system (ATS).

These responsibilities belong in external systems.

---

## Design Principles

### 1. Profile-First

The candidate profile is the source of truth.

LLMs may:

- select information,
- reorder information,
- rewrite information for clarity,

but they may not invent facts that do not exist in the profile.

### 2. Structured Outputs

LLMs should never directly generate PDFs.

Instead, each stage produces structured artifacts that can be inspected, validated, and modified.

Example:

```text
Job Description
    ↓
JD Analysis
    ↓
Profile Match
    ↓
Resume Plan
    ↓
Typst Renderer
    ↓
PDF
```

### 3. LLM Independence

The system should not depend on any single model provider.

All LLM interactions occur through a common agent interface.

Possible backends:

- Claude Code
- Gemini CLI
- Codex
- Local models
- Mock implementations

### 4. Human Inspectability

Every intermediate artifact should be readable.

A user should be able to inspect:

- extracted requirements,
- matched experiences,
- selected projects,
- generated summaries,
- final resume structure.

### 5. Deterministic Rendering

Resume rendering should not depend on an LLM.

Rendering should be performed by Typst using structured resume data.

---

## High-Level Architecture

```text
┌─────────────────┐
│ Job Description │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   JD Analysis   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Profile Matching│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Resume Plan    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Typst Renderer  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Resume PDF    │
└─────────────────┘
```

---

## Inputs

### Job Description

A job description may be provided as:

- plain text
- markdown
- copied content from a job board

Example:

```text
Machine Learning Platform Engineer

Responsibilities:
- Build ML infrastructure
- Productionize machine learning systems
- Support model deployment
```

### Candidate Profile

The candidate profile contains all information that may appear on a resume.

Example:

```yaml
experience:
  - company: Dalton Maag
    role: Software Developer
    bullets:
      - Built internal automation tools
      - Developed monitoring and observability features

projects:
  - name: Master's Thesis
    bullets:
      - Studied training dynamics of neural networks
```

### Resume Template

A Typst template defines visual layout and formatting.

Templates should not contain tailoring logic.

---

## Intermediate Artifacts

### JD Analysis

Extracted information from the job description.

Example:

```json
{
  "role_title": "Machine Learning Platform Engineer",
  "required_skills": ["Python", "Machine Learning", "Docker"]
}
```

### Profile Match

Mapping between requirements and profile evidence.

Example:

```json
{
  "strong_matches": ["Python", "Machine Learning"],
  "recommended_projects": ["Master's Thesis"]
}
```

### Resume Plan

Structured representation of the final resume.

Example:

```json
{
  "summary": "...",
  "experience": [...],
  "projects": [...],
  "skills": [...]
}
```

The renderer consumes this artifact.

---

## Agent System

Resume Tailor uses an agent abstraction layer.

```text
Pipeline
    │
    ▼
Agent Interface
    │
    ├── Claude Code
    ├── Gemini CLI
    ├── Codex
    ├── Local Model
    └── Mock Agent
```

Each pipeline stage may use a different backend.

Example:

```yaml
agents:
  parse_jd: gemini_cli
  match_profile: claude_code
  generate_plan: codex
```

---

## Typical Workflow

### Manual Usage

```text
Paste Job Description
        ↓
Generate Resume
        ↓
Review Resume Plan
        ↓
Export PDF
```

### Integrated Usage

```text
Job Intelligence System
          ↓
    Job Description
          ↓
     Resume Tailor
          ↓
      Resume PDF
```

---

## Future Extensions

### Cover Letters

```text
Job Description
        +
Candidate Profile
        ↓
Cover Letter
```

### Recruiter Messages

```text
Job Description
        ↓
Personalized Outreach Message
```

### Application Packages

```text
Resume
Cover Letter
Recruiter Message
Portfolio Links
```

### Multi-Resume Profiles

Support multiple profile variants:

```text
Research
Backend Engineering
ML Engineering
ML Platform
Data Science
```

generated from a shared profile source.

---

## Roadmap

### Phase 1

- Define schemas
- Define profile format
- Create Typst template
- Implement PDF rendering

### Phase 2

- Implement JD analysis
- Implement profile matching
- Implement resume plan generation

### Phase 3

- Add Claude Code integration
- Add Gemini CLI integration
- Add Codex integration

### Phase 4

- Add cover letter generation
- Add profile management
- Add API server

---

## Philosophy

Resume Tailor is not an LLM wrapper.

It is a document generation pipeline that uses LLMs as interchangeable components within a structured, inspectable, and reproducible workflow.

The candidate profile remains the source of truth, and all generated documents should be traceable back to information explicitly contained in that profile.

## API Contracts

Resume Tailor should expose the same core functionality through both a CLI and, later, an HTTP API.

The CLI is the first-class interface for the MVP. The HTTP API should be a thin wrapper around the same pipeline functions.

---

## CLI Contract

### Render Existing Resume Plan

```bash
resume-tailor render \
  --plan examples/resume_plan.json \
  --template templates/resume.typ \
  --out outputs/resume.pdf
```

Inputs:

- `resume_plan.json`
- `resume.typ`

Outputs:

- `resume.pdf`

No LLM is used in this command.

---

### Parse Job Description

```bash
resume-tailor parse-jd \
  --job examples/job.md \
  --out outputs/jd_analysis.json \
  --agent gemini_cli
```

Inputs:

- raw job description

Outputs:

- structured job description analysis

---

### Match Profile Against Job

```bash
resume-tailor match-profile \
  --jd outputs/jd_analysis.json \
  --profile examples/profile.yaml \
  --out outputs/profile_match.json \
  --agent claude_code
```

Inputs:

- `jd_analysis.json`
- `profile.yaml`

Outputs:

- `profile_match.json`

---

### Generate Resume Plan

```bash
resume-tailor generate-plan \
  --jd outputs/jd_analysis.json \
  --match outputs/profile_match.json \
  --profile examples/profile.yaml \
  --out outputs/resume_plan.json \
  --agent codex
```

Inputs:

- `jd_analysis.json`
- `profile_match.json`
- `profile.yaml`

Outputs:

- `resume_plan.json`

---

### Full Tailoring Pipeline

```bash
resume-tailor tailor \
  --job examples/job.md \
  --profile examples/profile.yaml \
  --template templates/resume.typ \
  --out outputs/resume.pdf \
  --config resume-tailor.yaml
```

Inputs:

- job description
- candidate profile
- resume template
- agent configuration

Outputs:

- `jd_analysis.json`
- `profile_match.json`
- `resume_plan.json`
- `resume.pdf`

---

## Python API Contract

The CLI should call a Python API internally.

Example:

```python
from pathlib import Path
from resume_tailor.pipeline import tailor_resume

result = tailor_resume(
    job_path=Path("examples/job.md"),
    profile_path=Path("examples/profile.yaml"),
    template_path=Path("templates/resume.typ"),
    output_path=Path("outputs/resume.pdf"),
    config_path=Path("resume-tailor.yaml"),
)
```

Expected result:

```python
TailorResult(
    jd_analysis_path=Path("outputs/jd_analysis.json"),
    profile_match_path=Path("outputs/profile_match.json"),
    resume_plan_path=Path("outputs/resume_plan.json"),
    pdf_path=Path("outputs/resume.pdf"),
)
```

---

## Future HTTP API Contract

The HTTP API should be added later, after the CLI pipeline is stable.

### `POST /v1/tailor`

Generate a tailored resume from raw inputs.

Request:

```json
{
  "job_description": "...",
  "profile": {
    "name": "Candidate Name",
    "experience": [],
    "projects": [],
    "skills": []
  },
  "template_id": "default",
  "agent_config": {
    "parse_jd": "gemini_cli",
    "match_profile": "claude_code",
    "generate_plan": "codex"
  }
}
```

Response:

```json
{
  "run_id": "run_123",
  "status": "completed",
  "artifacts": {
    "jd_analysis": "/artifacts/run_123/jd_analysis.json",
    "profile_match": "/artifacts/run_123/profile_match.json",
    "resume_plan": "/artifacts/run_123/resume_plan.json",
    "resume_pdf": "/artifacts/run_123/resume.pdf"
  }
}
```

---

### `POST /v1/parse-jd`

Request:

```json
{
  "job_description": "...",
  "agent": "gemini_cli"
}
```

Response:

```json
{
  "role_title": "Machine Learning Platform Engineer",
  "company": "Picnic",
  "responsibilities": [],
  "required_skills": [],
  "preferred_skills": [],
  "domain_keywords": [],
  "seniority": "mid"
}
```

---

### `POST /v1/match-profile`

Request:

```json
{
  "jd_analysis": {
    "role_title": "Machine Learning Platform Engineer",
    "required_skills": []
  },
  "profile": {
    "experience": [],
    "projects": [],
    "skills": []
  },
  "agent": "claude_code"
}
```

Response:

```json
{
  "strong_matches": [],
  "partial_matches": [],
  "missing_requirements": [],
  "recommended_experience": [],
  "recommended_projects": [],
  "recommended_skills": []
}
```

---

### `POST /v1/generate-plan`

Request:

```json
{
  "jd_analysis": {},
  "profile_match": {},
  "profile": {},
  "agent": "codex"
}
```

Response:

```json
{
  "name": "Candidate Name",
  "summary": "...",
  "experience": [],
  "projects": [],
  "education": [],
  "skills": []
}
```

---

### `POST /v1/render`

Render a resume plan into a PDF.

Request:

```json
{
  "resume_plan": {},
  "template_id": "default"
}
```

Response:

```json
{
  "status": "completed",
  "resume_pdf": "/artifacts/run_123/resume.pdf"
}
```

This endpoint should not call an LLM.

---

## Artifact Contract

Every full tailoring run should create a run directory:

```text
outputs/
  runs/
    run_123/
      input_job.md
      input_profile.yaml
      jd_analysis.json
      profile_match.json
      resume_plan.json
      resume.typ
      resume.pdf
      metadata.json
```

`metadata.json` should contain:

```json
{
  "run_id": "run_123",
  "created_at": "2026-06-15T20:30:00Z",
  "agents": {
    "parse_jd": "gemini_cli",
    "match_profile": "claude_code",
    "generate_plan": "codex"
  },
  "template": "default",
  "status": "completed"
}
```

---

## Error Contract

Errors should be structured.

Example:

```json
{
  "status": "failed",
  "stage": "generate_plan",
  "error_type": "schema_validation_error",
  "message": "Generated resume_plan.json did not match the expected schema.",
  "artifact_path": "outputs/runs/run_123/resume_plan.invalid.json"
}
```

Common error types:

- `agent_execution_error`
- `schema_validation_error`
- `missing_input_error`
- `render_error`
- `configuration_error`
- `unsupported_agent_error`

---

## Agent Contract

All agent backends should implement the same interface.

```python
class Agent:
    def run(self, task: AgentTask) -> AgentResult:
        ...
```

```python
class AgentTask:
    stage: str
    prompt: str
    input_files: list[Path]
    output_file: Path
    schema_file: Path | None
```

```python
class AgentResult:
    stage: str
    output_file: Path
    raw_output_file: Path | None
    success: bool
```

Agents are responsible for producing files.

The pipeline is responsible for validating those files.
