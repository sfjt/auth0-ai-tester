from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from tools import toolset

load_dotenv()

llm = init_chat_model(model="openai:gpt-5-nano").bind_tools(toolset)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("agent", agent_node)
    tool_node = ToolNode(toolset)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("agent", tools_condition)
    graph_builder.add_edge("tools", "agent")
    graph_builder.add_edge(START, "agent")
    return graph_builder.compile()


graph = build_graph()
