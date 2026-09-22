from datetime import datetime, timedelta


# ============================================================
# Demo Calendar Data
# ============================================================

CALENDAR_EVENTS = [
    {
        "title": "Project Meeting with Rahul",
        "date": "2026-09-18",
        "time": "10:00",
        "participants": ["Rahul", "Esha"],
        "description": "Discuss project progress and next steps."
    },
    {
        "title": "Team Standup",
        "date": "2026-09-18",
        "time": "09:00",
        "participants": ["Esha", "Team"],
        "description": "Daily project standup."
    }
]


# ============================================================
# Search Calendar
# ============================================================

def search_calendar(
    person: str,
    date: str
):

    results = []

    for event in CALENDAR_EVENTS:

        if (
            person.lower() in event["title"].lower()
            and event["date"] == date
        ):
            results.append(event)

    return results


# ============================================================
# Create Reminder
# ============================================================

def create_reminder(
    event: dict,
    minutes_before: int
):

    event_time = datetime.strptime(
        f'{event["date"]} {event["time"]}',
        "%Y-%m-%d %H:%M"
    )

    reminder_time = (
        event_time -
        timedelta(minutes=minutes_before)
    )

    reminder = {
        "event": event["title"],
        "reminder_time": reminder_time.strftime(
            "%Y-%m-%d %H:%M"
        ),
        "minutes_before": minutes_before
    }

    return reminder