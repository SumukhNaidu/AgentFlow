# ============================================================
# Demo Email Data
# ============================================================

EMAILS = [
    {
        "id": 1,
        "sender": "rahul@example.com",
        "subject": "Project Meeting Tomorrow",
        "date": "2026-09-18",
        "body": (
            "Hi Esha, let's discuss the project progress "
            "and the remaining tasks in tomorrow's meeting."
        )
    },
    {
        "id": 2,
        "sender": "rahul@example.com",
        "subject": "Project Architecture Discussion",
        "date": "2026-09-17",
        "body": (
            "Please review the updated architecture before "
            "our meeting. We should also discuss the API changes."
        )
    },
    {
        "id": 3,
        "sender": "sonali@example.com",
        "subject": "Hackathon Update",
        "date": "2026-09-18",
        "body": (
            "The hackathon submission deadline has been updated."
        )
    }
]


# ============================================================
# Search Emails
# ============================================================

def search_emails(
    keyword: str
):

    keyword = keyword.lower()

    results = []

    for email in EMAILS:

        searchable_text = (
            email["sender"]
            + " "
            + email["subject"]
            + " "
            + email["body"]
        ).lower()

        if keyword in searchable_text:

            results.append(email)

    return results


# ============================================================
# Summarize Emails
# ============================================================

def get_email_content(emails):

    if not emails:
        return "No related emails were found."

    content = []

    for email in emails:

        content.append(
            f"""
From: {email["sender"]}
Subject: {email["subject"]}
Date: {email["date"]}
Body: {email["body"]}
"""
        )

    return "\n".join(content)

# ============================================================
# Summarize Emails Using Local LLM
# ============================================================

def summarize_emails(emails):

    if not emails:
        return "No related emails were found."

    content = get_email_content(emails)

    prompt = f"""
You are an email summarization assistant.

Summarize the following emails.

Focus ONLY on:
- Main discussion points
- Important decisions
- Action items
- Things that should be discussed in the meeting

Do not invent information.

Keep the summary concise and easy to understand.

EMAILS:
{content}

Return only the summary.
"""

    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False
    }

    import requests

    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    return data["response"].strip()