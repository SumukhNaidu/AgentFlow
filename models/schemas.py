from typing import Optional
from pydantic import BaseModel


# ============================================================
# Calendar Parameters
# ============================================================

class CalendarParameters(BaseModel):

    person: Optional[str] = None

    date_reference: Optional[str] = None

    time: Optional[str] = None

    title: Optional[str] = None


# ============================================================
# Reminder Parameters
# ============================================================

class ReminderParameters(BaseModel):

    minutes_before: int


# ============================================================
# Email Parameters
# ============================================================

class EmailParameters(BaseModel):

    keyword: Optional[str] = None