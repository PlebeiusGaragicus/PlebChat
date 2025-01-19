from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.pydantic_v1 import BaseModel
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph

from langchain_ollama import ChatOllama

from .config import OLLAMA_HOST


class State(BaseModel):
    messages: Annotated[list, add_messages]






############################################################################

def chatbot(state: State):
    MODEL = "llama3.2:1b"
    llm = ChatOllama(
        model=MODEL,
        keep_alive="5m",  # Keep the model alive for 5 minutes
        # temperature=0.7,
        base_url=OLLAMA_HOST,  # Connect to Ollama running on host machine
    )

    # The messages are already LangChain message objects, use them directly
    response = llm.stream(state.messages)

    return {"messages": [{"role": "assistant", "content": chunk.content} for chunk in response]}



############################################################################
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge("__start__", "chatbot")
graph_builder.add_edge("chatbot", "__end__")

graph = graph_builder.compile()
