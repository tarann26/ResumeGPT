import json
import re
from io import BytesIO
from typing import Iterable, Optional

import openai
from PyPDF2 import PdfReader

from .prompts import load_prompt_text, substitute_desired_positions


class ResumeProcessingError(RuntimeError):
    """Raised when resume processing fails."""


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from a PDF represented as bytes."""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except Exception as exc:
        raise ResumeProcessingError(f"Unable to read PDF bytes: {exc}") from exc

    text_chunks: list[str] = []
    for page in reader.pages:
        text_chunks.append(page.extract_text() or "")
    raw_text = "\n".join(text_chunks)
    return re.sub(r"\n(?:\s*)", "\n", raw_text)


def _call_openai_chat(
    prompt: str,
    cv_content: str,
    *,
    model: str,
    temperature: float,
) -> str:
    completion_params = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": cv_content},
        ],
        "temperature": temperature,
    }
    response = openai.ChatCompletion.create(**completion_params)
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise ResumeProcessingError("Unexpected response from OpenAI") from exc


def process_resume(
    pdf_bytes: bytes,
    desired_positions: Iterable[str],
    *,
    openai_api_key: str,
    prompt_text: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.0,
) -> dict:
    """Process a resume PDF and return extracted info as a dict."""
    openai.api_key = openai_api_key

    base_prompt = prompt_text if prompt_text is not None else load_prompt_text()
    prompt = substitute_desired_positions(base_prompt, desired_positions)

    cv_content = extract_text_from_pdf_bytes(pdf_bytes)
    raw_response = _call_openai_chat(
        prompt,
        cv_content,
        model=model,
        temperature=temperature,
    )
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ResumeProcessingError("OpenAI did not return valid JSON") from exc


def process_resume_file(
    pdf_path: str,
    desired_positions: Iterable[str],
    *,
    openai_api_key: str,
    prompt_text: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.0,
) -> dict:
    """Process a resume PDF from a filesystem path."""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return process_resume(
        pdf_bytes,
        desired_positions,
        openai_api_key=openai_api_key,
        prompt_text=prompt_text,
        model=model,
        temperature=temperature,
    )


def load_default_prompt() -> str:
    """Public helper to access the bundled prompt text."""
    return load_prompt_text()
