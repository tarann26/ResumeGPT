"""FastAPI application exposing resume parsing as an HTTP API."""

from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .process import ResumeProcessingError, process_resume

app = FastAPI(title="ResumeGPT", version="0.1.0")


@app.post("/parse")
async def parse_resume(
    file: UploadFile = File(..., description="PDF file"),
    desired_positions: str | None = Form(
        None, description="Comma-separated desired positions (optional)"
    ),
):
    """Parse a resume PDF and return extracted fields."""
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    positions: List[str] = []
    if desired_positions:
        positions = [p.strip() for p in desired_positions.split(",") if p.strip()]

    try:
        api_key = os.environ["OPENAI_API_KEY"]
    except KeyError as exc:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured") from exc

    try:
        result = process_resume(
            pdf_bytes,
            positions,
            openai_api_key=api_key,
        )
    except ResumeProcessingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Unexpected error") from exc

    return JSONResponse(result)
