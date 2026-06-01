from __future__ import annotations

from fastapi import FastAPI

from .routes import analyze, events, feedback, match


app = FastAPI(title="VibeSignal Backend", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "vibe-signal-backend"}


app.include_router(analyze.router)
app.include_router(match.router)
app.include_router(feedback.router)
app.include_router(events.router)
