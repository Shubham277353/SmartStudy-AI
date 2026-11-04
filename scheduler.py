"""
scheduler.py
------------
Pure scheduling logic — no UI, no file I/O.

Algorithm overview:
  1. Score each subject using urgency (exam proximity), difficulty, and priority.
  2. Divide each day's available hours into fixed-size study blocks.
  3. Assign subjects to blocks greedily in descending score order,
     distributing evenly so no subject monopolises a single day.
  4. Reschedule missed sessions by redistributing their hours into
     remaining (future) days of the current week.
"""

from datetime import date, datetime, timedelta

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIFFICULTY_WEIGHT = {"Easy": 1, "Medium": 2, "Hard": 3}


# ── Scoring ───────────────────────────────────────────────────────────────────

def _days_until_exam(exam_date_str: str) -> int:
    """Return days between today and the exam date (minimum 1 to avoid division by zero)."""
    try:
        exam_dt = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        delta = (exam_dt - date.today()).days
        return max(delta, 1)
    except (ValueError, TypeError):
        return 30  # default if no exam date


def score_subject(subject: dict, exams: list) -> float:
    """
    Composite score = urgency(0.5) + difficulty(0.3) + priority(0.2)
    All components are normalised to a 0-1 range before weighting.
    """
    # Urgency: closer exam → higher score (capped at 30 days window)
    exam_entry = next((e for e in exams if e["subject"] == subject["name"]), None)
    days_left = _days_until_exam(exam_entry["date"]) if exam_entry else 30
    urgency = 1 - min(days_left, 30) / 30          # 0 (far) → 1 (today)

    difficulty = (DIFFICULTY_WEIGHT[subject["difficulty"]] - 1) / 2  # 0, 0.5, 1
    priority = (subject["priority"] - 1) / 4                         # 0 → 1

    return round(urgency * 0.5 + difficulty * 0.3 + priority * 0.2, 4)


# ── Slot generation ───────────────────────────────────────────────────────────

def _build_slots(daily_hours: float, block_size: float, break_minutes: int) -> list[dict]:
    """
    Return a list of slot dicts for one day.
    Each slot has a start_time string and duration (hours).
    Slots start at 08:00 with configurable break_minutes between them.
    """
    slots = []
    current_minutes = 8 * 60  # 08:00
    remaining = daily_hours

    while remaining >= block_size:
        h, m = divmod(int(current_minutes), 60)
        slots.append({
            "start": f"{h:02d}:{m:02d}",
            "duration_hrs": block_size,
            "subject": None,
            "missed": False,
        })
        current_minutes += block_size * 60 + break_minutes  # block + configured break
        remaining -= block_size

    return slots


# ── Timetable generation ──────────────────────────────────────────────────────

def generate_timetable(subjects: list, exams: list, preferences: dict) -> dict:
    """
    Build a weekly timetable dict keyed by day name.
    Each value is a list of slot dicts.
    """
    if not subjects:
        return {}

    daily_hours = preferences["daily_hours"]
    block_size = preferences["block_size"]
    break_minutes = int(preferences.get("break_minutes", 15))

    # Score and sort subjects (highest first)
    scored = sorted(
        subjects,
        key=lambda s: score_subject(s, exams),
        reverse=True,
    )

    timetable = {day: _build_slots(daily_hours, block_size, break_minutes) for day in DAYS}

    # Total slots available across the week
    slots_per_day = len(timetable[DAYS[0]])
    total_slots = slots_per_day * len(DAYS)
    if total_slots == 0:
        return timetable

    # ── Proportional weekly allocation ───────────────────────────────────────
    scores = [score_subject(s, exams) for s in scored]
    total_score = sum(scores) or 1

    allocation = {}          # subject name → total weekly slots
    remaining_slots = total_slots
    for i, subj in enumerate(scored[:-1]):
        count = max(1, round(scores[i] / total_score * total_slots))
        count = min(count, remaining_slots - (len(scored) - i - 1))
        allocation[subj["name"]] = count
        remaining_slots -= count
    allocation[scored[-1]["name"]] = remaining_slots

    # ── Per-day cap: spread each subject's slots across all 7 days ───────────
    # cap = ceil(weekly_allocation / 7), minimum 1
    import math
    daily_cap = {
        name: max(1, math.ceil(count / len(DAYS)))
        for name, count in allocation.items()
    }

    # Remaining budget each subject can still place (decremented as we fill)
    budget = dict(allocation)

    # ── Round-robin fill: iterate slots positions across all days ─────────────
    # For each slot position i (block 1, block 2 …) go through every day,
    # then move to the next position. This interleaves subjects naturally.
    day_used = {day: {} for day in DAYS}   # day → {subject: count placed today}

    for slot_pos in range(slots_per_day):
        for day in DAYS:
            slot = timetable[day][slot_pos]
            # Pick the highest-priority subject that still has budget
            # and hasn't hit its daily cap for this day
            for subj in scored:
                name = subj["name"]
                used_today = day_used[day].get(name, 0)
                if budget.get(name, 0) > 0 and used_today < daily_cap[name]:
                    slot["subject"] = name
                    budget[name] -= 1
                    day_used[day][name] = used_today + 1
                    break

    return timetable


# ── Reschedule missed sessions ────────────────────────────────────────────────

def reschedule_missed(timetable: dict, missed_sessions: list) -> dict:
    """
    Mark missed slots and redistribute their subjects into free slots
    on future days (days after today in the week).
    """
    import copy
    tt = copy.deepcopy(timetable)

    today_name = date.today().strftime("%A")
    today_idx = DAYS.index(today_name) if today_name in DAYS else 0
    future_days = DAYS[today_idx + 1:]

    # Collect subjects from missed slots
    missed_subjects = []
    for m in missed_sessions:
        day, idx = m["day"], m["slot_index"]
        if day in tt and idx < len(tt[day]):
            tt[day][idx]["missed"] = True
            if tt[day][idx]["subject"]:
                missed_subjects.append(tt[day][idx]["subject"])

    # Find free slots in future days (slots with no subject assigned)
    free_slots = [
        (day, i)
        for day in future_days
        for i, slot in enumerate(tt.get(day, []))
        if not slot["subject"] and not slot["missed"]
    ]

    # Fill free slots with missed subjects
    for subject, (day, i) in zip(missed_subjects, free_slots):
        tt[day][i]["subject"] = subject
        tt[day][i]["rescheduled"] = True

    return tt
