"""CLI entry point for resume-tailor."""

from pathlib import Path
from typing import Annotated

import typer

from resume_tailor.renderer import render

app = typer.Typer(
    name="resume-tailor",
    help="Generate tailored resumes from structured data and Typst templates.",
    no_args_is_help=True,
)


@app.callback()
def main():
    """
    Generate tailored resumes from structured data and Typst templates.
    """
    pass


@app.command(name="render")
def render_cmd(
    data: Annotated[
        Path,
        typer.Option(
            "--data",
            "-d",
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
    ] = Path("outputs/resume.pdf"),
) -> None:
    """Render a resume PDF from a JSON data file and a Typst template."""
    result = render(data_path=data, template_path=template, output_path=out)
    typer.echo(f"Resume written to {result}")
