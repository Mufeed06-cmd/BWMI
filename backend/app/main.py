from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .exam_data import EXAM_PATTERNS, SELECTABLE_STAGES, STAGES
from .models import ExamOption, ExamsResponse, TrackRequest, TrackResponse
from .predictor import build_ai_response


BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=BACKEND_ENV, override=False)

app = FastAPI(
    title="NTA Exam Tracker API",
    version="1.0.0",
    description="AI-assisted NTA exam timeline and readiness tracker.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/exams", response_model=ExamsResponse)
async def list_exams() -> ExamsResponse:
    return ExamsResponse(
        exams=[
            ExamOption(
                exam=name,
                stages=STAGES,
                selectable_stages=SELECTABLE_STAGES,
                description=pattern.description,
                historical_cycles=pattern.historical_cycles,
            )
            for name, pattern in EXAM_PATTERNS.items()
        ]
    )


@app.post("/api/track", response_model=TrackResponse)
async def track_exam(request: TrackRequest) -> TrackResponse:
    if request.exam not in EXAM_PATTERNS:
        raise HTTPException(status_code=422, detail="Unsupported exam.")

    if request.current_stage not in SELECTABLE_STAGES:
        raise HTTPException(status_code=422, detail="Unsupported stage.")

    return await build_ai_response(request.exam, request.current_stage)


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str) -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    requested_file = FRONTEND_DIST / full_path
    if requested_file.is_file():
        return FileResponse(requested_file)

    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend build not found. Run npm run build in frontend.")
