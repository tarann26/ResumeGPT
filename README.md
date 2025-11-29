# ResumeGPT

ResumeGPT extracts structured information from resume PDFs using OpenAI chat models. It ships as an importable Python package, a lightweight CLI, and a FastAPI HTTP service for hosting.

## Install

```bash
pip install .
```
(After publishing: `pip install resumegpt`.)

## HTTP API

- Endpoint: `POST /parse`
- Request: `multipart/form-data` with fields:
  - `file`: PDF file upload
  - `desired_positions`: comma-separated list (e.g., `Data Scientist,Data Engineer`)
- Response: JSON object containing the parsed fields (see “What it extracts”).

Run locally:

```bash
OPENAI_API_KEY=sk-... uvicorn resumegpt.api:app --host 0.0.0.0 --port 8000
# then call http://localhost:8000/parse
```

Examples:

```bash
curl -X POST http://localhost:8000/parse \
  -F "desired_positions=Data Scientist,Data Engineer" \
  -F "file=@/path/to/resume.pdf;type=application/pdf"
```

```js
// browser/Node fetch
const form = new FormData();
form.append("desired_positions", "Data Scientist,Data Engineer");
form.append("file", pdfFile); // File or Blob
const res = await fetch("http://localhost:8000/parse", { method: "POST", body: form });
const data = await res.json();
```

```python
import requests

files = {"file": ("resume.pdf", open("resume.pdf", "rb"), "application/pdf")}
data = {"desired_positions": "Data Scientist,Data Engineer"}
resp = requests.post("http://localhost:8000/parse", data=data, files=files)
print(resp.json())
```

## Deploy on Render

A `render.yaml` is included. Steps:
1. Push this repo to your Git provider.
2. In Render, create a Web Service from the repo. Render will read `render.yaml` to build and start:
   - Build: `pip install -e .[dev]`
   - Start: `uvicorn resumegpt.api:app --host 0.0.0.0 --port $PORT`
3. Add environment variable `OPENAI_API_KEY` in the service settings.
4. After deploy, call `https://<your-service>.onrender.com/parse` with the same multipart request shown above.

## Usage (Python)

```python
from resumegpt import process_resume

with open("resume.pdf", "rb") as f:
    pdf_bytes = f.read()

result = process_resume(
    pdf_bytes,
    desired_positions=["Data Scientist", "Data Engineer"],
    openai_api_key="sk-...",
)
print(result)
```

## Usage (CLI)

```bash
OPENAI_API_KEY=sk-... resumegpt path/to/resume.pdf "Data Scientist,Data Engineer" --pretty
```

## What it extracts

The model is prompted to return 23 fields:

1. Education Bachelor University
2. Education Bachelor GPA
3. Education Bachelor Major
4. Education Bachelor Graduation Date
5. Education Masters University
6. Education Masters GPA
7. Education Masters Major
8. Education Masters Graduation Date
9. Education PhD University
10. Education PhD GPA
11. Education PhD Major
12. Education PhD Graduation Date
13. Years of Experience
14. Experience Companies
15. Top 5 Responsibilities/Projects Titles
16. Top 5 Courses/Certifications Titles
17. Top 3 Technical Skills
18. Top 3 Soft Skills
19. Current Employment Status
20. Nationality
21. Current Residence
22. Suitable Position (filled dynamically from your desired positions)
23. Candidate Rating (Out of 10)

If information is missing in the resume, fields should be empty strings.

## Configuration

- Provide your OpenAI API key via `openai_api_key` (Python) or `OPENAI_API_KEY`/`--openai-api-key` (CLI).
- `model` defaults to `gpt-3.5-turbo`; override to `gpt-4` if you have access.
- `desired_positions` is a list (or comma-separated string in the CLI) used to tailor the prompt.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Build and upload (from a clean tree):

```bash
python -m build
twine upload dist/*
```

## License

MIT
