from agents.calendar_agent import handle_calendar_action
from agents.email_agent import handle_email_action


class ExecutionState:
    """
    Stores information produced during execution.

    Later steps can use information produced
    by earlier steps.
    """

    def __init__(self):
        self.data = {
            "calendar_event": None,
            "emails": None,
            "email_summary": None,
            "reminder": None,
            "steps": []
        }

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def add_step_result(self, step, result):
        self.data["steps"].append({
            "step": step,
            "result": result
        })

    def get_all(self):
        return self.data


def update_state_from_result(state, result):
    """
    Stores important outputs from an agent result
    into canonical execution-state fields.
    """

    if not result or not isinstance(result, dict):
        return

    result_type = result.get("type")

    if result_type == "calendar_search":
        events = result.get("events", [])

        if events:
            state.set("calendar_event", events[0])

    elif result_type == "email_search":
        state.set("emails", result.get("emails", []))

    elif result_type == "email_summary":
        state.set("email_summary", result.get("summary"))

        # Also preserve emails if the agent returned them.
        if result.get("emails") is not None:
            state.set("emails", result.get("emails"))

    elif result_type == "reminder_created":
        state.set("reminder", result.get("reminder"))


def execute_step(step, state):
    """
    Execute one planner step using the appropriate agent.
    """

    print("\n" + "-" * 70)
    print(f"EXECUTING STEP {step.step}")
    print("-" * 70)

    print(f"Agent : {step.agent}")
    print(f"Action: {step.action}")

    if step.agent == "calendar":
        result = handle_calendar_action(
            step.action,
            state=state
        )

    elif step.agent == "email":
        result = handle_email_action(
            step.action,
            state=state
        )

    else:
        return {
            "type": "execution_error",
            "error": f"Agent '{step.agent}' is not implemented yet."
        }

    update_state_from_result(state, result)

    state.add_step_result(
        step=step.step,
        result=result
    )

    print("\nStep Result:")
    print(result)

    return result


def execute_plan(plan):
    """
    Execute every step in the validated plan sequentially.
    """

    state = ExecutionState()

    print("\n" + "=" * 70)
    print("EXECUTOR STARTED")
    print("=" * 70)

    for step in plan.steps:

        result = execute_step(step, state)

        # Stop immediately if an agent reports an error.
        if result.get("type") == "execution_error":
            print("\nExecution stopped due to error.")
            return {
                "success": False,
                "state": state,
                "failed_step": step.step,
                "error": result
            }

        if result.get("type", "").endswith("_error"):
            print("\nExecution stopped due to agent error.")
            return {
                "success": False,
                "state": state,
                "failed_step": step.step,
                "error": result
            }

    print("\n" + "=" * 70)
    print("EXECUTION COMPLETED")
    print("=" * 70)

    return {
        "success": True,
        "state": state
    }