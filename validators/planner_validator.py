from agents.planner import TaskPlan


# ============================================================
# Planner Validation Result
# ============================================================

class ValidationResult:

    def __init__(
        self,
        valid: bool,
        errors: list[str] | None = None
    ):
        self.valid = valid
        self.errors = errors or []


# ============================================================
# Planner Validator
# ============================================================

def validate_plan(
    user_request: str,
    plan: TaskPlan
) -> ValidationResult:

    errors = []

    request = user_request.lower()

    # ========================================================
    # Rule 1 — Plan must contain steps
    # ========================================================

    if not plan.steps:

        errors.append(
            "Plan contains no steps."
        )

        return ValidationResult(
            valid=False,
            errors=errors
        )

    # ========================================================
    # Rule 2 — Step numbers must be sequential
    # ========================================================

    expected_step = 1

    for step in plan.steps:

        if step.step != expected_step:

            errors.append(
                f"Expected step {expected_step}, "
                f"but received step {step.step}."
            )

        expected_step += 1

    # ========================================================
    # Rule 3 — Memory should only be used when requested
    # ========================================================

    memory_keywords = [
        "remember",
        "store",
        "save",
        "memorize",
        "memory",
        "preference",
        "personal fact"
    ]

    user_requested_memory = any(
        keyword in request
        for keyword in memory_keywords
    )

    for step in plan.steps:

        if step.agent == "memory":

            if not user_requested_memory:

                errors.append(
                    "Memory agent was used even though "
                    "the user did not request information "
                    "to be remembered or stored."
                )

    # ========================================================
    # Rule 4 — Email summarization must use email agent
    # ========================================================

    for step in plan.steps:

        action = step.action.lower()

        is_summary_action = (
            "summar" in action
        )

        is_email_summary = (
            "email" in action
            or "emails" in action
            or "mail" in action
        )

        if is_summary_action and is_email_summary:

            if step.agent != "email":

                errors.append(
                    "Email summarization must be handled "
                    "by the email agent."
                )

    # ========================================================
    # Rule 5 — Email searching must use email agent
    # ========================================================

    for step in plan.steps:

        action = step.action.lower()

        is_email_action = (
            "email" in action
            or "emails" in action
            or "mail" in action
        )

        is_email_operation = (
            "find" in action
            or "search" in action
            or "retrieve" in action
            or "read" in action
            or "summar" in action
        )

        if is_email_action and is_email_operation:

            if step.agent != "email":

                errors.append(
                    "Email operations must be handled "
                    "by the email agent."
                )

    # ========================================================
    # Rule 6 — Actual calendar operations must use calendar
    # ========================================================

    # IMPORTANT:
    # Words such as "meeting" or "event" can be context rather
    # than the operation itself.
    #
    # Examples:
    #
    # "Find Rahul's meeting"
    #     -> calendar operation
    #
    # "Find emails related to Rahul's meeting"
    #     -> email operation
    #
    # "Create a reminder before the meeting"
    #     -> reminder operation (handled by Rule 7)
    #
    # "Store Rahul's meeting information"
    #     -> memory operation
    #
    # Therefore, explicit operation keywords take priority over
    # contextual calendar words.

    calendar_context_keywords = [
        "meeting",
        "calendar",
        "event",
        "appointment"
    ]

    calendar_operation_keywords = [
        "find",
        "search",
        "look up",
        "lookup",
        "check",
        "view",
        "show",
        "schedule",
        "reschedule",
        "cancel"
    ]

    for step in plan.steps:

        action = step.action.lower()

        # Reminder operations are handled separately by Rule 7.
        is_reminder_operation = (
            "reminder" in action
            or "remind" in action
        )

        # Email operations take priority over calendar context.
        is_email_operation = (
            (
                "email" in action
                or "emails" in action
                or "mail" in action
            )
            and any(
                keyword in action
                for keyword in [
                    "find",
                    "search",
                    "retrieve",
                    "read",
                    "summar"
                ]
            )
        )

        # Memory operations take priority over calendar context.
        is_memory_operation = (
            step.agent == "memory"
            and any(
                keyword in action
                for keyword in [
                    "store",
                    "save",
                    "remember",
                    "memorize"
                ]
            )
        )

        contains_calendar_context = any(
            keyword in action
            for keyword in calendar_context_keywords
        )

        is_calendar_operation = (
            contains_calendar_context
            and any(
                keyword in action
                for keyword in calendar_operation_keywords
            )
            and not is_email_operation
            and not is_memory_operation
            and not is_reminder_operation
        )

        if is_calendar_operation:

            if step.agent != "calendar":

                errors.append(
                    "Meeting, calendar, event, and appointment "
                    "operations must be handled by the calendar agent."
                )

    # ========================================================
    # Rule 7 — Reminders must use calendar
    # ========================================================

    for step in plan.steps:

        action = step.action.lower()

        is_reminder = (
            "reminder" in action
            or "remind" in action
        )

        if is_reminder:

            if step.agent != "calendar":

                errors.append(
                    "Reminders must be handled "
                    "by the calendar agent."
                )

    # ========================================================
    # Rule 8 — Task operations must use task agent
    # ========================================================

    task_keywords = [
        "todo",
        "to-do",
        "task",
        "checklist"
    ]

    task_action_keywords = [
        "create",
        "add",
        "complete",
        "update",
        "delete",
        "remove"
    ]

    for step in plan.steps:

        action = step.action.lower()

        contains_task_keyword = any(
            keyword in action
            for keyword in task_keywords
        )

        contains_task_action = any(
            keyword in action
            for keyword in task_action_keywords
        )

        if (
            contains_task_keyword
            and contains_task_action
        ):

            if step.agent != "task":

                errors.append(
                    "Todo and task-management operations "
                    "must be handled by the task agent."
                )

    # ========================================================
    # Rule 9 — Calendar reminder dependency
    # ========================================================

    has_reminder = False
    has_calendar_event_lookup = False

    for step in plan.steps:

        action = step.action.lower()

        if (
            "reminder" in action
            or "remind" in action
        ):

            has_reminder = True

        if (
            "meeting" in action
            or "calendar" in action
            or "event" in action
            or "appointment" in action
        ):

            if (
                "find" in action
                or "search" in action
                or "look" in action
                or "check" in action
            ):

                has_calendar_event_lookup = True

    if (
        has_reminder
        and not has_calendar_event_lookup
    ):

        errors.append(
            "A reminder depends on a calendar event, "
            "but the plan does not contain a step to "
            "identify the relevant meeting or event."
        )

    # ========================================================
    # Rule 10 — Reminder must occur after meeting lookup
    # ========================================================

    meeting_lookup_step = None
    reminder_step = None

    for step in plan.steps:

        action = step.action.lower()

        if (
            "meeting" in action
            or "event" in action
            or "appointment" in action
        ):

            if (
                "find" in action
                or "search" in action
                or "look" in action
                or "check" in action
            ):

                if meeting_lookup_step is None:

                    meeting_lookup_step = step.step

        if (
            "reminder" in action
            or "remind" in action
        ):

            if reminder_step is None:

                reminder_step = step.step

    if (
        meeting_lookup_step is not None
        and reminder_step is not None
    ):

        if reminder_step <= meeting_lookup_step:

            errors.append(
                "The reminder step must occur after "
                "the meeting/event lookup step."
            )

    # ========================================================
    # Rule 11 — Do not use memory for ordinary execution
    # ========================================================

    for step in plan.steps:

        action = step.action.lower()

        if step.agent == "memory":

            execution_keywords = [
                "meeting",
                "email",
                "calendar",
                "reminder",
                "task",
                "todo"
            ]

            contains_execution_keyword = any(
                keyword in action
                for keyword in execution_keywords
            )

            if (
                contains_execution_keyword
                and not user_requested_memory
            ):

                errors.append(
                    "Memory agent should not be used for "
                    "ordinary execution tasks."
                )

    # ========================================================
    # Final Validation Result
    # ========================================================

    if errors:

        return ValidationResult(
            valid=False,
            errors=errors
        )

    return ValidationResult(
        valid=True
    )


