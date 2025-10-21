import os
import json

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from auth0_fastapi.server.routes import router, register_auth_routes
from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client
from dotenv import load_dotenv
import uvicorn

from auth import auth_client, auth_config, get_access_token

load_dotenv()

langgraph_client = get_client(url=os.getenv("LANGGRAPH_URL"))
app = FastAPI()


@app.get("/")
async def root():
    return FileResponse("chat_interface/index.html")


async def get_thread(request: Request):
    thread_id = await get_thread_id(request)
    return await langgraph_client.threads.get(thread_id)


async def get_thread_id(request: Request, create_new=False):
    if "thread_id" not in request.session or create_new:
        thread = await langgraph_client.threads.create()
        request.session["thread_id"] = thread["thread_id"]

    return request.session["thread_id"]


def has_content_and_type(m: dict):
    return (
        "content" in m
        and type(m["content"]) is str
        and len(m["content"])
        and "type" in m
    )


def is_ai_response(m: dict):
    return has_content_and_type(m) and m["type"] == "ai"


def is_human_prompt(m: dict):
    return has_content_and_type(m) and m["type"] == "human"


@app.get("/history")
async def get_history(request: Request, response: Response):
    await auth_client.require_session(request, response)
    thread = await get_thread(request)
    history = []
    print(thread)
    if "values" in thread and "messages" in thread["values"]:
        history = [
            {"content": m["content"], "type": m["type"]}
            for m in thread["values"]["messages"]
            if is_human_prompt(m) or is_ai_response(m)
        ]
    return history


class Prompt(BaseModel):
    prompt: str


@app.post("/agent")
async def agent(
    data: Prompt,
    request: Request,
    response: Response,
):
    session = await auth_client.require_session(request, response)
    user_id = session["user"]["sub"]
    token = await get_access_token(request, response)
    result = await langgraph_client.runs.wait(
        thread_id=await get_thread_id(request),
        assistant_id="agent",
        input={"messages": [HumanMessage(data.prompt)]},
        config={
            "configurable": {
                "thread_id": "TEST",
                "api_access_token": token,
                "user_id": user_id,
            }
        },
    )
    print(json.dumps(result, indent=2))
    ai_responses = [m["content"] for m in result["messages"] if is_ai_response(m)]
    return {"ai": ai_responses[-1]}


app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET_KEY"))
app.state.auth_config = auth_config
app.state.auth_client = auth_client
register_auth_routes(router, auth_config)
app.include_router(router)

uvicorn.run(app, host="localhost", port=8000, reload=False)
