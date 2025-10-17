import gradio as gr
from langchain_core.messages.ai import AIMessage

from agent import build_graph

graph = build_graph()


def chat(user_input: str, _):
    config = {"configurable": {"thread_id": "TEST"}}
    events = graph.stream({"messages": [{"role": "user", "content": user_input}]}, config)
    for event in events:
        print(event)
        for value in event.values():
            message = value["messages"][-1]
            if isinstance(message, AIMessage) and message.content:
                return message.content


gr.ChatInterface(chat).launch()
