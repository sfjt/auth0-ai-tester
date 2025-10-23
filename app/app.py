import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from auth0_fastapi.server.routes import router, register_auth_routes
from auth0_ai_langchain.async_authorization import GraphResumer
from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client
from langgraph_sdk.schema import Thread
from dotenv import load_dotenv
import uvicorn

from auth import auth_client, auth_config, get_access_token

load_dotenv()


@asynccontextmanager
async def resume_graph(_: FastAPI):
    resumer = GraphResumer(
        lang_graph=get_client(url=os.getenv("LANGGRAPH_URL")),
        filters={"graph_id": "agent"},
    )
    resumer.on_resume(
        lambda thread: print(
            f"Resuming: thread_id {thread['thread_id']} from interruption {thread['interruption_id']}"
        )
    ).on_error(lambda err: print(f"Error: {str(err)}"))
    resumer.start()

    yield

    resumer.stop()


langgraph_client = get_client(url=os.getenv("LANGGRAPH_URL"))
app = FastAPI(lifespan=resume_graph)


@app.get("/")
async def root():
    return FileResponse("chat_interface/index.html")


async def get_thread(request: Request, response: Response):
    try:
        thread_id = await get_thread_id(request, response)
        return await langgraph_client.threads.get(thread_id)
    except Exception as e:
        print(f"{type(e)} {e}")
        thread_id = await get_thread_id(request, response, create_new=True)
        return await langgraph_client.threads.get(thread_id)


async def get_thread_id(request: Request, response: Response, create_new=False):
    if not request.cookies.get("thread_id") or create_new:
        thread = await langgraph_client.threads.create()
        response.set_cookie("thread_id", thread["thread_id"])
        return thread["thread_id"]

    return request.cookies.get("thread_id")


def messages_exist(thread):
    return (
        "values" in thread
        and type(thread["values"]) is dict
        and "messages" in thread["values"]
    )


def has_content_and_type(m: dict, message_types: list[str]):
    return (
        "content" in m
        and type(m["content"]) is str
        and len(m["content"])
        and "type" in m
        and m["type"] in message_types
    )


@app.get("/history")
async def get_history(request: Request, response: Response):
    await auth_client.require_session(request, response)

    thread = await get_thread(request, response)

    print("=====")
    print("GET /history")
    print(json.dumps(thread, indent=2))
    print("=====")

    if values := thread.get("values"):
        return [
            {"content": m["content"], "type": m["type"]}
            for m in values.get("messages", {})
            if has_content_and_type(m, ["human", "ai"])
        ]
    return []


class Prompt(BaseModel):
    prompt: str


@app.post("/agent")
async def agent(
    data: Prompt,
    request: Request,
    response: Response,
):
    try:
        session = await auth_client.require_session(request, response)
        user_id = session["user"]["sub"]
        token = await get_access_token(request, response)
    except Exception as e:
        print(f"{type(e)} {e}")
        return {"error": str(e)}

    thread_id = await get_thread_id(request, response)
    result = await langgraph_client.runs.wait(
        thread_id,
        assistant_id="agent",
        input={"messages": [HumanMessage(data.prompt)]},
        config={
            "configurable": {
                "api_access_token": token,
                "user_id": user_id,
            }
        },
    )

    print("=====")
    print("POST /agent")
    print(json.dumps(result, indent=2))
    print("=====")

    thread = await langgraph_client.threads.get(thread_id)
    if interrupts := thread.get("interrupts"):
        interrupt_id = next(iter(interrupts))
        return {"interrupt": {interrupts[interrupt_id][0]["value"]["message"]}}

    if messages := result.get("messages"):
        ai_responses = [
            m["content"] for m in messages if has_content_and_type(m, ["ai"])
        ]
        return {"ai": ai_responses[-1]}

    return {"error": "No agent response or interrupt returned."}


app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET_KEY"))
app.state.auth_config = auth_config
app.state.auth_client = auth_client
register_auth_routes(router, auth_config)
app.include_router(router)

uvicorn.run(app, host="localhost", port=8000, reload=False)
