"""Legacy entrypoint to run the full pipeline on a directory of resumes."""

from __future__ import annotations

import sys
from typing import Iterable, List

from .chatgpt_pipeline import CVsInfoExtractor
from .ocr_reader import CVsReader


def run_pipeline(cvs_directory_path: str, openai_api_key: str, desired_positions: Iterable[str]):
    """Process all PDFs in a directory and return extracted info."""
    cvs_reader = CVsReader(cvs_directory_path=cvs_directory_path)
    cvs_content_df = cvs_reader.read_cv()

    cvs_info_extractor = CVsInfoExtractor(
        cvs_df=cvs_content_df,
        openai_api_key=openai_api_key,
        desired_positions=[pos.strip() for pos in desired_positions if str(pos).strip()],
    )
    return cvs_info_extractor.extract_cv_info()


def main(argv: List[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    if len(args) < 3:
        print("Usage: python -m resumegpt.main <cvs_directory_path> <openai_api_key> \"Role1,Role2\"")
        return 1

    cvs_directory_path_arg, openai_api_key_arg, desired_positions_arg = args[0], args[1], args[2].split(",")
    desired_positions = [position.strip() for position in desired_positions_arg]

    run_pipeline(cvs_directory_path_arg, openai_api_key_arg, desired_positions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
