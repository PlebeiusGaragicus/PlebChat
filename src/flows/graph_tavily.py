from typing import TypedDict, Annotated, Sequence
import operator
import json

from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
from langchain.tools.render import format_tool_to_openai_function
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END

from src.common import get, PREFERENCES_PATH

from pydantic import BaseModel

import streamlit as st

from src.flows import AIWorkflowAbsctractConstruct


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]



class TavilyBotSettings(BaseModel):
    nothing: bool = False
    something: bool = True
    API_KEY: str = ""



class TavilyBot(AIWorkflowAbsctractConstruct):
    emoji = "🤖"
    name = "tavily"

    def __init__(self):
        super().__init__()
        self.agentic = True
        self.preamble = "TavilyBot is ready to search the web for you!"


    def setup(self):
        self._is_setup = True

        self.graph = compiled_graph()

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = TavilyBotSettings(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = TavilyBotSettings()


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("TavilyBot.run(): not setup yet! Run `setup()` first!")
        # yield "TavilyBot is ready to search the web for you!"

        inputs = {"messages": [HumanMessage(content=prompt)]}
        for output in self.graph.stream(inputs):
            # stream() yields dictionaries with output keyed by node name
            for key, value in output.items():
                yield key, value
            #     print(f"Output from node '{key}':")
            #     print("---")
            #     print(value)
            # print("\n---\n")



    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        st.toggle("Nothing", key="nothing", value=self.settings.nothing, on_change=update, args=("nothing",))
        st.toggle("Something", key="something", value=self.settings.something, on_change=update, args=("something",))
        st.text_input("API_KEY", key="API_KEY", value=self.settings.API_KEY, on_change=update, args=("API_KEY",))




def compiled_graph():
    tools = [TavilySearchResults(max_results=1)]
    tool_executor = ToolExecutor(tools)

    model = ChatOpenAI(temperature=0, streaming=True)

    functions = [format_tool_to_openai_function(t) for t in tools]
    model = model.bind_functions(functions)


    def should_continue(state):
        messages = state["messages"]
        last_message = messages[-1]
        if "function_call" not in last_message.additional_kwargs:
            return "end"
        else:
            return "continue"

    def call_model(state):
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    def call_tool(state):
        messages = state["messages"]
        last_message = messages[-1]
        action = ToolInvocation(
            tool=last_message.additional_kwargs["function_call"]["name"],
            tool_input=json.loads(
                last_message.additional_kwargs["function_call"]["arguments"]
            ),
        )
        response = tool_executor.invoke(action)
        function_message = FunctionMessage(content=str(response), name=action.tool)
        return {"messages": [function_message]}


    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tool)

    workflow.set_entry_point("agent")

    cond_edges = {
            "continue": "action",
            "end": END,
        }
    workflow.add_conditional_edges( "agent", should_continue, cond_edges)
    workflow.add_edge("action", "agent")
    app = workflow.compile()
    return app









# USE IT



# from langchain_core.messages import HumanMessage

# inputs = {"messages": [HumanMessage(content="what is the weather in sf")]}
# app.invoke(inputs)







# ### STREAM THE STEPS OF THE CHAIN
# inputs = {"messages": [HumanMessage(content="what is the weather in sf")]}
# for output in app.stream(inputs):
#     # stream() yields dictionaries with output keyed by node name
#     for key, value in output.items():
#         print(f"Output from node '{key}':")
#         print("---")
#         print(value)
#     print("\n---\n")






# ## STREAM THE ACTUAL TOKENS FROM THE AGENTS 
# inputs = {"messages": [HumanMessage(content="what is the weather in sf?")]}

# async for output in app.astream_log(inputs, include_types=["llm"]):
#     # astream_log() yields the requested logs (here LLMs) in JSONPatch format
#     for op in output.ops:
#         if op["path"] == "/streamed_output/-":
#             # this is the output from .stream()
#             ...
#         elif op["path"].startswith("/logs/") and op["path"].endswith(
#             "/streamed_output/-"
#         ):
#             # because we chose to only include LLMs, these are LLM tokens
#             print(op["value"])