from typing import TypedDict, Annotated, Sequence
import operator
import json
import random


# from langchain_community.chat_models.fireworks import ChatFireworks
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI


from typing import List, Sequence

from langgraph.graph import END, MessageGraph



from pydantic import BaseModel
from src.common import get, not_init, PREFERENCES_PATH, cprint, Colors
from src.flows import LangChainConstruct

import streamlit as st

DEFAULT_GOAL = """You are an essay assistant tasked with writing excellent 5-paragraph essays.
Generate the best essay possible for the user's request.
If the user provides critique, respond with a revised version of your previous attempts."""

DEFAULT_REFLECTION = """You are a teacher grading an essay submission. Generate critique and recommendations for the user's submission.
Provide detailed recommendations, including requests for length, depth, style, etc."""

class SingleWorkflowConfig(BaseModel):
# class SingleWorkflowConfig():
    # TODO this should NOT be blank!!! just give an example because the user is stupid!!!
    workflow_name: str = "Little Prince Essay"
    goal: str = DEFAULT_GOAL
    reflection_goal: str = DEFAULT_REFLECTION


class WorkflowConfigurationSet(BaseModel):
    selected_workflow_index: int = 0
    workflows: List[SingleWorkflowConfig] = [SingleWorkflowConfig()]







class ChainReflectionBotSETTINGS(BaseModel):
    max_iterations: int = 3
    OPENAI_API_KEY: str = ""



