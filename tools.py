from datetime import datetime, timezone

from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()


@tool
def clock():
    """Return current time in UTC stringo format"""
    utc_now = datetime.now(timezone.utc)
    return utc_now.isoformat()


search = TavilySearch(max_results=2)

toolset = [
    clock,
    search
]
