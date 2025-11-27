import argparse
import json
import os
import sys
from typing import List, Optional

from .core import process_resume_file


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract structured info from a resume PDF.")
    parser.add_argument("pdf_path", help="Path to the resume PDF file.")
    parser.add_argument(
        "desired_positions",
        help="Comma-separated list of desired positions (e.g., 'Data Scientist,Data Engineer').",
    )
    parser.add_argument(
        "--openai-api-key",
        dest="openai_api_key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key (or set OPENAI_API_KEY).",
    )
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="OpenAI chat model to use (default: gpt-3.5-turbo).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (default: 0.0).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if not args.openai_api_key:
        print("Error: OpenAI API key not provided (use --openai-api-key or OPENAI_API_KEY).", file=sys.stderr)
        return 1

    desired_positions = [p.strip() for p in args.desired_positions.split(",") if p.strip()]
    try:
        result = process_resume_file(
            args.pdf_path,
            desired_positions,
            openai_api_key=args.openai_api_key,
            model=args.model,
            temperature=args.temperature,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    json_output = json.dumps(result, indent=2 if args.pretty else None)
    print(json_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
