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
    max_results: int = 3
    TAVILY_API_KEY: str = ""
    OPENAI_API_KEY: str = ""



class TavilyBot(AIWorkflowAbsctractConstruct):
    emoji = "🔍"
    name = "Tavily"

    def __init__(self):
        super().__init__()
        self.agentic = True


    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = TavilyBotSettings(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = TavilyBotSettings()

        self.graph = compile_runnable(self.settings)


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("TavilyBot.run(): not setup yet! Run `setup()` first!")

        inputs = {"messages": [HumanMessage(content=prompt)]}
        for output in self.graph.stream(inputs):
            # stream() yields dictionaries with output keyed by node name
            for key, value in output.items():
                yield key, value




    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

            self.setup() # we have to re-init the graph with the new settings

        st.select_slider("Number of Search Results", options=[1, 2, 3, 4, 5], key="max_results", value=self.settings.max_results, on_change=update, args=("max_results",))

        st.text_input("TAVILY_API_KEY", key="TAVILY_API_KEY", value=self.settings.TAVILY_API_KEY, on_change=update, args=("TAVILY_API_KEY",))
        st.text_input("OPENAI_API_KEY", key="OPENAI_API_KEY", value=self.settings.OPENAI_API_KEY, on_change=update, args=("OPENAI_API_KEY",))




def compile_runnable(settings: TavilyBotSettings):
    # tools = [TavilySearchResults(max_results=1)] # TODO turn this into a setting!
    tools = [TavilySearchResults(max_results=settings.max_results)]
    tool_executor = ToolExecutor(tools)

    model = ChatOpenAI(temperature=0, streaming=True)
    # model = ChatOpenAI(temperature=0, streaming=True, api_key=settings.OPENAI_API_KEY)

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
