"""Prompt management for resumegpt."""

from importlib import resources
from typing import Iterable


def load_prompt_text() -> str:
    """Load the bundled prompt text."""
    try:
        prompt_path = resources.files("resumegpt.data").joinpath("prompt.txt")
        with prompt_path.open("r") as f:
            return f.read()
    except AttributeError:
        with resources.open_text("resumegpt.data", "prompt.txt") as f:
            return f.read()


def substitute_desired_positions(base_prompt: str, desired_positions: Iterable[str]) -> str:
    """Inject desired positions into the prompt."""
    positions = [p.strip() for p in desired_positions if str(p).strip()]
    suitable_positions_str = "(" + ", ".join(positions) + ")" if positions else "(suitable position for the candidate)"
    return base_prompt.replace("(suitable position for the candidate)", suitable_positions_str)
