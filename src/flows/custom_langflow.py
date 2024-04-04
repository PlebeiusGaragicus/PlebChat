from typing import TypedDict, Annotated, Sequence
import operator
import json







from pydantic import BaseModel
from src.common import get, PREFERENCES_PATH, AVATAR_PATH
from src.flows import AIWorkflowAbsctractConstruct

import streamlit as st





class CustomLangFlowSETTINGS(BaseModel):
    nothing: int = 0


class CustomLangFlow(AIWorkflowAbsctractConstruct):
    name = "⛓️ :grey[Custom LangFlow]"
    avatar_filename = "langflow.png"
    preamble = "Your custom LangFlow endpoints. 🪢"

    def __init__(self):
        super().__init__()
        self.agentic = True # TODO - move this into the base class



    def setup(self):
        self._is_setup = True

        self.settings = CustomLangFlowSETTINGS()
        self.graph = compile_runnable(self.settings)


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("CustomLangFlow.run(): not setup yet! Run `setup()` first!")
        
        yield ("__end__", "This is just a stub for now.")





    def display_settings(self):
        st.write("No settings... yet!")



def compile_runnable(settings: CustomLangFlowSETTINGS):
    return None
