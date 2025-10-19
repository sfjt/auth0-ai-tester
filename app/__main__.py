import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from auth0_fastapi.server.routes import router, register_auth_routes
from dotenv import load_dotenv
import uvicorn

from app.auth import auth_client, auth_config, get_access_token
from app.agent import invoke

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


class Prompt(BaseModel):
    prompt: str


@app.get("/")
async def root():
    return FileResponse("app/chat_interface/index.html")


@app.post("/agent")
async def agent(
        data: Prompt,
        request: Request,
        response: Response,
):
    try:
        token = await get_access_token(request, response)
        result = await invoke(
            data.prompt,
            token
        )
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}


app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET_KEY"))
app.state.auth_config = auth_config
app.state.auth_client = auth_client
register_auth_routes(router, auth_config)
app.include_router(router)

uvicorn.run(app, host="localhost", port=8000, reload=False)
