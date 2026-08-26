from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .exam_data import EXAMS, SELECTABLE_STAGES, STAGES


ExamName = Literal["JEE Main", "NEET", "CUET"]
SelectableStage = Literal["Applied", "Admit Card Released", "Exam Done", "Answer Key Out"]
StageName = Literal[
    "Applied",
    "Admit Card Released",
    "Exam Done",
    "Answer Key Out",
    "Result Declared",
]
StageStatus = Literal["completed", "current", "upcoming"]


class TrackRequest(BaseModel):
    exam: ExamName
    current_stage: SelectableStage


class TimelineItem(BaseModel):
    stage: StageName
    status: StageStatus
    display_date: str | None = None
    predicted_date: str | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    note: str


class TrackResponse(BaseModel):
    exam: ExamName
    current_stage: SelectableStage
    generated_at: str
    source: Literal["groq", "fallback"]
    timeline: list[TimelineItem]
    readiness_items: list[str] = Field(min_length=3, max_length=5)
    summary: str


class ExamOption(BaseModel):
    exam: str
    stages: tuple[str, ...]
    selectable_stages: tuple[str, ...]
    description: str
    historical_cycles: list[dict[str, str]]


class ExamsResponse(BaseModel):
    exams: list[ExamOption]


def valid_exams() -> tuple[str, ...]:
    return EXAMS


def valid_stages() -> tuple[str, ...]:
    return STAGES


def valid_selectable_stages() -> tuple[str, ...]:
    return SELECTABLE_STAGES
