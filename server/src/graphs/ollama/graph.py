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

def ollama_llm_call(state: State):
    MODEL = "llama3.1:latest"
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
graph_builder.add_node("ollama_llm_call", ollama_llm_call)
graph_builder.add_edge("__start__", "ollama_llm_call")
graph_builder.add_edge("ollama_llm_call", "__end__")

graph = graph_builder.compile()
