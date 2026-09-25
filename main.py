from agents.router import route_request
from agents.planner import create_plan
from agents.executor import execute_plan

from validators.planner_validator import validate_plan


def run_agent_system(user_request: str):

    print("\n" + "=" * 70)
    print("USER REQUEST")
    print("=" * 70)

    print(user_request)

    # ============================================================
    # STEP 1 — ROUTER
    # ============================================================

    print("\n" + "=" * 70)
    print("STEP 1 — ROUTER")
    print("=" * 70)

    decision = route_request(user_request)

    print(f"Agent:             {decision.agent}")
    print(f"Intent:            {decision.intent}")
    print(f"Complexity:        {decision.complexity}")
    print(f"Requires Planning: {decision.requires_planning}")

    # ============================================================
    # DIRECT EXECUTION
    # ============================================================

    if not decision.requires_planning:

        print("\n" + "=" * 70)
        print("DIRECT EXECUTION")
        print("=" * 70)

        print(
            f"Request can be handled directly by "
            f"the {decision.agent} agent."
        )

        return {
            "type": "direct",
            "router": decision
        }

    # ============================================================
    # STEP 2 — PLANNER
    # ============================================================

    print("\n" + "=" * 70)
    print("STEP 2 — PLANNER")
    print("=" * 70)

    plan = create_plan(user_request)

    print("\nGenerated Plan:")
    print("-" * 70)

    for step in plan.steps:
        print(
            f"{step.step}. "
            f"[{step.agent}] "
            f"{step.action}"
        )

    print("-" * 70)

    # ============================================================
    # STEP 3 — PLAN VALIDATION
    # ============================================================

    print("\n" + "=" * 70)
    print("STEP 3 — PLAN VALIDATION")
    print("=" * 70)

    validation_result = validate_plan(
        user_request,
        plan
    )

    if validation_result.valid:

        print("VALID")
        print("Plan passed all validation checks.")

    else:

        print("INVALID")

        print("\nValidation Errors:")

        for error in validation_result.errors:
            print(f"- {error}")

        print("\nExecution stopped.")

        return {
            "type": "invalid_plan",
            "router": decision,
            "plan": plan,
            "validation": validation_result
        }

    # ============================================================
    # STEP 4 — EXECUTOR
    # ============================================================

    print("\n" + "=" * 70)
    print("STEP 4 — EXECUTOR")
    print("=" * 70)

    execution_result = execute_plan(plan)

    # ============================================================
    # FINAL RESULT
    # ============================================================

    print("\n" + "=" * 70)
    print("FINAL EXECUTION STATE")
    print("=" * 70)

    state = execution_result["state"]

    for key, value in state.get_all().items():

        print(f"\n{key}:")
        print(value)

    return {
        "type": "execution_complete"
        if execution_result["success"]
        else "execution_failed",

        "router": decision,
        "plan": plan,
        "validation": validation_result,
        "execution": execution_result
    }


if __name__ == "__main__":

    user_request = (
        "I have a meeting with Rahul tomorrow at 10 AM. "
        "Find the related emails, summarize them, "
        "and remind me 30 minutes before the meeting."
    )

    result = run_agent_system(user_request)

    print("\n" + "=" * 70)
    print("SYSTEM RESULT")
    print("=" * 70)

    print(
        f"Result Type: {result['type']}"
    )