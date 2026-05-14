"""
Maison BU — Booking & Schedule Tools
Utilities for the Last Minute Booking Agent to query availability.

In production, connect these to your booking system (e.g. Fresha, Planity,
Booksy, or a custom calendar API). The stubs below demonstrate the interface.
"""
from datetime import datetime, timedelta
from typing import Optional


def get_available_slots(
    date: str | None = None,
    service: str | None = None,
    therapist: str | None = None,
    lookahead_days: int = 7,
) -> list[dict]:
    """
    Returns available appointment slots.

    In production: query your booking system API here.
    Returns a list of slot dicts:
      {"date": "Thursday 15 May", "time": "14:00", "duration": "90 min",
       "service": "Colour & Balayage", "therapist": "Marie"}
    """
    # --- STUB: replace with real API call ---
    today = datetime.today()
    mock_slots = []
    for i in range(1, lookahead_days + 1):
        day = today + timedelta(days=i)
        if day.weekday() < 6:  # Mon–Sat
            mock_slots.append({
                "date": day.strftime("%A %d %B"),
                "time": "11:00",
                "duration": "60 min",
                "service": service or "Signature Treatment",
                "therapist": therapist or "The Maison BU Team",
            })
    return mock_slots[:3]  # Return first 3 available


def get_todays_cancellations() -> list[dict]:
    """
    Returns today's cancellations as re-openable slots.

    In production: poll your booking system's webhook or cancellation feed.
    """
    # --- STUB ---
    return [
        {
            "date": "Today",
            "time": "15:30",
            "duration": "75 min",
            "service": "Colour Balayage",
            "therapist": "Sophie",
        }
    ]


def format_slots_for_display(slots: list[dict]) -> str:
    if not slots:
        return "No slots currently available."
    lines = []
    for s in slots:
        line = f"  {s['date']} · {s['time']} · {s.get('service', 'Treatment')} ({s.get('duration', '')})"
        if s.get("therapist"):
            line += f" with {s['therapist']}"
        lines.append(line)
    return "\n".join(lines)


def check_slow_periods(weeks_ahead: int = 4) -> list[dict]:
    """
    Identifies upcoming weeks with low booking rates.

    In production: pull occupancy data from your booking system.
    Returns periods where occupancy < threshold.
    """
    # --- STUB ---
    today = datetime.today()
    slow = []
    for i in range(1, weeks_ahead + 1):
        week_start = today + timedelta(weeks=i)
        slow.append({
            "week_start": week_start.strftime("%d %B"),
            "week_end": (week_start + timedelta(days=5)).strftime("%d %B"),
            "occupancy_percent": 45,
            "available_slots": 12,
        })
    return slow[:2]
