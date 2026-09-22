from tools.calendar_tools import (
    search_calendar,
    create_reminder
)


# ============================================================
# Calendar Agent
# ============================================================

def handle_calendar_action(action: str):

    action_lower = action.lower()


    # --------------------------------------------------------
    # Find meeting
    # --------------------------------------------------------

    if "find" in action_lower and "meeting" in action_lower:

        # For our current demo, we know the request contains
        # Rahul and tomorrow.
        #
        # We will make this more general later.

        if "rahul" in action_lower:

            events = search_calendar(
                "Rahul",
                "2026-09-18"
            )

            return {
                "type": "calendar_search",
                "events": events
            }


    # --------------------------------------------------------
    # Create reminder
    # --------------------------------------------------------

    if "reminder" in action_lower:

        # In the current demo we use the Rahul meeting.
        events = search_calendar(
            "Rahul",
            "2026-09-18"
        )

        if not events:

            return {
                "type": "error",
                "message": "Meeting not found."
            }

        event = events[0]

        reminder = create_reminder(
            event,
            minutes_before=30
        )

        return {
            "type": "reminder_created",
            "reminder": reminder
        }


    # --------------------------------------------------------
    # Unsupported action
    # --------------------------------------------------------

    return {
        "type": "error",
        "message": f"Unsupported calendar action: {action}"
    }


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    action = input(
        "Enter calendar action: "
    ).strip()

    result = handle_calendar_action(action)

    print("\nCalendar Agent Result:")
    print(result)