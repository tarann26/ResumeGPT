"""Shared helpers for filesystem paths and outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

DEFAULT_OUTPUT_DIR = Path("Output")


def ensure_output_dir(base_dir: str | Path | None = None) -> Path:
    """Ensure the output directory exists and return it."""
    directory = Path(base_dir) if base_dir is not None else DEFAULT_OUTPUT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def output_paths(base_dir: str | Path | None = None) -> Tuple[Path, Path]:
    """Return CSV and Excel paths under the output directory."""
    directory = ensure_output_dir(base_dir)
    return directory / "CVs_Info_Extracted.csv", directory / "CVs_Info_Extracted.xlsx"
