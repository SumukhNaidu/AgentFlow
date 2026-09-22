from tools.email_tools import (
    search_emails,
    get_email_content,
    summarize_emails
)
# ============================================================
# Email Agent
# ============================================================

def handle_email_action(action: str):

    action_lower = action.lower()


    # --------------------------------------------------------
    # Search emails
    # --------------------------------------------------------

    if (
        "find" in action_lower
        and "email" in action_lower
    ):

        # Current demo implementation
        # We will make this dynamic later.

        if "rahul" in action_lower:

            emails = search_emails("Rahul")

            return {
                "type": "email_search",
                "emails": emails
            }


    # --------------------------------------------------------
    # Summarize emails
    # --------------------------------------------------------

    if "summarize" in action_lower:

     emails = search_emails("Rahul")

     summary = summarize_emails(emails)

     return {
         "type": "email_summary",
         "summary": summary
    }


    # --------------------------------------------------------
    # Unsupported action
    # --------------------------------------------------------

    return {
        "type": "error",
        "message": f"Unsupported email action: {action}"
    }


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    action = input(
        "Enter email action: "
    ).strip()

    result = handle_email_action(action)

    print("\nEmail Agent Result:")
    print(result) 