import requests
from typing import Literal
from pydantic import BaseModel


# ============================================================
# Ollama Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"


# ============================================================
# Router Output Schema
# ============================================================

class RouterDecision(BaseModel):

    agent: Literal[
        "email",
        "calendar",
        "task",
        "memory",
        "general"
    ]

    intent: str

    complexity: Literal[
        "simple",
        "complex"
    ]

    requires_planning: bool


# ============================================================
# Complexity Detection
# ============================================================

def detect_complexity(user_request: str) -> bool:

    request = user_request.lower()

    complex_indicators = [
        " and ",
        " then ",
        " after ",
        " before ",
        " also ",
        "summarize",
        "related emails",
        "find the emails",
        "set a reminder",
        "remind me",
    ]

    matches = sum(
        indicator in request
        for indicator in complex_indicators
    )

    return matches >= 2


# ============================================================
# Router Function
# ============================================================

def route_request(user_request: str) -> RouterDecision:

    # --------------------------------------------------------
    # Python determines whether the request needs planning.
    # This is deterministic and more reliable than asking
    # the small model to make this decision.
    # --------------------------------------------------------

    requires_planning = detect_complexity(user_request)


    # --------------------------------------------------------
    # Ask Qwen to determine the primary agent and intent.
    # --------------------------------------------------------

    prompt = f"""
You are the Router Agent for a personal productivity AI system.

Your job is to determine the PRIMARY agent responsible for
the user's request and identify the user's intent.


AVAILABLE AGENTS
----------------

email:
- Search emails
- Read emails
- Summarize emails
- Manage emails

calendar:
- Meetings
- Events
- Scheduling
- Calendar reminders

task:
- Todo items
- Task management

memory:
- Store user preferences
- Retrieve stored user facts
- Store or retrieve personal information

general:
- Anything unrelated to the above


ROUTING RULES
-------------

1. Choose exactly ONE primary agent.

2. Use "email" for email-related requests.

3. Use "calendar" for meetings, events, scheduling,
   and reminders related to calendar events.

4. Use "task" for todo and task-management requests.

5. Use "memory" when the user wants to store or retrieve
   a personal fact or preference.

6. Use "general" for unrelated requests.

7. Do NOT try to list all agents involved.

8. If the request requires multiple actions or agents,
   the Planner will handle the decomposition.

9. Return ONLY valid JSON.


EXAMPLE 1
---------

User:
"Find my emails from Rahul"

Return:

{{
    "agent": "email",
    "intent": "search_email"
}}


EXAMPLE 2
---------

User:
"Remind me to submit my assignment tomorrow"

Return:

{{
    "agent": "calendar",
    "intent": "set_reminder"
}}


EXAMPLE 3
---------

User:
"Remember that I prefer working in the morning"

Return:

{{
    "agent": "memory",
    "intent": "store_preference"
}}


EXAMPLE 4
---------

User:
"I have a meeting with Rahul tomorrow at 10 AM.
Find the related emails, summarize them,
and remind me 30 minutes before the meeting."

The PRIMARY agent is calendar because the request
contains a meeting and reminder.

Return:

{{
    "agent": "calendar",
    "intent": "multi_step_request"
}}


USER REQUEST
------------

{user_request}


RETURN ONLY JSON:
"""


    # ========================================================
    # Ollama Request
    # ========================================================

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


    # ========================================================
    # Validate LLM Output
    # ========================================================

    llm_decision = RouterDecision(
        agent="general",
        intent="unknown",
        complexity="simple",
        requires_planning=False
    )

    # The LLM only needs to provide agent + intent.
    # We temporarily parse its JSON ourselves.
    import json

    llm_data = json.loads(raw_output)


    # ========================================================
    # Build Final Router Decision
    # ========================================================

    decision = RouterDecision(
        agent=llm_data["agent"],
        intent=llm_data["intent"],
        complexity=(
            "complex"
            if requires_planning
            else "simple"
        ),
        requires_planning=requires_planning
    )


    return decision


# ============================================================
# Main Program
# ============================================================

if __name__ == "__main__":

    user_request = input(
        "Enter your request: "
    ).strip()


    if not user_request:

        print("\nRouter failed:")
        print("User request cannot be empty.")


    else:

        try:

            decision = route_request(user_request)

            print("\nRouter Decision:")
            print("-" * 50)

            print(
                decision.model_dump_json(indent=2)
            )

            print("-" * 50)


        except requests.exceptions.RequestException as e:

            print("\nRouter failed:")
            print("Could not connect to Ollama.")
            print(e)


        except Exception as e:

            print("\nRouter validation failed:")
            print(e)