# ============================================================
# Validator Tests
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # TEST 1 — Correct plan
    # ========================================================

    print("\n" + "=" * 70)
    print("TEST 1 — Correct Plan")
    print("=" * 70)

    correct_request = (
        "I have a meeting with Rahul tomorrow at 10 AM. "
        "Find the related emails, summarize them, "
        "and remind me 30 minutes before the meeting."
    )

    correct_plan = TaskPlan(
        steps=[
            {
                "step": 1,
                "agent": "calendar",
                "action": "Find Rahul's meeting tomorrow at 10 AM"
            },
            {
                "step": 2,
                "agent": "email",
                "action": "Find emails related to Rahul's meeting"
            },
            {
                "step": 3,
                "agent": "email",
                "action": "Summarize the important points from the related emails"
            },
            {
                "step": 4,
                "agent": "calendar",
                "action": "Create a reminder 30 minutes before the meeting"
            }
        ]
    )

    result = validate_plan(
        correct_request,
        correct_plan
    )

    print("\nExpected: VALID")
    print(f"Actual:   {'VALID' if result.valid else 'INVALID'}")

    if result.errors:
        for error in result.errors:
            print(f"- {error}")


    # ========================================================
    # TEST 2 — Email operation incorrectly assigned
    # ========================================================

    print("\n" + "=" * 70)
    print("TEST 2 — Email Operation Assigned to Calendar")
    print("=" * 70)

    bad_email_plan = TaskPlan(
        steps=[
            {
                "step": 1,
                "agent": "calendar",
                "action": "Find Rahul's meeting tomorrow at 10 AM"
            },
            {
                "step": 2,
                "agent": "calendar",
                "action": "Find emails related to Rahul's meeting"
            },
            {
                "step": 3,
                "agent": "email",
                "action": "Summarize the emails"
            },
            {
                "step": 4,
                "agent": "calendar",
                "action": "Create a reminder 30 minutes before the meeting"
            }
        ]
    )

    result = validate_plan(
        correct_request,
        bad_email_plan
    )

    print("\nExpected: INVALID")
    print(f"Actual:   {'VALID' if result.valid else 'INVALID'}")

    for error in result.errors:
        print(f"- {error}")


    # ========================================================
    # TEST 3 — Reminder assigned to wrong agent
    # ========================================================

    print("\n" + "=" * 70)
    print("TEST 3 — Reminder Assigned to Email Agent")
    print("=" * 70)

    bad_reminder_plan = TaskPlan(
        steps=[
            {
                "step": 1,
                "agent": "calendar",
                "action": "Find Rahul's meeting tomorrow at 10 AM"
            },
            {
                "step": 2,
                "agent": "email",
                "action": "Find emails related to Rahul's meeting"
            },
            {
                "step": 3,
                "agent": "email",
                "action": "Summarize the emails"
            },
            {
                "step": 4,
                "agent": "email",
                "action": "Create a reminder 30 minutes before the meeting"
            }
        ]
    )

    result = validate_plan(
        correct_request,
        bad_reminder_plan
    )

    print("\nExpected: INVALID")
    print(f"Actual:   {'VALID' if result.valid else 'INVALID'}")

    for error in result.errors:
        print(f"- {error}")


    # ========================================================
    # TEST 4 — Memory used without user requesting it
    # ========================================================

    print("\n" + "=" * 70)
    print("TEST 4 — Unnecessary Memory Agent")
    print("=" * 70)

    bad_memory_plan = TaskPlan(
        steps=[
            {
                "step": 1,
                "agent": "calendar",
                "action": "Find Rahul's meeting tomorrow at 10 AM"
            },
            {
                "step": 2,
                "agent": "memory",
                "action": "Store Rahul's meeting information"
            },
            {
                "step": 3,
                "agent": "email",
                "action": "Find emails related to Rahul's meeting"
            },
            {
                "step": 4,
                "agent": "email",
                "action": "Summarize the emails"
            },
            {
                "step": 5,
                "agent": "calendar",
                "action": "Create a reminder 30 minutes before the meeting"
            }
        ]
    )

    result = validate_plan(
        correct_request,
        bad_memory_plan
    )

    print("\nExpected: INVALID")
    print(f"Actual:   {'VALID' if result.valid else 'INVALID'}")

    for error in result.errors:
        print(f"- {error}")


    # ========================================================
    # TEST 5 — Reminder before meeting lookup
    # ========================================================

    print("\n" + "=" * 70)
    print("TEST 5 — Reminder Before Meeting Lookup")
    print("=" * 70)

    bad_order_plan = TaskPlan(
        steps=[
            {
                "step": 1,
                "agent": "calendar",
                "action": "Create a reminder 30 minutes before the meeting"
            },
            {
                "step": 2,
                "agent": "calendar",
                "action": "Find Rahul's meeting tomorrow at 10 AM"
            },
            {
                "step": 3,
                "agent": "email",
                "action": "Find emails related to Rahul's meeting"
            },
            {
                "step": 4,
                "agent": "email",
                "action": "Summarize the emails"
            }
        ]
    )

    result = validate_plan(
        correct_request,
        bad_order_plan
    )

    print("\nExpected: INVALID")
    print(f"Actual:   {'VALID' if result.valid else 'INVALID'}")

    for error in result.errors:
        print(f"- {error}")


    # ========================================================
    # TEST 6 — Incorrect step numbering
    # ========================================================

    print("\n" + "=" * 70)
    print("TEST 6 — Incorrect Step Numbering")
    print("=" * 70)

    bad_numbering_plan = TaskPlan(
        steps=[
            {
                "step": 1,
                "agent": "calendar",
                "action": "Find Rahul's meeting tomorrow at 10 AM"
            },
            {
                "step": 3,
                "agent": "email",
                "action": "Find emails related to Rahul's meeting"
            },
            {
                "step": 4,
                "agent": "email",
                "action": "Summarize the emails"
            }
        ]
    )

    result = validate_plan(
        correct_request,
        bad_numbering_plan
    )

    print("\nExpected: INVALID")
    print(f"Actual:   {'VALID' if result.valid else 'INVALID'}")

    for error in result.errors:
        print(f"- {error}")


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("VALIDATOR TESTING COMPLETE")
    print("=" * 70)
