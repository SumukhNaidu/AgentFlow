from agents.extractor import (
    extract_calendar_parameters,
    extract_reminder_parameters
)

from tools.calendar_tools import (
    search_calendar,
    create_reminder
)

from tools.date_tools import resolve_date


def handle_calendar_action(action: str, state=None):

    action_lower = action.lower()

    # ============================================================
    # CALENDAR SEARCH
    # ============================================================

    if (
        "find" in action_lower
        or "search" in action_lower
        or "look" in action_lower
        or "check" in action_lower
    ) and (
        "meeting" in action_lower
        or "event" in action_lower
        or "appointment" in action_lower
        or "calendar" in action_lower
    ):

        parameters = extract_calendar_parameters(action)

        if not parameters.person:
            return {
                "type": "calendar_error",
                "error": "Calendar search requires a person."
            }

        if not parameters.date_reference:
            return {
                "type": "calendar_error",
                "error": "Calendar search requires a date."
            }

        try:
            date = resolve_date(parameters.date_reference)

        except ValueError as e:
            return {
                "type": "calendar_error",
                "error": str(e)
            }

        events = search_calendar(
            person=parameters.person,
            date=date
        )

        return {
            "type": "calendar_search",
            "parameters": parameters.model_dump(),
            "resolved_date": date,
            "events": events
        }

    # ============================================================
    # REMINDER
    # ============================================================

    if (
        "reminder" in action_lower
        or "remind" in action_lower
    ):

        reminder_parameters = extract_reminder_parameters(action)

        # --------------------------------------------------------
        # First try to use the event already found by a previous
        # execution step.
        # --------------------------------------------------------

        event = None

        if state is not None:
            event = state.get("calendar_event")

        # --------------------------------------------------------
        # If there is no previous event, try extracting one from
        # the current action.
        #
        # This is useful for standalone reminder requests.
        # --------------------------------------------------------

        if event is None:

            calendar_parameters = extract_calendar_parameters(action)

            if calendar_parameters.person and calendar_parameters.date_reference:

                try:
                    date = resolve_date(
                        calendar_parameters.date_reference
                    )

                except ValueError as e:
                    return {
                        "type": "calendar_error",
                        "error": str(e)
                    }

                events = search_calendar(
                    person=calendar_parameters.person,
                    date=date
                )

                if events:
                    event = events[0]

        # --------------------------------------------------------
        # No event available
        # --------------------------------------------------------

        if event is None:
            return {
                "type": "calendar_error",
                "error": (
                    "Reminder requires a previously identified "
                    "calendar event."
                )
            }

        # --------------------------------------------------------
        # Create reminder
        # --------------------------------------------------------

        reminder = create_reminder(
            event,
            minutes_before=reminder_parameters.minutes_before
        )

        return {
            "type": "reminder_created",
            "parameters": reminder_parameters.model_dump(),
            "event": event,
            "reminder": reminder
        }

    return {
        "type": "calendar_error",
        "error": "Unsupported calendar action."
    }