"""CLI-based agent backends — shell out to an LLM CLI tool that writes its
JSON response to a file.

Each backend (agy, claude, codex, ...) only needs to declare its default
model list and how to build the command line for a given prompt/model/output
path. The subprocess loop, model fallback, and file handling are shared here.
"""

import logging
import subprocess
import tempfile
from pathlib import Path

from resume_tailor.agents.base import Agent
from resume_tailor.agents.prompts import FILE_OUTPUT_INSTRUCTION


class CLIAgent(Agent):
    """Agent backend that shells out to a CLI tool.

    The CLI is expected to write its complete JSON response to a file path
    we provide (appended to the prompt via `FILE_OUTPUT_INSTRUCTION`). If a
    model fails, the next model in `self.models` is tried.
    """

    DEFAULT_MODELS: list[str] = []
    TIMEOUT = 300

    def __init__(self, models: list[str] | None = None):
        self.models = models or self.DEFAULT_MODELS

    def _build_command(self, prompt: str, model: str, output_path: Path) -> list[str]:
        """Build the subprocess command line for this backend."""
        raise NotImplementedError(
            f"{type(self).__name__} does not implement _build_command()."
        )

    def _run_once(self, prompt: str, model: str) -> str:
        """Run the CLI once for a single model and return the output file contents."""
        output_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        output_path = Path(output_file.name)
        output_file.close()
        output_path.unlink()  # the CLI must create this file itself

        try:
            full_prompt = prompt + FILE_OUTPUT_INSTRUCTION.format(output_path=output_path)
            cmd = self._build_command(full_prompt, model, output_path)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"{cmd[0]} failed with model {model} (exit {result.returncode}):\n{result.stderr}"
                )
            if not output_path.exists():
                raise RuntimeError(
                    f"Agent completed successfully but did not write to {output_path}.\n"
                    f"Stdout: {result.stdout[:500]}"
                )
            return output_path.read_text()
        finally:
            output_path.unlink(missing_ok=True)

    def _complete(self, prompt: str) -> str:
        last_error = None
        for model in self.models:
            try:
                return self._run_once(prompt, model)
            except Exception as e:
                logger = logging.getLogger("tailor")
                logger.warning(f"Model {model} failed: {e}. Trying next model if available...")
                last_error = e

        raise RuntimeError(f"All models failed. Last error: {last_error}")


class AgyAgent(CLIAgent):
    """Agent backend that shells out to the Antigravity CLI (agy)."""

    DEFAULT_MODELS = [
        "Claude Opus 4.6 (Thinking)",
        "Claude Sonnet 4.6 (Thinking)",
        "Gemini 3.1 Pro (High)",
    ]

    def _build_command(self, prompt: str, model: str, output_path: Path) -> list[str]:
        return ["agy", "--prompt", prompt, "--model", model]


class ClaudeAgent(CLIAgent):
    """Agent backend that shells out to the Claude Code CLI (claude)."""

    DEFAULT_MODELS = ["opus", "sonnet"]

    def _build_command(self, prompt: str, model: str, output_path: Path) -> list[str]:
        return [
            "claude",
            "-p",
            "--model", model,
            "--allowedTools", "Write",
            "--permission-mode", "acceptEdits",
            prompt,
        ]
