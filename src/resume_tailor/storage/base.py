from abc import ABC, abstractmethod
from pathlib import Path


class ArtifactStore(ABC):
    @abstractmethod
    def get_local_path(self, job_id: str, filename: str) -> Path:
        """Return the path to the file"""
        pass

    @abstractmethod
    def write_artifact(self, job_id: str, filename: str, content: str) -> None:
        """Save a JSON artifact (e.g., jd_analysis.json, tailored.json)"""
        pass

    @abstractmethod
    def write_pdf(self, job_id: str, filename: str, pdf_bytes: bytes) -> str:
        """Save the compiled PDF and return a URI/path to it."""
        pass
