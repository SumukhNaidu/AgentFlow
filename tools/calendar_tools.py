from datetime import datetime, timedelta


# ============================================================
# DEMO CALENDAR DATA
# ============================================================

TOMORROW = (
    datetime.now().date() + timedelta(days=1)
).isoformat()


CALENDAR_EVENTS = [
    {
        "title": "Project Meeting with Rahul",
        "date": TOMORROW,
        "time": "10:00",
        "participants": ["Rahul", "Esha"],
        "description": (
            "Discuss project progress and next steps."
        )
    },
    {
        "title": "Team Standup",
        "date": TOMORROW,
        "time": "09:00",
        "participants": ["Esha", "Team"],
        "description": (
            "Daily project standup."
        )
    }
]


# ============================================================
# SEARCH CALENDAR
# ============================================================

def search_calendar(person=None, date=None):

    results = []

    for event in CALENDAR_EVENTS:

        person_match = True
        date_match = True

        if person:
            person_match = any(
                person.lower() in participant.lower()
                for participant in event["participants"]
            )

        if date:
            date_match = event["date"] == date

        if person_match and date_match:
            results.append(event)

    return results


# ============================================================
# CREATE REMINDER
# ============================================================

def create_reminder(event, minutes_before):

    event_datetime = datetime.strptime(
        f"{event['date']} {event['time']}",
        "%Y-%m-%d %H:%M"
    )

    reminder_time = (
        event_datetime
        - timedelta(minutes=minutes_before)
    )

    return {
        "type": "reminder_created",
        "reminder": {
            "event": event["title"],
            "reminder_time": reminder_time.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "minutes_before": minutes_before
        }
    }