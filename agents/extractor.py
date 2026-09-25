import json
import requests

from models.schemas import (
    CalendarParameters,
    ReminderParameters,
    EmailParameters
)


OLLAMA_URL = "http://localhost:11434/api/generate"

EXTRACTION_MODEL = "qwen2.5:1.5b"


# ============================================================
# Generic Ollama Request
# ============================================================

def _call_ollama(prompt: str) -> dict:

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EXTRACTION_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data


# ============================================================
# Clean JSON Response
# ============================================================

def _parse_json(response_text: str) -> dict:

    text = response_text.strip()

    # Remove markdown code fences if the model produces them.
    if text.startswith("```"):

        lines = text.splitlines()

        lines = [
            line
            for line in lines
            if not line.strip().startswith("```")
        ]

        text = "\n".join(lines).strip()

    return json.loads(text)


# ============================================================
# Calendar Parameter Extraction
# ============================================================

import re


def extract_calendar_parameters(
    action: str
) -> CalendarParameters:

    # ========================================================
    # Step 1 — Deterministic extraction
    # ========================================================

    person = None
    date_reference = None
    time = None
    title = None

    action_lower = action.lower()

    # --------------------------------------------------------
    # Extract relative date
    # --------------------------------------------------------

    date_patterns = [
        r"\btoday\b",
        r"\btomorrow\b",
        r"\byesterday\b",
        r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\bthis\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    ]

    for pattern in date_patterns:

        match = re.search(
            pattern,
            action_lower
        )

        if match:

            date_reference = match.group(0)

            break

    # --------------------------------------------------------
    # Extract time
    # --------------------------------------------------------

    time_pattern = (
        r"\b"
        r"([0-9]{1,2}"
        r"(?:[:.][0-9]{2})?"
        r"\s*(?:AM|PM|am|pm))"
        r"\b"
    )

    time_match = re.search(
        time_pattern,
        action
    )

    if time_match:

        time = time_match.group(1)

    # --------------------------------------------------------
    # Extract person
    #
    # Handles:
    # "Find Rahul's meeting"
    # "meeting with Rahul"
    # "Rahul's meeting"
    # --------------------------------------------------------

    person_patterns = [
        r"meeting\s+with\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+)'s\s+meeting",
        r"meeting\s+with\s+([A-Z][a-z]+\s+[A-Z][a-z]+)"
    ]

    for pattern in person_patterns:

        match = re.search(
            pattern,
            action
        )

        if match:

            person = match.group(1)

            break

    # ========================================================
    # Step 2 — If deterministic extraction succeeded,
    #          return the result.
    # ========================================================

    if (
        person is not None
        or date_reference is not None
        or time is not None
    ):

        return CalendarParameters(
            person=person,
            date_reference=date_reference,
            time=time,
            title=title
        )

    # ========================================================
    # Step 3 — Qwen fallback
    # ========================================================

    prompt = f"""
Extract calendar information from this action:

{action}

Return ONLY JSON:

{{
    "person": null,
    "date_reference": null,
    "time": null,
    "title": null
}}

Rules:

- Extract a person's name if explicitly mentioned.
- Preserve relative dates exactly.
- Extract the explicitly mentioned time.
- Do not calculate dates.
- Do not invent information.
- Return null when information is absent.
"""

    data = _call_ollama(prompt)

    parsed = _parse_json(
        data["response"]
    )

    return CalendarParameters(**parsed)


# ============================================================
# Reminder Parameter Extraction
# ============================================================

def extract_reminder_parameters(
    action: str
) -> ReminderParameters:

    prompt = f"""
Extract the reminder offset from this action.

ACTION:
{action}

Return ONLY valid JSON in this format:

{{
    "minutes_before": 0
}}

Rules:

1. Extract the number of minutes before the event.
2. Example:
   "remind me 30 minutes before the meeting"
   -> 30
3. Do not invent a value.
4. If no number is provided, return 0.

Return JSON only.
"""

    data = _call_ollama(prompt)

    parsed = _parse_json(
        data["response"]
    )

    return ReminderParameters(**parsed)


# ============================================================
# Email Parameter Extraction
# ============================================================

def extract_email_parameters(
    action: str
) -> EmailParameters:

    import re

    # ========================================================
    # Deterministic extraction
    # ========================================================

    # Example:
    # "Find emails related to Rahul's meeting"
    #                     ↓
    #                   Rahul

    person_patterns = [
        r"emails?\s+(?:related\s+to|from|about)\s+([A-Z][a-z]+)",
        r"mail\s+(?:related\s+to|from|about)\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+)'s\s+(?:emails?|mail)"
    ]

    for pattern in person_patterns:

        match = re.search(
            pattern,
            action
        )

        if match:

            return EmailParameters(
                keyword=match.group(1)
            )

    # ========================================================
    # Qwen fallback
    # ========================================================

    prompt = f"""
Extract the most useful search keyword from this email action:

{action}

Return ONLY JSON:

{{
    "keyword": null
}}

Rules:

1. If a person's name is mentioned, use ONLY the person's name.
2. Do not include words such as:
   - email
   - emails
   - mail
   - meeting
   - related
   - find
   - search
3. Do not invent information.
4. Return null if there is no clear keyword.

Example:

Action:
Find emails related to Rahul's meeting

Output:
{{
    "keyword": "Rahul"
}}

Return JSON only.
"""

    data = _call_ollama(prompt)

    parsed = _parse_json(
        data["response"]
    )

    return EmailParameters(**parsed)