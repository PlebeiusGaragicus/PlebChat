import dotenv
dotenv.load_dotenv()

from typing import List
from pydantic import BaseModel
import json
import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="LangGraph Agent API")


from src.graphs.phi.graph import graph as phi_graph
from src.graphs.phi.commands import handle_commands as phi_handle_commands


from src.graphs.llama.graph import graph as llama_graph
from src.graphs.llama.commands import handle_commands as llama_handle_commands


from src.graphs.research.research_rabbit import graph as research_graph



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"], # USE FOR DEVELOPMENT
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_sse_response(stream):
    """Create a StreamingResponse with SSE configuration."""
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no"
        }
    )

# THESE ARE THE KINDS GENERATED FROM OUR LANDGRAPH AGENT
# on_chat_model_start
# on_chat_model_stream
# on_chat_model_end
# on_llm_start
# on_llm_stream
# on_llm_end
# on_chain_start
# on_chain_stream
# on_chain_end
# on_tool_start
# on_tool_stream
# on_tool_end
# on_retriever_start
# on_retriever_chunk
# on_retriever_end
# on_prompt_start
# on_prompt_end

async def stream_graph_events(graph, input_data):
    """Stream events from a graph with standardized formatting."""

    async for event in graph.astream_events(input=input_data, version="v2"):
        # print(event, end='\n')

        kind = event["event"]
        print(kind, end='\n')

        if kind == 'on_chat_model_start':
            # Send a control event with type
            yield f"event: status\ndata: {{'status': 'model_start'}}\n\n"

        elif kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Content events don't need special event type - they're default
                content_encoded = content.replace('\n', '\\n')
                yield f"data: {content_encoded}\n\n"

        elif kind in ['on_tool_start', 'on_tool_end', 'on_chain_start', 'on_chain_end']:
            # Send control events for tool/chain status
            yield f"event: status\ndata: {{'status': '{kind}'}}\n\n"


async def stream_simple_response(message: str):
    """Stream a simple string message in SSE format."""
    yield f"data: {message}\n\n"



class PostRequest(BaseModel):
    user_message: str
    messages: List[dict]
    body: dict



@app.get("/health")
async def health_check():
    return {"status": "healthy"}




##########################################################################################
@app.post("/phi", response_class=StreamingResponse)
async def main(request: PostRequest):
    query = request.user_message
    if query.startswith("/"):
        return create_sse_response(phi_handle_commands(request))

    # Create a default message from the user query if messages list is empty
    message = {"role": "user", "content": query}
    if request.messages and len(request.messages) > 0:
        message = request.messages[-1]

    input_data = {"messages": [message]}
    
    return create_sse_response(
        stream_graph_events(
            phi_graph, 
            input_data
        )
    )


##########################################################################################
@app.post("/llama", response_class=StreamingResponse)
async def main(request: PostRequest):
    query = request.user_message
    if query.startswith("/"):
        return create_sse_response(llama_handle_commands(request))

    # Create a default message from the user query if messages list is empty
    message = {"role": "user", "content": query}
    if request.messages and len(request.messages) > 0:
        message = request.messages[-1]

    input_data = {"messages": [message]}
    
    return create_sse_response(
        stream_graph_events(
            llama_graph, 
            input_data
        )
    )


##########################################################################################
@app.post("/research", response_class=StreamingResponse)
async def main(request: PostRequest):
    query = request.user_message
    if query.startswith("/"):
        return create_sse_response(stream_simple_response("no commands available"))

    # # Create a default message from the user query if messages list is empty
    # message = {"role": "user", "content": query}
    # if request.messages and len(request.messages) > 0:
    #     message = request.messages[-1]

    input_data = {"research_topic": query}
    
    return create_sse_response(
        stream_graph_events(
            research_graph, 
            input_data
        )
    )
