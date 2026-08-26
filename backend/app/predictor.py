from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from .exam_data import STAGES, get_pattern
from .models import TimelineItem, TrackResponse


BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=BACKEND_ENV, override=False)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
PATTERN_NOTE = "Based on NTA patterns from 2019–2024"
DISCLAIMER = "Dates are estimates, not official NTA notices."


def build_fallback_response(exam: str, current_stage: str, today: date | None = None) -> TrackResponse:
    today = today or date.today()
    pattern = get_pattern(exam)
    current_index = STAGES.index(current_stage)
    running_date = today
    timeline: list[TimelineItem] = []

    for index, stage in enumerate(STAGES):
        if index < current_index:
            days_before_current = sum(
                pattern.gap_days[STAGES[step]]
                for step in range(index + 1, current_index + 1)
            )
            display_date = today - timedelta(days=days_before_current)
            timeline.append(
                TimelineItem(
                    stage=stage,
                    status="completed",
                    display_date=display_date.isoformat(),
                    note=PATTERN_NOTE,
                )
            )
            continue

        if index == current_index:
            timeline.append(
                TimelineItem(
                    stage=stage,
                    status="current",
                    display_date=today.isoformat(),
                    note="You are here",
                )
            )
            continue

        running_date = running_date + timedelta(days=pattern.gap_days[stage])
        timeline.append(
            TimelineItem(
                stage=stage,
                status="upcoming",
                predicted_date=running_date.isoformat(),
                confidence=max(40, pattern.confidence[stage] - ((index - current_index - 1) * 4)),
                note=PATTERN_NOTE,
            )
        )

    return TrackResponse(
        exam=exam,
        current_stage=current_stage,
        generated_at=today.isoformat(),
        source="fallback",
        timeline=timeline,
        readiness_items=_fallback_readiness(exam, current_stage),
        summary=f"{exam} is currently tracked at {current_stage}. {DISCLAIMER}",
    )


async def build_ai_response(exam: str, current_stage: str, today: date | None = None) -> TrackResponse:
    today = today or date.today()
    api_key = os.getenv("GROQ_API_KEY")

    fallback = build_fallback_response(exam, current_stage, today)
    if not api_key:
        return fallback

    payload = _groq_payload(exam, current_stage, today, fallback)

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPError:
        return fallback

    parsed = _extract_groq_json(response.json())
    if not parsed:
        return fallback

    return _merge_ai_prediction(exam, current_stage, today, fallback, parsed)

def _fallback_readiness(exam: str, current_stage: str) -> list[str]:
    items_by_stage = {
        "Applied": [
            "Save your application number, password, fee receipt, and uploaded photo in one folder.",
            "Check the official portal once daily for correction-window or city-slip updates.",
            "Make a two-week revision grid for weak chapters and previous-year questions.",
            "Confirm your ID proof, category certificate, and PwD documents if applicable.",
        ],
        "Admit Card Released": [
            "Download the admit card and verify your name, photo, exam date, shift, and center.",
            "Plan travel to the center with a buffer for security checks and traffic.",
            "Pack ID proof, admit card printouts, transparent stationery, and allowed documents.",
            "Switch to timed mocks and light revision instead of starting new topics.",
        ],
        "Exam Done": [
            "Write down questions or topics you remember while they are fresh.",
            "Keep your admit card and response-sheet credentials ready for the answer key.",
            "Avoid score speculation; use the next two days for rest and backup exam planning.",
            "Track objection fees and evidence format before the answer-key window opens.",
        ],
        "Answer Key Out": [
            "Download the answer key, response sheet, and question paper immediately.",
            "Calculate a careful tentative score and mark disputed questions separately.",
            "Submit objections only with clear source proof before the deadline.",
            "Prepare result-day documents and shortlist next-step options based on likely score bands.",
        ],
    }
    items = items_by_stage[current_stage]
    if exam == "CUET":
        return [items[0], "Keep subject-wise shift details handy because CUET updates can vary by paper.", *items[1:3]]
    if exam == "NEET":
        return [items[0], "Keep counseling category and domicile documents ready early.", *items[1:3]]
    return items


