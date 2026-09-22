from agents.router import route_request
from agents.planner import create_plan


# ============================================================
# Orchestrator
# ============================================================

def process_request(user_request: str):

    print("\n" + "=" * 60)
    print("USER REQUEST")
    print("=" * 60)
    print(user_request)


    # ========================================================
    # STEP 1: ROUTER
    # ========================================================

    print("\n[1] Running Router...")

    decision = route_request(user_request)

    print("\nRouter Decision:")
    print(decision.model_dump_json(indent=2))


    # ========================================================
    # STEP 2: Decide whether planning is required
    # ========================================================

    if decision.requires_planning:

        print("\n[2] Complex request detected.")
        print("    Sending request to Planner...")


        # ====================================================
        # STEP 3: PLANNER
        # ====================================================

        plan = create_plan(user_request)


        print("\nPlanner Output:")
        print("-" * 60)

        for step in plan.steps:

            print(
                f"{step.step}. "
                f"[{step.agent}] "
                f"{step.action}"
            )

        print("-" * 60)


        # ====================================================
        # STEP 4: Execution will come later
        # ====================================================

        print("\n[3] Plan created successfully.")
        print("    Agent execution layer is not implemented yet.")


        return {
            "type": "planned",
            "router": decision,
            "plan": plan
        }


    else:

        # ====================================================
        # SIMPLE REQUEST
        # ====================================================

        print("\n[2] Simple request detected.")

        print(
            f"    Request will be handled by: "
            f"{decision.agent}"
        )

        print(
            f"    Intent: {decision.intent}"
        )


        # ====================================================
        # Direct execution will come later
        # ====================================================

        print("\n[3] Direct agent execution is not implemented yet.")


        return {
            "type": "direct",
            "router": decision
        }


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    user_request = input(
        "\nEnter your request: "
    ).strip()


    if not user_request:

        print("\nRequest cannot be empty.")


    else:

        try:

            process_request(user_request)

        except Exception as e:

            print("\nOrchestrator failed:")
            print(e)