class ChainReflectionBot(LangChainConstruct):
    emoji = "🧠"
    name = "Reflection"
    avatar_filename = "reflection.png"
    preamble = "Let's reflect on this for a moment... 🤔"


    def __init__(self):
        super().__init__()


    def setup(self):
        self._is_setup = True # TODO - deprecate this.

        try:
            settings_filename = PREFERENCES_PATH / f"botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                # TODO - can I move this boilerplate function into the base class?
                self.settings = ChainReflectionBotSETTINGS(**settings)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.exception(e)
            self.settings = ChainReflectionBotSETTINGS()

        
        try:
            workflows_filename = PREFERENCES_PATH / f"workflows_{self.name}.json"
            with open(workflows_filename, "r") as f:
                all_workflows = json.loads(f.read())
                # TODO - can I move this boilerplate function into the base class?
                self.all_workflows = WorkflowConfigurationSet(**all_workflows)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.exception(e)
            self.all_workflows = WorkflowConfigurationSet()
            with open(workflows_filename, "w") as f:
                f.write(json.dumps(self.all_workflows.model_dump()))
        
        # clamp selected_workflow_index to 0, len(workflows)
        self.all_workflows.selected_workflow_index = max(0, min(self.all_workflows.selected_workflow_index, len(self.all_workflows.workflows) - 1))

        # index = self.all_workflows.selected_workflow_index if self.all_workflows.selected_workflow_index < len(self.all_workflows.workflows) else 0
        # cprint(f"Selected workflow index: {self.all_workflows.selected_workflow_index}", Colors.YELLOW)
        # index = max(0, min(self.all_workflows.selected_workflow_index, len(self.all_workflows.workflows) - 1))  # clamp to 0, len(workflows)
        # try:
        #     index = self.all_workflows.selected_workflow_index
        #     workflow = self.all_workflows.workflows[index]
        # except Exception as e:
        #     index = 0
        #     workflow = self.all_workflows.workflows[index]

        if len(self.all_workflows.workflows) == 0:
                self.all_workflows.workflows.append(SingleWorkflowConfig())

        self.graph = compile_runnable(self.settings, self.all_workflows.workflows[self.all_workflows.selected_workflow_index])
        # self.graph = compile_runnable(self.settings, workflow)


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

        st.select_slider("Number of :red[Review Iterations]", options=[1, 2, 3, 4, 5], key="max_iterations", value=self.settings.max_iterations, on_change=update, args=("max_iterations",))

        with st.expander(":blue[API KEYS]", expanded=False):
            st.text_input(":blue[OPENAI_API_KEY]", key="OPENAI_API_KEY", value=self.settings.OPENAI_API_KEY, on_change=update, args=("OPENAI_API_KEY",))


    async def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Run `setup()` first!")

        async for event in self.graph.astream([HumanMessage(content=prompt)],):
            # {
            #   "generate": "AIMessage(content='\"The Little Prince\" by Antoine de Saint-Exupéry is a timeless classic that continues to resonate with readers of all ages due to its profound messages and themes that are still relevant in modern life. This novella, originally published in 1943, may seem like a simple children\\'s story on the surface, but its deeper meaning and philosophical insights make it a powerful and thought-provoking work that offers valuable lessons for today\\'s world.\\n\\nOne of the central themes in \"The Little Prince\" is the importance of seeing beyond the surface and looking with the heart. In a society that is increasingly focused on materialism and superficial appearances, this message is more relevant than ever. The Little Prince teaches us the value of connecting with others on a deeper level, understanding their true essence, and appreciating the beauty that lies beneath the surface.\\n\\nMoreover, the novella highlights the significance of imagination and creativity in a world that often prioritizes logic and practicality. The Little Prince\\'s ability to see the world through a childlike perspective reminds us of the importance of maintaining a sense of wonder and curiosity in our lives. In a time where innovation and originality are highly valued, this message serves as a reminder of the power of imagination in shaping our perceptions and experiences.\\n\\nAnother key theme in \"The Little Prince\" is the exploration of human relationships and the complexities of love, friendship, and loss. The interactions between the Little Prince and the various characters he encounters during his journey serve as a reflection of the diverse relationships we navigate in our own lives. Through these encounters, the novella prompts readers to reflect on the nature of human connections, the importance of empathy and understanding, and the impact of our actions on those around us.\\n\\nFurthermore, the novella touches upon themes of loneliness, isolation, and the search for meaning and purpose in life. In today\\'s fast-paced and interconnected world, many people struggle with feelings of loneliness and alienation despite being constantly surrounded by others. The Little Prince\\'s journey to find his place in the universe and his quest for connection and understanding resonate with individuals who are searching for their own sense of belonging and purpose in a complex and often overwhelming world.\\n\\nIn conclusion, \"The Little Prince\" continues to be a relevant and poignant work that offers valuable insights and lessons for modern life. Its timeless themes of love, friendship, imagination, and the importance of looking beyond the surface serve as a powerful reminder of the enduring human experience and the universal truths that connect us all. As we navigate the complexities of the modern world, the messages of The Little Prince remind us to approach life with an open heart, a curious mind, and a deep appreciation for the beauty and wonder that surrounds us.')"
            # }
            # yield ("Reflection Bot:", event)
            yield event # {"node_name": output}


    def display_workplace_variables(self):
        def update(key):

            if key == "selected_workflow_index":
                new_value = st.session_state[key]
                # get first instance of this name in the list
                # [wf for wf in self.all_workflows.workflows if wf.workflow_name == new_value][0]
                self.all_workflows.selected_workflow_index = [index for index, wf in enumerate(self.all_workflows.workflows) if wf.workflow_name == new_value][0]
            else:
                new_value = st.session_state[key]
                # check if this name already exists in the list
                if new_value not in [wf.workflow_name for wf in self.all_workflows.workflows]:
                    self.all_workflows.workflows[self.all_workflows.selected_workflow_index].__dict__[key] = new_value
                else:
                    self.all_workflows.workflows[self.all_workflows.selected_workflow_index].__dict__[key] = f"{new_value}_{random.randint(100, 999)}"

            # save to file
            workflows_filename = PREFERENCES_PATH / f"workflows_{self.name}.json"
            with open(workflows_filename, "w") as f:
                f.write(json.dumps(self.all_workflows.model_dump()))

            self.setup()
            st.toast("Updated!")

        def save_as_new():
            workflow_name = f"{st.session_state.workflow_name} copy"
            # if st.session_state.workflow_name in [wf.workflow_name for wf in self.all_workflows.workflows]:
            #     workflow_name = f"{st.session_state.workflow_name}_{random.randint(100, 999)}"
            # else:
            #     workflow_name = st.session_state.workflow_name

            current_wf = SingleWorkflowConfig(workflow_name=workflow_name, goal=st.session_state.goal, reflection_goal=st.session_state.reflection_goal)

            # make index the last one
            self.all_workflows.workflows.append(current_wf)
            self.all_workflows.selected_workflow_index = len(self.all_workflows.workflows) - 1

            workflows_filename = PREFERENCES_PATH / f"workflows_{self.name}.json"
            with open(workflows_filename, "w") as f:
                f.write(json.dumps(self.all_workflows.model_dump()))

            self.setup()


        def delete_workflow():
            del self.all_workflows.workflows[self.all_workflows.selected_workflow_index]
            self.all_workflows.selected_workflow_index = max(0, min(self.all_workflows.selected_workflow_index, len(self.all_workflows.workflows) - 1))

            # if no workflows left, add a new one
            if len(self.all_workflows.workflows) == 0:
                self.all_workflows.workflows.append(SingleWorkflowConfig())

            workflows_filename = PREFERENCES_PATH / f"workflows_{self.name}.json"
            with open(workflows_filename, "w") as f:
                f.write(json.dumps(self.all_workflows.model_dump()))

            self.setup()


        st.selectbox("Select Workflow", options=[wf.workflow_name for wf in self.all_workflows.workflows], key="selected_workflow_index", index=self.all_workflows.selected_workflow_index, on_change=update, args=("selected_workflow_index",))

        cols2 = st.columns((1, 1))
        with cols2[0]:
            st.button(":green[Duplicate Workflow]", on_click=save_as_new)
        with cols2[1]:
            st.button(":red[Delete Workflow]", on_click=delete_workflow)
        st.divider()

        st.text_input("Workflow name:", value=self.all_workflows.workflows[self.all_workflows.selected_workflow_index].workflow_name, key="workflow_name", on_change=update, args=("workflow_name",))
        st.text_area("Generation goal:", value=self.all_workflows.workflows[self.all_workflows.selected_workflow_index].goal, key="goal", on_change=update, args=("goal",))

        st.text_area("Reflection prompt", value=self.all_workflows.workflows[self.all_workflows.selected_workflow_index].reflection_goal, key="reflection_goal", on_change=update, args=("reflection_goal",))
    





def compile_runnable(settings: ChainReflectionBotSETTINGS, workflow_vars: SingleWorkflowConfig):

    if not_init('workflow_vars'):
        # st.session_state.workflow_vars = SingleWorkflowConfig()
        st.session_state.workflow_vars = workflow_vars


    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
        st.error("settings.OPENAI_API_KEY is blank")
        return None

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                workflow_vars.goal, # This is a 2-tuple of (role, content) with role being 'human', 'user', 'ai', 'assistant', or 'system'.
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
            workflow_vars.reflection_goal, # This is a 2-tuple of (role, content) with role being 'human', 'user', 'ai', 'assistant', or 'system'.
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
        if len(state) / 2 > settings.max_iterations: # TODO... hmmm
            return END
        return "reflect"


    builder.add_conditional_edges("generate", should_continue)
    builder.add_edge("reflect", "generate")
    graph = builder.compile() # returns a Pregel
    return graph
