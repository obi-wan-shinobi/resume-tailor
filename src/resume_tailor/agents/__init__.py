"""Agent backends for LLM-based resume tailoring."""

from resume_tailor.agents.base import Agent


def get_agent(backend: str, models: list[str] | None = None) -> Agent:
    """Get an agent instance by backend name.

    Args:
        backend: One of "agy", "claude", "mock".
        models: Optional list of LLM models to use (for fallbacks).

    Returns:
        An Agent instance.

    Raises:
        ValueError: If the backend is not supported.
    """
    if backend == "mock":
        from resume_tailor.agents.mock import MockAgent

        return MockAgent()
    elif backend == "agy":
        from resume_tailor.agents.cli import AgyAgent

        return AgyAgent(models=models)
    elif backend == "claude":
        from resume_tailor.agents.cli import ClaudeAgent

        return ClaudeAgent(models=models)
    else:
        raise ValueError(
            f"Unsupported agent backend: {backend!r}. "
            f"Available: agy, claude, mock"
        )


__all__ = ["Agent", "get_agent"]
