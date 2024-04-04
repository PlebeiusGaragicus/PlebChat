from typing import TypedDict, Annotated, Sequence
import operator
import json


from langchain_community.chat_models.fireworks import ChatFireworks
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI


from typing import List, Sequence

from langgraph.graph import END, MessageGraph



from pydantic import BaseModel
from src.common import get, PREFERENCES_PATH, AVATAR_PATH
from src.flows import LangChainConstruct

import streamlit as st



class WorkflowVariables(BaseModel):
    # TODO this should NOT be blank!!! just give an example because the user is stupid!!!
    reflection_goal: str = ""




class ChainReflectionBotSETTINGS(BaseModel):
    max_iterations: int = 3



class ChainReflectionBot(LangChainConstruct):
    name = "🧠 :red[Reflection]"
    avatar_filename = "reflection.png"
    preamble = "Let's reflect on this for a moment... 🤔"


    def __init__(self):
        super().__init__()


    def setup(self):
        self._is_setup = True # TODO - deprecate this.

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                # TODO - can I move this boilerplate function into the base class?
                self.settings = ChainReflectionBotSETTINGS(**settings)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.exception(e)
            self.settings = ChainReflectionBotSETTINGS()

        self.workflow_vars = WorkflowVariables()
        self.graph = compile_runnable(self.settings, self.workflow_vars)


    def display_settings(self):
        def update(key):
            # TODO - move this into the base class!!!
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

            self.setup() # we have to re-init the graph with the new settings

        st.select_slider("Number of :red[Iterations]", options=[1, 2, 3, 4, 5], key="max_iterations", value=self.settings.max_iterations, on_change=update, args=("max_iterations",))

        with st.expander(":blue[API KEYS]", expanded=False):
            st.text_input(":blue[OPENAI_API_KEY]", key="OPENAI_API_KEY", value=self.settings.OPENAI_API_KEY, on_change=update, args=("OPENAI_API_KEY",))


    "Generate an essay on the topicality of The Little Prince and its message in modern life"
    async def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Run `setup()` first!")
        
        ### EXAMPLE FROM TAVILY CHAIN
        # inputs = {"messages": [HumanMessage(content=prompt)]}
        # for output in self.graph.stream(inputs):
        #     # stream() yields dictionaries with output keyed by node name
        #     for key, value in output.items():
        #         yield key, value

        async for event in self.graph.astream(
            [
                HumanMessage(content=prompt)
            ],
        ):
            # print(event)
            yield ("Reflection Bot:", event)

        yield ("__end__", "ok, I'm done!")


    def invoke(self, prompt, **kwargs):
        import asyncio
        return asyncio.run(self.run(prompt, **kwargs))




# def compile_runnable(settings: ChainReflectionBotSETTINGS, workflowvars: WorkflowVariables) -> RunnableSerializable:
def compile_runnable(settings: ChainReflectionBotSETTINGS, workflow_vars: WorkflowVariables):

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
        st.error("settings.OPENAI_API_KEY is blank")
        # raise ValueError("settings.OPENAI_API_KEY is blank")
        return None

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an essay assistant tasked with writing excellent 5-paragraph essays."
                " Generate the best essay possible for the user's request."
                " If the user provides critique, respond with a revised version of your previous attempts.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    llm = ChatOpenAI(streaming=True, api_key=settings.OPENAI_API_KEY)
    generate = prompt | llm



    reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a teacher grading an essay submission. Generate critique and recommendations for the user's submission."
            " Provide detailed recommendations, including requests for length, depth, style, etc.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])
    reflect = reflection_prompt | llm




    async def generation_node(state: Sequence[BaseMessage]):
        return await generate.ainvoke({"messages": state})


    async def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
        # Other messages we need to adjust
        cls_map = {"ai": HumanMessage, "human": AIMessage}
        # First message is the original user request. We hold it the same for all nodes
        translated = [messages[0]] + [
            cls_map[msg.type](content=msg.content) for msg in messages[1:]
        ]
        res = await reflect.ainvoke({"messages": translated})
        # We treat the output of this as human feedback for the generator
        return HumanMessage(content=res.content)


    builder = MessageGraph()
    builder.add_node("generate", generation_node)
    builder.add_node("reflect", reflection_node)
    builder.set_entry_point("generate")


    def should_continue(state: List[BaseMessage]):
        if len(state) > 6:
            # End after 3 iterations
            return END
        return "reflect"


    builder.add_conditional_edges("generate", should_continue)
    builder.add_edge("reflect", "generate")
    graph = builder.compile() # returns a Pregel
    return graph
