# Resume Tailor

Resume Tailor is a standalone tool for generating job-specific resumes from a candidate profile and a Typst resume template.

Given a job description, it uses an LLM to select, reorder, and rewrite the dynamic sections of your resume (experience, skills, projects) while keeping static sections (name, education, publications) untouched. The output is a tailored resume PDF.

---

## Quickstart

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- At least one LLM CLI backend installed and authenticated: [`agy`](https://antigravity.google/) (Antigravity CLI) and/or [`claude`](https://claude.com/claude-code) (Claude Code CLI)

### Installation

```bash
uv sync
```

This installs all dependencies and the `resume-tailor` CLI in the project virtual environment.

### Render a resume

```bash
uv run resume-tailor render \
  examples/sample_tailored.json \
  --template templates/resume.typ \
  --out artifacts/resume.pdf
```

Or compile directly with Typst:

```bash
uv run typst compile templates/resume.typ \
  --input data=examples/sample_tailored.json \
  --root . \
  outputs/resume.pdf
```

Both produce the same PDF. The CLI wraps the Typst compilation with validation and convenience defaults.

### Tailor a resume for a job

```bash
uv run resume-tailor tailor \
  jobs/booking_ml_engineer.txt \
  --agent claude
```

This runs the full single-call LLM pipeline (JD analysis + profile matching + tailored resume generation in one prompt), validates the output against the schema, renders the PDF, and writes all intermediate artifacts under `artifacts/<job_id>/`.

---

## Goals

### Primary Goals

- Generate high-quality tailored resumes for specific job descriptions.
- Maintain a single source of truth for candidate information.
- Avoid hallucinating experience, skills, or achievements.
- Produce deterministic, reproducible resume documents.
- Support multiple LLM backends (Antigravity, Claude Code, Codex, etc.) interchangeably.
- Remain usable as a standalone command-line application.

### Non-Goals

- Tracking job applications.
- Managing interview pipelines.
- Scraping job boards.
- Acting as an applicant tracking system (ATS).

These responsibilities belong in external systems.

---

## Design

### Template-Driven Rendering

Resume Tailor uses a **Typst template with JSON data injection**. The template contains two kinds of content:

**Static sections** are hardcoded in the template and never change between applications:

- Name and contact information
- Education
- Publications
- Spoken languages

**Dynamic sections** are loaded from a JSON data file and tailored per job application:

- Experience (reorder roles, select/condense/rewrite bullets)
- Technical Skills (reorder categories, highlight relevant skills)
- Projects (select which to include, tailor bullets)
- Summary (optional, written per job)

The Typst template (`templates/resume.typ`) uses Typst's built-in `json()` function and scripting (`#for`, `#if`) to render dynamic content. No external templating engine (e.g. Jinja2) is needed.

### Dynamic Data Contract

The JSON data file — the output of the tailoring pipeline — has this shape:

```json
{
  "summary": "Optional tailored summary...",
  "experience": [
    {
      "company": "Company Name",
      "role": "Role Title",
      "dates": "Start – End",
      "location": "City, Country",
      "bullets": ["Bullet 1", "Bullet 2"]
    }
  ],
  "skills": {
    "Category": ["Skill 1", "Skill 2"]
  },
  "projects": [
    {
      "name": "Project Name",
      "kind": "Course Project",
      "url": "github.com/user/repo",
      "bullets": ["Bullet 1", "Bullet 2"]
    }
  ]
}
```

See `examples/sample_tailored.json` for a complete example, and `src/resume_tailor/schemas/__init__.py` for the Pydantic models (`JDAnalysis`, `ProfileMatch`, `TailoredResume`, `TailorResult`) that validate it.

### Profile-First

The candidate profile (`sources/complete-profile.md`) is the source of truth, and `sources/baseline.json` is the untailored dynamic-content baseline. LLMs may select, reorder, and rewrite information for clarity, but they may not invent facts that do not exist in the profile.

### Single-Call Pipeline

The tailoring pipeline makes a single LLM call:

```text
Job Description + Candidate Profile + Baseline JSON
                     ↓  LLM
               tailored.json (jd_analysis + profile_match + tailored_resume)
                     ↓  Typst
                  resume.pdf
```

The LLM receives the job description, the full candidate profile, and the baseline resume JSON in one prompt (`src/resume_tailor/agents/prompts.py`), and returns a single JSON object containing the JD analysis, profile match, and tailored resume together. Each piece is validated against its schema before the resume is rendered.

### Agent Architecture

Every backend implements one interface — `Agent._complete(prompt) -> str` — and the shared pipeline (`Agent.tailor()` in `src/resume_tailor/agents/base.py`) builds the prompt, calls `_complete()`, extracts/validates JSON, and returns a `TailorResult`. This keeps file-writing backends (CLIs) and future response-based backends (a direct API call) structurally identical — they only differ in *how* the raw text is produced.

```text
Agent (abstract: _complete(), _extract_json(), tailor())
  └── CLIAgent (subprocess + model-fallback loop + temp output file)
        ├── AgyAgent    — shells out to `agy`
        └── ClaudeAgent — shells out to `claude`
MockAgent (Agent)         — no LLM call, used for testing
```

`CLIAgent` appends a file-output instruction to the prompt, runs the CLI as a subprocess, and reads back the JSON file the CLI is instructed to write. If a model fails, it retries with the next model in the backend's fallback list. A concrete CLI backend only needs to declare `DEFAULT_MODELS` and `_build_command()`.

The agent backend is selected via the `--agent` flag (`agy`, `claude`, or `mock`). `codex` is a planned backend, not yet implemented.

---

## HTTP API

Resume Tailor also ships a thin FastAPI wrapper (`src/resume_tailor/api.py`) around the same tailoring pipeline, for use by external callers (e.g. job-intelligence-board) that want a tailored PDF over HTTP instead of a CLI invocation.

```bash
uv run resume-tailor-api
```

This starts a Uvicorn server on `0.0.0.0:8000`.

| Endpoint | Method | Description |
|----------|--------|--------------|
| `/health` | `GET` | Liveness check — returns `{"status": "ok"}` |
| `/tailor` | `POST` | Runs the tailor pipeline and returns the rendered PDF |

`POST /tailor` request body:

```json
{
  "job_id": "booking-ml-engineer",
  "company": "Booking.com",
  "title": "ML Engineer",
  "description": "Full job description text...",
  "agent": "claude",
  "models": null
}
```

`job_id`/`description` are required; `company`/`title` are informational only; `agent` defaults to `claude`; `models` optionally overrides the backend's default model fallback list. On success the response is the tailored resume PDF (`application/pdf`, `Content-Disposition: attachment`). Intermediate artifacts (`jd_analysis.json`, `profile_match.json`, `tailored.json`) are written to `artifacts/job-<job_id>/` via `LocalFileStore`, the same as the CLI's `tailor` command. Failures surface as `400` (empty description) or `500` (pipeline error) with a JSON `detail` message.

The API always uses the default profile (`sources/complete-profile.md`), template (`templates/resume.typ`), and baseline (`sources/baseline.json`) — there is no per-request override, unlike the CLI's `--profile`/`--template`/`--baseline` flags.

---

## Repository Layout

```text
resume-tailor/
├── src/resume_tailor/
│   ├── __init__.py          # CLI entry point (`main`)
│   ├── cli.py                # Typer CLI commands: `render`, `tailor`
│   ├── api.py                 # FastAPI wrapper (`/health`, `/tailor`)
│   ├── renderer.py           # Typst compilation wrapper
│   ├── schemas/               # Pydantic models for validation
│   ├── storage/               # Artifact storage (local filesystem)
│   └── agents/
│       ├── base.py            # `Agent` — pipeline + JSON extraction
│       ├── cli.py             # `CLIAgent`, `AgyAgent`, `ClaudeAgent`
│       ├── mock.py            # `MockAgent`
│       └── prompts.py         # Shared tailoring prompt + file-output instruction
├── templates/
│   └── resume.typ            # Typst template (static + dynamic)
├── sources/
│   ├── complete-profile.md   # Detailed candidate profile (source of truth)
│   ├── baseline.json         # Untailored baseline dynamic content
│   └── resume.tex            # Original LaTeX resume (reference)
├── examples/
│   ├── job.md                 # Example job description
│   └── sample_tailored.json  # Example tailored dynamic content
├── jobs/                      # Real job descriptions used for tailoring runs
├── artifacts/                 # Per-job run artifacts (gitignored)
├── pyproject.toml
└── README.md
```

### Template

The Typst template (`templates/resume.typ`) is a faithful port of the original LaTeX resume. It uses:

- **New Computer Modern** font (equivalent to LaTeX's `lmodern`)
- **Font Awesome** icons via the `@preview/fontawesome` Typst package
- **Link color** `#1F4E79` matching the LaTeX original

To edit the template, modify `templates/resume.typ` directly. Static content (name, education, etc.) is plaintext in the file. Dynamic sections use Typst's `#for` loops over the JSON data.

To make a section dynamic that is currently static, move its content from the template into the JSON data file and add a `#for` loop to render it.

---

## CLI Commands

### `render`

Render a resume PDF from a JSON data file and a Typst template. No LLM is used.

```bash
uv run resume-tailor render \
  examples/sample_tailored.json \
  --template templates/resume.typ \
  --out artifacts/resume.pdf
```

| Argument/Flag | Description | Default |
|---------------|-------------|---------|
| `DATA` | Path to the JSON data file | (required) |
| `--template`, `-t` | Path to the Typst template | `templates/resume.typ` |
| `--out`, `-o` | Output PDF path | `artifacts/resume.pdf` |

### `tailor`

Generate a tailored resume for a specific job description using an LLM agent.

```bash
uv run resume-tailor tailor \
  jobs/booking_ml_engineer.txt \
  --agent claude \
  --model opus
```

| Argument/Flag | Description | Default |
|---------------|-------------|---------|
| `JOB` | Path to the job description (text or markdown) | (required) |
| `--profile`, `-p` | Path to the candidate profile | `sources/complete-profile.md` |
| `--template`, `-t` | Path to the Typst template | `templates/resume.typ` |
| `--baseline`, `-b` | Path to the baseline resume JSON | `sources/baseline.json` |
| `--agent`, `-a` | Agent backend to use (`agy`, `claude`, `mock`) | `agy` |
| `--model`, `-m` | Specific model(s) to use; repeatable for fallbacks | backend's default list |
| `--save-artifacts` | Save intermediate artifacts (`jd_analysis.json`, `profile_match.json`, `tailored.json`) | `true` |

There is no `--out` flag on `tailor` — the output PDF and all artifacts are written to `artifacts/<job_id>/` automatically, where `<job_id>` is derived from the job file's stem.

---

## Artifacts

Every `tailor` run writes to `artifacts/<job_id>/`:

```text
artifacts/
  booking_ml_engineer/
    original_job.txt
    llm_prompt.txt
    llm_raw_response.txt
    jd_analysis.json
    profile_match.json
    tailored.json
    resume.typ
    booking_ml_engineer_resume.pdf
    tailor.log
```

`tailor.log` records per-run progress and any model-fallback warnings. `resume.typ` is a per-run copy of the template used to render that job's PDF, so it can be hand-edited and re-rendered later (via `render`) without touching the shared template in `templates/`.

---

## Roadmap

### Done

- Typst template with static/dynamic sections, JSON data contract, `render` command
- Tailored JSON schema (Pydantic validation)
- Single-call agent pipeline (`Agent` / `CLIAgent` base classes)
- `agy` and `claude` CLI backends, plus a `mock` backend for testing
- `tailor` CLI command with model fallback and artifact/logging support
- HTTP API server (`resume-tailor-api`) — thin FastAPI wrapper over the same agent pipeline, for use by job-intelligence-board

### Planned

- `codex` CLI backend
- Output quality evaluation
- Cover letter generation

---

## Philosophy

Resume Tailor is not an LLM wrapper.

It is a document generation pipeline that uses LLMs as interchangeable components within a structured, inspectable, and reproducible workflow.

The candidate profile remains the source of truth, and all generated documents should be traceable back to information explicitly contained in that profile.
