import requests
from pydantic import BaseModel, Field
from typing import List, Literal


# ============================================================
# Ollama Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"


# ============================================================
# Allowed Agents
# ============================================================

AgentName = Literal[
    "email",
    "calendar",
    "task",
    "memory"
]


# ============================================================
# Plan Step Schema
# ============================================================

class PlanStep(BaseModel):
    step: int = Field(ge=1)

    agent: AgentName

    action: str = Field(min_length=1)


# ============================================================
# Complete Plan Schema
# ============================================================

class TaskPlan(BaseModel):
    steps: List[PlanStep] = Field(min_length=1)


# ============================================================
# Planner Function
# ============================================================

def create_plan(user_request: str) -> TaskPlan:

    prompt = f"""
You are the Planning Agent for a personal productivity AI system.

Your job is to break a complex user request into the MINIMUM number
of executable steps.

The available agents are:

- email
- calendar
- task
- memory


AGENT RESPONSIBILITIES
----------------------

email:
- Search emails
- Read emails
- Retrieve emails
- Summarize emails
- Find emails related to a topic, person, or meeting

calendar:
- Find meetings
- Find events
- Check meeting details
- Schedule meetings
- Create reminders related to meetings
- Modify or cancel calendar events

task:
- Create todo items
- Complete todo items
- Update tasks
- Delete tasks
- Manage task lists

memory:
- Store user preferences
- Store user facts
- Retrieve stored user preferences or facts

IMPORTANT:
Do NOT use the memory agent unless the user explicitly asks
to remember, store, save, or retrieve a personal fact or preference.


PLANNING RULES
--------------

1. Each step must have exactly ONE responsible agent.

2. The ONLY valid agents are:
   "email", "calendar", "task", "memory"

3. NEVER invent another agent.

4. Do NOT create unnecessary steps.

5. Do NOT create a memory step unless the user explicitly
   asks to remember or store something.

6. Searching and summarizing emails must use the email agent.

7. Finding meetings and calendar events must use the calendar agent.

8. Reminders related to meetings must use the calendar agent.

9. Todo items must use the task agent.

10. Preserve dependencies between steps.

11. If a later action depends on information from an earlier action,
    the dependent action must come AFTER the earlier action.

12. Do NOT perform calculations that should be handled by Python.
    For example, if the user says "30 minutes before the meeting",
    describe it as:
    "Create a reminder 30 minutes before the meeting."

13. Do NOT invent information that is not present in the request.

14. Every action must be something that the assigned agent can
    actually execute.

15. Return ONLY valid JSON.


EXAMPLE
-------

User request:

"I have a meeting with Rahul tomorrow at 10 AM.
Find the related emails, summarize them,
and remind me 30 minutes before the meeting."


Correct plan:

{{
    "steps": [
        {{
            "step": 1,
            "agent": "calendar",
            "action": "Find Rahul's meeting tomorrow at 10 AM"
        }},
        {{
            "step": 2,
            "agent": "email",
            "action": "Find emails related to Rahul's meeting"
        }},
        {{
            "step": 3,
            "agent": "email",
            "action": "Summarize the important points from the related emails"
        }},
        {{
            "step": 4,
            "agent": "calendar",
            "action": "Create a reminder 30 minutes before the meeting"
        }}
    ]
}}


USER REQUEST
------------

{user_request}


RETURN ONLY JSON IN THIS FORMAT:

{{
    "steps": [
        {{
            "step": 1,
            "agent": "calendar",
            "action": "..."
        }}
    ]
}}
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
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    raw_output = data["response"]

    # ========================================================
    # Validate LLM output using Pydantic
    # ========================================================

    plan = TaskPlan.model_validate_json(raw_output)

    # ========================================================
    # Additional application-level validation
    # ========================================================

    for expected_step, plan_step in enumerate(plan.steps, start=1):

        if plan_step.step != expected_step:
            raise ValueError(
                f"Invalid step numbering: "
                f"expected {expected_step}, "
                f"got {plan_step.step}"
            )

    return plan


# ============================================================
# Main Program
# ============================================================

if __name__ == "__main__":

    user_request = input(
        "Enter a complex request: "
    ).strip()

    if not user_request:
        print("\nPlanner failed:")
        print("User request cannot be empty.")

    else:

        try:

            plan = create_plan(user_request)

            print("\nTask Plan:")
            print("-" * 50)

            for step in plan.steps:

                print(
                    f"{step.step}. "
                    f"[{step.agent}] "
                    f"{step.action}"
                )

            print("-" * 50)

            print("\nPlan generated successfully.")

        except requests.exceptions.RequestException as e:

            print("\nPlanner failed:")
            print("Could not connect to Ollama.")
            print(e)

        except ValueError as e:

            print("\nPlanner validation failed:")
            print(e)

        except Exception as e:

            print("\nPlanner failed:")
            print(e)