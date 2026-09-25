from agents.extractor import extract_email_parameters

from tools.email_tools import (
    search_emails,
    get_email_content,
    summarize_emails
)


def handle_email_action(action: str, state=None):

    action_lower = action.lower()

    # ============================================================
    # EMAIL SEARCH
    # ============================================================

    if (
        "find" in action_lower
        or "search" in action_lower
        or "retrieve" in action_lower
    ):

        parameters = extract_email_parameters(action)

        keyword = parameters.keyword

        if not keyword:
            return {
                "type": "email_error",
                "error": "Email search requires a keyword."
            }

        emails = search_emails(keyword)

        return {
            "type": "email_search",
            "parameters": parameters.model_dump(),
            "emails": emails
        }

    # ============================================================
    # EMAIL SUMMARY
    # ============================================================

    if "summar" in action_lower:

        emails = None

        # --------------------------------------------------------
        # First use emails from a previous step.
        # --------------------------------------------------------

        if state is not None:
            emails = state.get("emails")

        # --------------------------------------------------------
        # If no previous emails exist, perform a fresh search.
        # --------------------------------------------------------

        if emails is None:

            parameters = extract_email_parameters(action)

            keyword = parameters.keyword

            if not keyword:
                return {
                    "type": "email_error",
                    "error": "Email summary requires emails or a keyword."
                }

            emails = search_emails(keyword)

        # --------------------------------------------------------
        # No emails found
        # --------------------------------------------------------

        if not emails:
            return {
                "type": "email_summary",
                "summary": "No relevant emails found.",
                "emails": []
            }

        # --------------------------------------------------------
        # Summarize the actual emails
        # --------------------------------------------------------

        summary = summarize_emails(emails)

        return {
            "type": "email_summary",
            "summary": summary,
            "emails": emails
        }

    return {
        "type": "email_error",
        "error": "Unsupported email action."
    }