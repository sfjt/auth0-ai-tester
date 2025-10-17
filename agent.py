from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

from tools import toolset

load_dotenv()

llm = init_chat_model(model="openai:gpt-4o").bind_tools(toolset)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("agent", agent)
    tool_node = ToolNode(toolset)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("agent", tools_condition)
    graph_builder.add_edge("tools", "agent")
    graph_builder.add_edge(START, "agent")
    memory = InMemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    print(graph.get_graph().draw_ascii())

    return graph
