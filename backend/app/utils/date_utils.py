from datetime import datetime, date
from typing import Union

def format_date_to_str(dt: Union[datetime, date], fmt: str = "%Y-%m-%d") -> str:
    """
    Formats a datetime or date object into a standard string representation.
    """
    return dt.strftime(fmt)

def parse_str_to_date(date_str: str, fmt: str = "%Y-%m-%d") -> date:
    """
    Parses a formatted date string into a Python date object.
    """
    return datetime.strptime(date_str, fmt).date()
