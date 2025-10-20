from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from app.tools import toolset

load_dotenv()

llm = init_chat_model(model="openai:gpt-5-nano").bind_tools(toolset)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("agent", agent_node)
tool_node = ToolNode(toolset)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("agent", tools_condition)
graph_builder.add_edge("tools", "agent")
graph_builder.add_edge(START, "agent")
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

graph_png = graph.get_graph().draw_mermaid_png()


async def invoke(user_input: str, token: str, user_id: str):
    initial_state = State(messages=[HumanMessage(content=user_input)])
    config = {
        "configurable": {
            "thread_id": "TEST",
            "api_access_token": token,
            "user_id": user_id
        }
    }
    response = await graph.ainvoke(initial_state, config)
    print(response)

    return response["messages"][-1].content
