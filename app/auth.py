import os

from fastapi import Request, Response
from auth0_fastapi.auth import AuthClient
from auth0_fastapi.config import Auth0Config
from dotenv import load_dotenv

load_dotenv()

auth_config = Auth0Config(
    domain=os.getenv("AUTH0_DOMAIN"),
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    audience=os.getenv("API_AUDIENCE"),
    authorization_params={"scope": "openid profile email offline_access"},
    app_base_url="http://localhost:8000",
    secret=os.getenv("APP_SECRET_KEY"),
)

auth_client = AuthClient(auth_config)


async def get_access_token(request: Request, response: Response) -> str:
    store_options = {"request": request, "response": response}
    return await auth_client.client.get_access_token(store_options=store_options)
