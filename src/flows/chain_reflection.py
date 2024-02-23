from typing import TypedDict, Annotated, Sequence
import operator
import json







from pydantic import BaseModel
from src.common import get, PREFERENCES_PATH, AVATAR_PATH
from src.flows import AIWorkflowAbsctractConstruct

import streamlit as st





class ChainReflectionBotSETTINGS(BaseModel):
    max_results: int = 3
    reflection_goal: str = "" # TODO this should NOT be blank!!! just give an example because the user is stupid!!!
    OPENAI_API_KEY: str = ""



class ChainReflectionBot(AIWorkflowAbsctractConstruct):
    emoji = "🧠"
    name = "Reflection"
    avatar_filename = "reflection.png"
    preamble = "Let's reflect on this for a moment... 🤔"

    def __init__(self):
        super().__init__()
        self.agentic = True # TODO - move this into the base class


    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = AVATAR_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                # TODO - can I move this boilerplate function into the base class?
                self.settings = ChainReflectionBotSETTINGS(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = ChainReflectionBotSETTINGS()

        self.graph = compile_runnable(self.settings)


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("TavilyBot.run(): not setup yet! Run `setup()` first!")
        
        yield ("__end__", "this is text")





    def display_settings(self):
        def update(key):
            # TODO - move this into the base class!!!
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

            self.setup() # we have to re-init the graph with the new settings

        st.select_slider("Number of Search Results", options=[1, 2, 3, 4, 5], key="max_results", value=self.settings.max_results, on_change=update, args=("max_results",))

        with st.expander(":blue[API KEYS]", expanded=False):
            st.text_input(":blue[OPENAI_API_KEY]", key="OPENAI_API_KEY", value=self.settings.OPENAI_API_KEY, on_change=update, args=("OPENAI_API_KEY",))




def compile_runnable(settings: ChainReflectionBotSETTINGS):
    pass
