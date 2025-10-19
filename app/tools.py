import os
from datetime import datetime, timezone

import requests
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()


def _authorization_header(config: RunnableConfig) -> dict:
    access_token = config.get("configurable", {}).get("api_access_token")
    return {"Authorization": f"Bearer {access_token}"}


@tool
def clock():
    """Return current time in UTC string format"""
    utc_now = datetime.now(timezone.utc)
    return utc_now.isoformat()


@tool
def userinfo(config: RunnableConfig):
    """Return user info"""
    url = f"https://{os.getenv('AUTH0_DOMAIN')}/userinfo"

    try:
        response = requests.get(url, headers=_authorization_header(config))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return str(e)


search = TavilySearch(max_results=2)

toolset = [
    clock,
    search,
    userinfo,
]
