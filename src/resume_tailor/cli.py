"""CLI entry point for resume-tailor."""

import json
from pathlib import Path
from typing import Annotated

import typer

from resume_tailor.renderer import render

app = typer.Typer(
    name="resume-tailor",
    help="Generate tailored resumes from structured data and Typst templates.",
    no_args_is_help=True,
)


@app.command(name="render")
def render_cmd(
    data: Annotated[
        Path,
        typer.Argument(
            help="Path to the JSON file containing dynamic resume content.",
            exists=True,
            dir_okay=False,
        ),
    ],
    template: Annotated[
        Path,
        typer.Option(
            "--template",
            "-t",
            help="Path to the Typst template file.",
            exists=True,
            dir_okay=False,
        ),
    ] = Path("templates/resume.typ"),
    out: Annotated[
        Path,
        typer.Option(
            "--out",
            "-o",
            help="Output path for the compiled PDF.",
        ),
    ] = Path("artifacts/resume.pdf"),
) -> None:
    """Render a resume PDF from a JSON data file and a Typst template."""
    pdf_bytes = render(data_path=data, template_path=template)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf_bytes)
    typer.secho(f"✓ Resume written to {out}", fg=typer.colors.GREEN)


@app.command(name="tailor")
def tailor(
    job: Annotated[
        Path,
        typer.Argument(
            help="Path to the job description file (text or markdown).",
            exists=True,
            dir_okay=False,
        ),
    ],
    profile: Annotated[
        Path,
        typer.Option(
            "--profile",
            "-p",
            help="Path to the candidate profile.",
            exists=True,
            dir_okay=False,
        ),
    ] = Path("sources/complete-profile.md"),
    template: Annotated[
        Path,
        typer.Option(
            "--template",
            "-t",
            help="Path to the Typst template file.",
            exists=True,
            dir_okay=False,
        ),
    ] = Path("templates/resume.typ"),
    baseline: Annotated[
        Path,
        typer.Option(
            "--baseline",
            "-b",
            help="Path to the baseline resume JSON.",
            exists=True,
            dir_okay=False,
        ),
    ] = Path("sources/baseline.json"),
    agent: Annotated[
        str,
        typer.Option(
            "--agent",
            "-a",
            help="Agent backend to use (agy, claude, mock).",
        ),
    ] = "agy",
    model: Annotated[
        list[str] | None,
        typer.Option(
            "--model",
            "-m",
            help="Specific LLM model(s) to use. Can be specified multiple times for fallbacks.",
        ),
    ] = None,
    save_artifacts: Annotated[
        bool,
        typer.Option(
            "--save-artifacts",
            help="Save intermediate artifacts (jd_analysis.json, profile_match.json, tailored.json).",
        ),
    ] = True,
) -> None:
    """Tailor a resume for a specific job description using an LLM agent."""
    import logging
    from resume_tailor.agents import get_agent
    from resume_tailor.storage.local import LocalFileStore

    job_id = job.stem
    store = LocalFileStore()
    
    # Set up file logger
    log_path = store.get_local_path(job_id, "tailor.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("tailor")
    logger.info(f"Starting pipeline for job: {job_id}")

    # Read inputs
    job_description = job.read_text()
    profile_text = profile.read_text()
    baseline_text = baseline.read_text()

    try:
        # Run the tailoring pipeline
        msg = f"Using agent: {agent}" + (f" (models: {model})" if model else " (models: default fallback sequence)")
        typer.secho(msg, fg=typer.colors.CYAN)
        logger.info(msg)
        
        agent_instance = get_agent(agent, models=model)
        result = agent_instance.tailor(job_description, profile_text, baseline_text)

        # Save intermediate artifacts alongside the output PDF
        if save_artifacts:
            store.write_artifact(job_id, "original_job.txt", job_description)

            if result.raw_prompt:
                store.write_artifact(job_id, "llm_prompt.txt", result.raw_prompt)
            if result.raw_response:
                store.write_artifact(job_id, "llm_raw_response.txt", result.raw_response)
                
            store.write_artifact(
                job_id, "jd_analysis.json", result.jd_analysis.model_dump_json(indent=2)
            )
            jd_path = store.get_local_path(job_id, 'jd_analysis.json')
            typer.secho(f"  -> JD analysis:   {jd_path}", fg=typer.colors.BLUE)
            logger.info(f"Saved JD analysis to {jd_path}")

            store.write_artifact(
                job_id,
                "profile_match.json",
                result.profile_match.model_dump_json(indent=2),
            )
            match_path = store.get_local_path(job_id, 'profile_match.json')
            typer.secho(f"  -> Profile match: {match_path}", fg=typer.colors.BLUE)
            logger.info(f"Saved Profile match to {match_path}")

        store.write_artifact(
            job_id, "tailored.json", result.tailored_resume.model_dump_json(indent=2)
        )
        tailored_path = store.get_local_path(job_id, "tailored.json")
        if save_artifacts:
            typer.secho(f"  -> Tailored JSON: {tailored_path}", fg=typer.colors.BLUE)
            logger.info(f"Saved Tailored JSON to {tailored_path}")

        # Copy the template alongside the tailored data so it can be hand-edited
        # and re-rendered later without touching the shared template.
        store.write_artifact(job_id, template.name, template.read_text())
        template_path = store.get_local_path(job_id, template.name)
        typer.secho(f"  -> Template copy: {template_path}", fg=typer.colors.BLUE)
        logger.info(f"Saved template copy to {template_path}")

        # Render the PDF
        pdf_bytes = render(
            data_path=tailored_path,
            template_path=template_path,
        )
        pdf_path = store.write_pdf(job_id, f"{job_id}_resume.pdf", pdf_bytes)
        typer.secho(f"✓ Resume written to {pdf_path}", fg=typer.colors.GREEN)
        logger.info(f"Pipeline completed successfully. PDF written to {pdf_path}")
    except Exception as e:
        typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        logger.exception("Pipeline failed with error")
        raise typer.Exit(1)
