"""HTTP service wrapping the tailor pipeline for use by external callers (e.g. job-intel)."""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from resume_tailor.agents import get_agent
from resume_tailor.renderer import render
from resume_tailor.storage.local import LocalFileStore

logger = logging.getLogger("resume_tailor.api")

DEFAULT_PROFILE = Path("sources/complete-profile.md")
DEFAULT_TEMPLATE = Path("templates/resume.typ")
DEFAULT_BASELINE = Path("sources/baseline.json")
DEFAULT_AGENT = "claude"

app = FastAPI(title="resume-tailor")


class TailorRequest(BaseModel):
    job_id: int | str
    company: str = ""
    title: str = ""
    description: str
    agent: str = DEFAULT_AGENT
    models: list[str] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tailor")
def tailor(req: TailorRequest) -> Response:
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="description must not be empty")

    job_id = f"job-{req.job_id}"
    store = LocalFileStore()

    profile_text = DEFAULT_PROFILE.read_text()
    baseline_text = DEFAULT_BASELINE.read_text()

    try:
        agent_instance = get_agent(req.agent, models=req.models)
        result = agent_instance.tailor(req.description, profile_text, baseline_text)

        store.write_artifact(job_id, "original_job.txt", req.description)
        store.write_artifact(
            job_id, "jd_analysis.json", result.jd_analysis.model_dump_json(indent=2)
        )
        store.write_artifact(
            job_id, "profile_match.json", result.profile_match.model_dump_json(indent=2)
        )
        store.write_artifact(
            job_id, "tailored.json", result.tailored_resume.model_dump_json(indent=2)
        )

        tailored_path = store.get_local_path(job_id, "tailored.json")
        pdf_bytes = render(data_path=tailored_path, template_path=DEFAULT_TEMPLATE)
        store.write_pdf(job_id, f"{job_id}_resume.pdf", pdf_bytes)
    except Exception as exc:
        logger.exception("Tailor pipeline failed for %s", job_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    filename = f"{job_id}_resume.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
