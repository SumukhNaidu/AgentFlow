from agents.extractor import (
    extract_calendar_parameters,
    extract_reminder_parameters,
    extract_email_parameters
)


# ============================================================
# Calendar Test
# ============================================================

calendar_action = (
    "Find Rahul's meeting tomorrow at 10 AM"
)

calendar_result = extract_calendar_parameters(
    calendar_action
)

print("\nCalendar Parameters:")
print(calendar_result)


# ============================================================
# Reminder Test
# ============================================================

reminder_action = (
    "Create a reminder 30 minutes before the meeting"
)

reminder_result = extract_reminder_parameters(
    reminder_action
)

print("\nReminder Parameters:")
print(reminder_result)


# ============================================================
# Email Test
# ============================================================

email_action = (
    "Find emails related to Rahul's meeting"
)

email_result = extract_email_parameters(
    email_action
)

print("\nEmail Parameters:")
print(email_result)