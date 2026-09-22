import requests

from models.schemas import (
    CalendarParameters,
    ReminderParameters,
    EmailParameters
)


# ============================================================
# Ollama Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"


# ============================================================
# Calendar Parameter Extraction
# ============================================================

def extract_calendar_parameters(
    user_request: str
) -> CalendarParameters:

    prompt = f"""
You are a parameter extraction agent.

Extract calendar-related information from the user's request.

Extract:

- person
- date_reference
- time
- title

Rules:

1. Do not invent information.
2. If a value is not present, return null.
3. Keep relative dates such as "tomorrow",
   "next Monday", or "next week" exactly as written.
4. Return the time in HH:MM format when possible.
5. Return ONLY valid JSON.

Example:

User:
"Find Rahul's meeting tomorrow at 10 AM"

Return:

{{
    "person": "Rahul",
    "date_reference": "tomorrow",
    "time": "10:00",
    "title": null
}}

User request:

{user_request}

Return ONLY JSON.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    raw_output = data["response"]

    return CalendarParameters.model_validate_json(
        raw_output
    )


# ============================================================
# Reminder Parameter Extraction
# ============================================================

def extract_reminder_parameters(
    user_request: str
) -> ReminderParameters:

    prompt = f"""
Extract the reminder offset from the user's request.

Return:

{{
    "minutes_before": number
}}

Examples:

"Remind me 30 minutes before the meeting"

Return:

{{
    "minutes_before": 30
}}

"Remind me 1 hour before the meeting"

Return:

{{
    "minutes_before": 60
}}

Do not invent information.

Return ONLY valid JSON.

User request:

{user_request}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    raw_output = data["response"]

    return ReminderParameters.model_validate_json(
        raw_output
    )


# ============================================================
# Email Parameter Extraction
# ============================================================

def extract_email_parameters(
    user_request: str
) -> EmailParameters:

    prompt = f"""
Extract the main person, topic, or keyword that should be
used when searching emails.

Return:

{{
    "keyword": "..."
}}

Examples:

"Find emails from Rahul"

Return:

{{
    "keyword": "Rahul"
}}

"Find emails about the project architecture"

Return:

{{
    "keyword": "project architecture"
}}

Do not invent information.

Return ONLY valid JSON.

User request:

{user_request}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        stream=False,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    raw_output = data["response"]

    return EmailParameters.model_validate_json(
        raw_output
    )


# ============================================================
# Testing
# ============================================================

if __name__ == "__main__":

    request = input(
        "Enter a calendar request: "
    ).strip()

    try:

        calendar = extract_calendar_parameters(
            request
        )

        print("\nCalendar Parameters:")
        print(
            calendar.model_dump_json(
                indent=2
            )
        )

    except Exception as e:

        print("\nExtraction failed:")
        print(e)