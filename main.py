from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers.string import StrOutputParser

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4o")
    messages = []
    str_parser = StrOutputParser()

    while True:
        user_input = input("You: ")

        if user_input == "exit":
            break

        messages.append(HumanMessage(content=user_input))
        response = llm.invoke(messages)
        str_response = str_parser.invoke(response)
        messages.append(AIMessage(content=str_response))
        print(f"Agent: {str_response}")
