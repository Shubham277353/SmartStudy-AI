"""
data_manager.py
---------------
Handles all local data persistence using a single JSON file.
Provides simple CRUD helpers for subjects, exams, preferences,
timetable, and missed sessions.
"""

import json
import os
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "study_data.json")

_DEFAULT = {
    "subjects": [],
    "exams": [],
    "preferences": {
        "daily_hours": 6,
        "block_size": 1.5,
        "break_minutes": 15,
    },
    "timetable": {},
    "missed_sessions": [],
}


# ── Core I/O ──────────────────────────────────────────────────────────────────

def load() -> dict:
    if not os.path.exists(DATA_FILE):
        save(_DEFAULT.copy())
        return _DEFAULT.copy()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save(data: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Subjects ──────────────────────────────────────────────────────────────────

def get_subjects() -> list:
    return load()["subjects"]


def add_subject(name: str, difficulty: str, priority: int) -> None:
    data = load()
    # Prevent duplicates (case-insensitive)
    if any(s["name"].lower() == name.lower() for s in data["subjects"]):
        raise ValueError(f"Subject '{name}' already exists.")
    data["subjects"].append({"name": name, "difficulty": difficulty, "priority": priority})
    save(data)


def remove_subject(name: str) -> None:
    data = load()
    data["subjects"] = [s for s in data["subjects"] if s["name"] != name]
    data["exams"] = [e for e in data["exams"] if e["subject"] != name]
    save(data)


# ── Exams ─────────────────────────────────────────────────────────────────────

def get_exams() -> list:
    return load()["exams"]


def add_exam(subject: str, exam_date: str) -> None:
    data = load()
    # Overwrite if exam for this subject already exists
    data["exams"] = [e for e in data["exams"] if e["subject"] != subject]
    data["exams"].append({"subject": subject, "date": exam_date})
    save(data)


def remove_exam(subject: str) -> None:
    data = load()
    data["exams"] = [e for e in data["exams"] if e["subject"] != subject]
    save(data)


# ── Preferences ───────────────────────────────────────────────────────────────

def get_preferences() -> dict:
    return load()["preferences"]


def save_preferences(daily_hours: float, block_size: float, break_minutes: int) -> None:
    data = load()
    data["preferences"] = {
        "daily_hours": daily_hours,
        "block_size": block_size,
        "break_minutes": break_minutes,
    }
    save(data)


# ── Timetable ─────────────────────────────────────────────────────────────────

def get_timetable() -> dict:
    return load()["timetable"]


def save_timetable(timetable: dict) -> None:
    data = load()
    data["timetable"] = timetable
    data["missed_sessions"] = []   # reset missed sessions on regeneration
    save(data)


# ── Missed Sessions ───────────────────────────────────────────────────────────

def get_missed_sessions() -> list:
    return load()["missed_sessions"]


def mark_missed(day: str, slot_index: int) -> None:
    data = load()
    entry = {"day": day, "slot_index": slot_index}
    if entry not in data["missed_sessions"]:
        data["missed_sessions"].append(entry)
    save(data)


def unmark_missed(day: str, slot_index: int) -> None:
    data = load()
    data["missed_sessions"] = [
        m for m in data["missed_sessions"]
        if not (m["day"] == day and m["slot_index"] == slot_index)
    ]
    save(data)


def save_rescheduled_timetable(timetable: dict) -> None:
    data = load()
    data["timetable"] = timetable
    save(data)
