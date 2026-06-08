# Render Backend Runtime Requirements

Render deploys the hosted FastAPI backend. It should install `requirements-render.txt`, not the full local/research `requirements.txt`.

## Why this exists

The full local requirements file includes research, evaluation, and NLP dependencies that are useful locally but unnecessary for the hosted API runtime.

Heavy compiled packages such as spaCy / thinc / blis can fail or slow hosted builds. The hosted backend only needs the lightweight dependencies required to serve the API.

## Render build command

Use:

```bash
pip install -r requirements-render.txt
```

## Render start command

Use:

```bash
PYTHONPATH=src uvicorn backend.app:app --host 0.0.0.0 --port $PORT --no-access-log
```

## Required Render environment variables

```text
PYTHON_VERSION=3.11.11
VIBE_BACKEND_ENV=production
VIBE_BACKEND_ALLOWED_ORIGINS=https://www.vibe-signal.com,https://vibe-signal.com,https://vibe-signal.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:19006,http://localhost:8081
```

## Safety boundary

This change does not alter backend behavior. It only narrows hosted install dependencies.

No raw/private content, model artifacts, embeddings, vector stores, external datasets, analytics, tracking, auth, or model training are added.
