"""Resume renderer — compiles a Typst template with injected JSON data into a PDF."""

from pathlib import Path

import typst


def render(
    data_path: Path,
    template_path: Path,
    output_path: Path,
    *,
    root: Path | None = None,
) -> Path:
    """Compile a Typst template with dynamic JSON data into a PDF.

    Args:
        data_path: Path to the JSON file containing dynamic resume content.
        template_path: Path to the Typst template file.
        output_path: Path where the compiled PDF will be written.
        root: Project root for Typst path resolution. Defaults to
              the parent of the template directory.

    Returns:
        The output_path the PDF was written to.

    Raises:
        FileNotFoundError: If data_path or template_path do not exist.
        typst.TypstError: If the Typst compilation fails.
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Resolve root — Typst needs this to find files via absolute-looking paths.
    if root is None:
        root = template_path.resolve().parent.parent

    # The data path is passed as a sys.input so the template can load it
    # via json(sys.inputs.at("data")).  The template prepends "../" to
    # navigate from templates/ up to the project root.
    pdf_bytes: bytes = typst.compile(
        str(template_path),
        root=str(root),
        sys_inputs={"data": str(data_path)},
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_bytes)
    return output_path
