# import time
# import json
# from typing import Type, Union

# from pydantic import BaseModel

# import streamlit as st


class AIWorkflowAbsctractConstruct:
    def __init__(self, emoji: str, name: str):
        self.emoji = emoji
        self.name = name
        self._is_setup = False

        self.setup()
    
    def setup(self):
        raise NotImplementedError("Must implement setup() this in child class!")

    def run(self, prompt, **kwargs):
        raise NotImplementedError("Must implement run() this in child class!")

    def display_settings(self):
        raise NotImplementedError("Must implement display_settings() this in child class!")


class StreamingLLM(AIWorkflowAbsctractConstruct):
    agentic = False

