
from langchain_core.tools import tool
from datetime import datetime

@tool
def get_current_date() -> str:
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def get_current_time() -> str:
    """Returns the current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")