def _groq_payload(exam: str, current_stage: str, today: date, fallback: TrackResponse) -> dict[str, Any]:
    pattern = get_pattern(exam)
    context = {
        "exam": exam,
        "current_stage": current_stage,
        "today": today.isoformat(),
        "stage_order": STAGES,
        "historical_cycles": pattern.historical_cycles,
        "average_gap_days_after_current_stage": pattern.gap_days,
        "baseline_timeline": [item.model_dump() for item in fallback.timeline],
    }

    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "predictions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "stage": {"type": "string", "enum": list(STAGES)},
                        "predicted_date": {
                            "type": "string",
                            "description": "ISO date in YYYY-MM-DD format.",
                        },
                        "confidence": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "note": {"type": "string"},
                    },
                    "required": ["stage", "predicted_date", "confidence", "note"],
                    "additionalProperties": False,
                },
            },
            "readiness_items": {
                "type": "array",
                "minItems": 3,
                "maxItems": 5,
                "items": {"type": "string"},
            },
        },
        "required": ["summary", "predictions", "readiness_items"],
        "additionalProperties": False,
    }

    return {
        "model": os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an exam operations assistant for Indian NTA entrance exams. "
                    "Use only the supplied NTA pattern data and baseline calculations. "
                    "Return cautious predictions, never official claims. Keep action items plain-English and specific."
                ),
            },
            {"role": "user", "content": json.dumps(context)},
        ],
        "temperature": 0.2,
        "max_completion_tokens": 900,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "nta_exam_tracker_prediction",
                "strict": True,
                "schema": schema,
            },
        },
    }


def _extract_groq_json(groq_response: dict[str, Any]) -> dict[str, Any] | None:
    choices = groq_response.get("choices", [])
    if not choices:
        return None

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None

    message = first_choice.get("message", {})
    if not isinstance(message, dict):
        return None

    content = message.get("content")
    if isinstance(content, str):
        return _loads_json(content)

    return None


def _loads_json(value: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _merge_ai_prediction(
    exam: str,
    current_stage: str,
    today: date,
    fallback: TrackResponse,
    parsed: dict[str, Any],
) -> TrackResponse:
    prediction_by_stage = {
        item["stage"]: item
        for item in parsed.get("predictions", [])
        if isinstance(item, dict) and item.get("stage") in STAGES
    }

    timeline: list[TimelineItem] = []
    for item in fallback.timeline:
        if item.status != "upcoming":
            timeline.append(item)
            continue

        ai_item = prediction_by_stage.get(item.stage)
        timeline.append(
            TimelineItem(
                stage=item.stage,
                status=item.status,
                predicted_date=_safe_date(ai_item.get("predicted_date") if ai_item else None, item.predicted_date),
                confidence=_safe_confidence(ai_item.get("confidence") if ai_item else None, item.confidence),
                note=PATTERN_NOTE,
            )
        )

    readiness_items = [
        text.strip()
        for text in parsed.get("readiness_items", [])
        if isinstance(text, str) and text.strip()
    ][:5]

    if len(readiness_items) < 3:
        readiness_items = fallback.readiness_items

    return TrackResponse(
        exam=exam,
        current_stage=current_stage,
        generated_at=today.isoformat(),
        source="groq",
        timeline=timeline,
        readiness_items=readiness_items,
        summary=_with_disclaimer(_safe_text(parsed.get("summary"), fallback.summary)),
    )


def _safe_date(value: Any, fallback: str | None) -> str | None:
    if not isinstance(value, str):
        return fallback
    try:
        date.fromisoformat(value)
    except ValueError:
        return fallback
    return value


def _safe_confidence(value: Any, fallback: int | None) -> int | None:
    if not isinstance(value, int):
        return fallback
    return min(100, max(0, value))


def _safe_text(value: Any, fallback: str) -> str:
    if not isinstance(value, str) or not value.strip():
        return fallback
    return value.strip()


def _with_disclaimer(summary: str) -> str:
    if "not official nta notices" in summary.lower():
        return summary
    return f"{summary} {DISCLAIMER}"
