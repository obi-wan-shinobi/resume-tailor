from dataclasses import dataclass
from pathlib import Path

from .base import ArtifactStore


@dataclass
class LocalFileStore(ArtifactStore):
    base_dir: Path = Path("artifacts")

    def get_local_path(self, job_id: str, filename: str) -> Path:
        """Return the full path to the file"""
        return self.base_dir / job_id / filename

    def write_artifact(self, job_id: str, filename: str, content: str) -> None:
        """Save a JSON artifact (e.g., jd_analysis.json, tailored.json)"""
        path = self.get_local_path(job_id, filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def write_pdf(self, job_id: str, filename: str, pdf_bytes: bytes) -> str:
        """Save the compiled PDF and return a URI/path to it."""
        path = self.get_local_path(job_id, filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pdf_bytes)
        return str(path)
