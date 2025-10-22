import os
from datetime import datetime, timezone
import json

import requests
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch
from auth0_ai_langchain.async_authorization import get_async_authorization_credentials
from auth0_ai_langchain.auth0_ai import Auth0AI
from langchain_core.tools import StructuredTool
from langchain_core.runnables import ensure_config
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


auth0_ai = Auth0AI()


def return_ciba_credentials():
    credentials = get_async_authorization_credentials()

    print("=====")
    print("return_ciba_credentials")
    print(json.dumps(credentials, indent=2))
    print("=====")

    result = {
        "access_token_exists": "access_token" in credentials,
        "id_token_exists": "id_token" in credentials,
        "expires_in": credentials["expires_in"],
        "scope": credentials["scope"],
    }
    return result


test_ciba = auth0_ai.with_async_authorization(
    scopes=["test:ciba"],
    audience=os.getenv("API_AUDIENCE"),
    binding_message="TEST Client Initiated Backchannel Authentication",
    on_authorization_request="block",
    user_id=lambda *_, **__: ensure_config().get("configurable", {}).get("user_id"),
)(
    StructuredTool.from_function(
        func=return_ciba_credentials,
        name="test_ciba",
        description="Test tool for Client Initiated Backchannel Authentication (CIBA)",
    )
)

search = TavilySearch(max_results=2)

toolset = [
    clock,
    search,
    userinfo,
    test_ciba,
]
