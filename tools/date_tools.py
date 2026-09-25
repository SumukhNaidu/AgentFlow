from datetime import datetime, timedelta


# ============================================================
# Resolve Relative Date
# ============================================================

def resolve_date(date_reference: str) -> str:

    if not date_reference:
        return None

    reference = date_reference.strip().lower()

    today = datetime.now().date()

    if reference == "today":

        return today.isoformat()

    if reference == "tomorrow":

        return (today + timedelta(days=1)).isoformat()

    if reference == "yesterday":

        return (today - timedelta(days=1)).isoformat()

    raise ValueError(
        f"Unsupported date reference: {date_reference}"
    )