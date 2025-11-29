# ResumeGPT

ResumeGPT extracts structured information from resume PDFs using OpenAI chat models. This repo now provides only a FastAPI HTTP service for hosting.

## Quick start (local)

```bash
pip install -r requirements.txt
OPENAI_API_KEY=sk-... uvicorn resumegpt.api:app --host 0.0.0.0 --port 8000
```

Then call:

```bash
curl -X POST http://localhost:8000/parse \
  -F "desired_positions=Data Scientist,Data Engineer" \
  -F "file=@/path/to/resume.pdf;type=application/pdf"
```

## HTTP API

- Endpoint: `POST /parse`
- Request: `multipart/form-data` with fields:
  - `file`: PDF file upload
  - `desired_positions`: comma-separated list (e.g., `Data Scientist,Data Engineer`)
- Response: JSON object containing the parsed fields (see “What it extracts”).

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

## Deploy on Railway

1. Push this repo to your Git provider.
2. Create a Railway service from the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn resumegpt.api:app --host 0.0.0.0 --port $PORT` (also in `Procfile`).
5. Add environment variable `OPENAI_API_KEY` in the Railway dashboard.
6. After deploy, call `https://<your-service>.up.railway.app/parse` with the multipart request shown above.

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

- Provide your OpenAI API key via `OPENAI_API_KEY`.
- `model` defaults to `gpt-3.5-turbo`; override inside `resumegpt/process.py` if you need `gpt-4`.
- `desired_positions` is the comma-separated string you pass in the request.

## License

MIT
