import time
import json

from pydantic import BaseModel

import streamlit as st

from src.flows import StreamingLLM
from src.persist import PREFERENCES_PATH
from src.common import get


class LLM_SETTINGS_OPENAI:
    api_key: str = ""
    temperature: float = 0.7


class LLM_OPENAI_GPT_3_5(StreamingLLM):
    emoji = "💫"
    name = "GPT-3.5"

    def __init__(self):
        super().__init__(emoji="💫", name="GPT-3.5")

    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = LLM_SETTINGS_OPENAI(**settings)
        except FileNotFoundError:
            self.settings = LLM_SETTINGS_OPENAI()


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Echobot.run(): not setup yet! Run `setup()` first!")
        
        yield "not setup yet, bro"



    
    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        st.text_input("API_KEY", key="api_key", value=self.settings.api_key, on_change=update, args=("api_key",))
        st.slider("Temperature", min_value=0.0, max_value=1.0, key="temperature", value=self.settings.temperature, on_change=update, args=("temperature",))
