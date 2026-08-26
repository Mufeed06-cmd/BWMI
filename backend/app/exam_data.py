from __future__ import annotations

from dataclasses import dataclass


EXAMS = ("JEE Main", "NEET", "CUET")

STAGES = (
    "Applied",
    "Admit Card Released",
    "Exam Done",
    "Answer Key Out",
    "Result Declared",
)

SELECTABLE_STAGES = STAGES[:4]


@dataclass(frozen=True)
class ExamPattern:
    label: str
    description: str
    gap_days: dict[str, int]
    confidence: dict[str, int]
    historical_cycles: list[dict[str, str]]


EXAM_PATTERNS: dict[str, ExamPattern] = {
    "JEE Main": ExamPattern(
        label="JEE Main",
        description="Engineering entrance cycle with a short admit-card to exam gap and quick answer-key window.",
        gap_days={
            "Admit Card Released": 22,
            "Exam Done": 6,
            "Answer Key Out": 8,
            "Result Declared": 10,
        },
        confidence={
            "Admit Card Released": 78,
            "Exam Done": 74,
            "Answer Key Out": 70,
            "Result Declared": 66,
        },
        historical_cycles=[
            {
                "cycle": "2023 Session 2",
                "Applied": "2023-03-12",
                "Admit Card Released": "2023-04-03",
                "Exam Done": "2023-04-15",
                "Answer Key Out": "2023-04-19",
                "Result Declared": "2023-04-29",
            },
            {
                "cycle": "2024 Session 2",
                "Applied": "2024-03-04",
                "Admit Card Released": "2024-03-31",
                "Exam Done": "2024-04-12",
                "Answer Key Out": "2024-04-12",
                "Result Declared": "2024-04-24",
            },
            {
                "cycle": "2025 Session 2",
                "Applied": "2025-02-25",
                "Admit Card Released": "2025-03-29",
                "Exam Done": "2025-04-09",
                "Answer Key Out": "2025-04-11",
                "Result Declared": "2025-04-18",
            },
        ],
    ),
    "NEET": ExamPattern(
        label="NEET",
        description="Medical entrance cycle with one main paper and a longer answer-key review window.",
        gap_days={
            "Admit Card Released": 32,
            "Exam Done": 5,
            "Answer Key Out": 24,
            "Result Declared": 14,
        },
        confidence={
            "Admit Card Released": 76,
            "Exam Done": 72,
            "Answer Key Out": 64,
            "Result Declared": 61,
        },
        historical_cycles=[
            {
                "cycle": "2023",
                "Applied": "2023-04-15",
                "Admit Card Released": "2023-05-03",
                "Exam Done": "2023-05-07",
                "Answer Key Out": "2023-06-04",
                "Result Declared": "2023-06-13",
            },
            {
                "cycle": "2024",
                "Applied": "2024-04-10",
                "Admit Card Released": "2024-05-02",
                "Exam Done": "2024-05-05",
                "Answer Key Out": "2024-05-29",
                "Result Declared": "2024-06-04",
            },
            {
                "cycle": "2025",
                "Applied": "2025-03-07",
                "Admit Card Released": "2025-04-30",
                "Exam Done": "2025-05-04",
                "Answer Key Out": "2025-06-03",
                "Result Declared": "2025-06-14",
            },
        ],
    ),
    "CUET": ExamPattern(
        label="CUET",
        description="Multi-shift entrance cycle where city slips and admit cards tend to move close to exam windows.",
        gap_days={
            "Admit Card Released": 25,
            "Exam Done": 12,
            "Answer Key Out": 18,
            "Result Declared": 21,
        },
        confidence={
            "Admit Card Released": 72,
            "Exam Done": 68,
            "Answer Key Out": 63,
            "Result Declared": 59,
        },
        historical_cycles=[
            {
                "cycle": "2023",
                "Applied": "2023-03-30",
                "Admit Card Released": "2023-05-19",
                "Exam Done": "2023-06-23",
                "Answer Key Out": "2023-06-29",
                "Result Declared": "2023-07-15",
            },
            {
                "cycle": "2024",
                "Applied": "2024-04-05",
                "Admit Card Released": "2024-05-13",
                "Exam Done": "2024-05-29",
                "Answer Key Out": "2024-07-07",
                "Result Declared": "2024-07-28",
            },
            {
                "cycle": "2025",
                "Applied": "2025-03-24",
                "Admit Card Released": "2025-05-10",
                "Exam Done": "2025-06-03",
                "Answer Key Out": "2025-06-17",
                "Result Declared": "2025-07-04",
            },
        ],
    ),
}


def get_pattern(exam: str) -> ExamPattern:
    return EXAM_PATTERNS[exam]
