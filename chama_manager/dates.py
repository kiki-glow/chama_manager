"""Date helpers: month arithmetic for contributions and loan schedules."""

import calendar
from datetime import date

def month_start(day: date) -> date:
    """Return the first day of the month containing `day`."""
    return day.replace(day=1)

def add_months(day: date, months: int) -> date:
    """Move `day` forward by whole months, clamping to the month's last day.
    
    Example: 31 Jan + 1 month -> 28 Feb (29 in a leap year).
    """
    # count months since year 0 so year rollovers are handled by divmod
    total = day.year * 12 + (day.month - 1) + months
    year, month_index = divmod(total, 12)
    month = month_index + 1
    last_day =  calendar.monthrange(year, month)[1]
    
    return date(year, month, min(day.day, last_day))