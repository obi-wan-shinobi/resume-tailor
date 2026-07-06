"""Resume renderer — compiles a Typst template with injected JSON data into a PDF."""

from pathlib import Path

import typst


def render(
    data_path: Path,
    template_path: Path,
    *,
    root: Path | None = None,
) -> bytes:
    """Compile a Typst template with dynamic JSON data into a PDF.

    Args:
        data_path: Path to the JSON file containing dynamic resume content.
        template_path: Path to the Typst template file.
        root: Project root for Typst path resolution. Defaults to
              the parent of the template directory.

    Returns:
        The raw bytes of the compiled PDF.

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

    return pdf_bytes
