import time
import json

from pydantic import BaseModel

import streamlit as st

from src.flows import AIWorkflowAbsctractConstruct



class echobot_settings(BaseModel):
    uppercase: bool = False
    reverse: bool = False
    sleep_time: float = 1.0
    caboose: str = "🚂"


class echobot(AIWorkflowAbsctractConstruct):
    def __init__(self):
        super().__init__(emoji="🤖", name="echobot")
        # self.settings = echobot_settings()
        self.agentic = False
        self.preamble = "Echobot is ready to echo your prompt!"

    def setup(self):
        self._is_setup = True
        print("Setting up Echobot...")
        # load settings from file
        try:
            with open(f"{self.name}_settings.json", "r") as f:
                settings = json.loads(f.read())
                self.settings = echobot_settings(**settings)
        except FileNotFoundError:
            self.settings = echobot_settings()


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Echobot.run(): not setup yet! Run `setup()` first!")

        echo = prompt.split(" ")
        if self.settings.uppercase:
            echo = [e.upper() for e in echo]
        if self.settings.reverse:
            echo = echo[::-1]

        for e in echo:
            time.sleep(self.settings.sleep_time)
            yield f"{e} "


    
    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            if key == 'caboose':
                new_value = new_value[:1]
            self.settings.__dict__[key] = new_value

            # save to file
            with open(f"{self.name}_settings.json", "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        st.toggle("Uppercase", key="uppercase", value=self.settings.uppercase, on_change=update, args=("uppercase",))
        st.toggle("Reverse", key="reverse", value=self.settings.reverse, on_change=update, args=("reverse",))
        st.slider("Sleep time", min_value=0.01, max_value=1.0, key="sleep_time", value=self.settings.sleep_time, on_change=update, args=("sleep_time",))
        st.text_input("Caboose", key="caboose", value=self.settings.caboose, on_change=update, args=("caboose",))





class dummybot(AIWorkflowAbsctractConstruct):
    def __init__(self):
        super().__init__(emoji="🤖", name="dummybot")
        # self.settings = echobot_settings()

        self.preamble = "I can do this if I keep trying.  Don't give up and you'll get there!"

    def setup(self):
        self._is_setup = True
        print("Setting up Dummybot...")

        # load settings from file
        try:
            with open(f"{self.name}_settings.json", "r") as f:
                settings = json.loads(f.read())
                self.settings = echobot_settings(**settings)
        except FileNotFoundError:
            self.settings = echobot_settings()


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Echobot.run(): not setup yet! Run `setup()` first!")

        print(f"Running `{self.name}` with prompt: `{prompt}`\nkwargs: {kwargs}")
        self.runnable(prompt)
    

    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            if key == 'caboose':
                new_value = new_value[:1]
            self.settings.__dict__[key] = new_value

            # save to file
            with open(f"{self.name}_settings.json", "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        st.toggle("Uppercase", key="uppercase", value=self.settings.uppercase, on_change=update, args=("uppercase",))
        st.toggle("Reverse", key="reverse", value=self.settings.reverse, on_change=update, args=("reverse",))
        st.slider("Sleep time", min_value=0.1, max_value=3.0, key="sleep_time", value=self.settings.sleep_time, on_change=update, args=("sleep_time",))
        st.text_input("Caboose", key="caboose", value=self.settings.caboose, on_change=update, args=("caboose",))




class tommybot(AIWorkflowAbsctractConstruct):
    def __init__(self):
        super().__init__(emoji="🤖", name="tommybot")
        # self.settings = echobot_settings() #NOTE: DO NOT DO THIS.. IT OVERWRITES THE SETTINGS TO DEFAULT

        self.preamble = "I can do this, but I can't do it alone!  Stay connected with your network!"

    def setup(self):
        self._is_setup = True
        print("Setting up Tommybot...")

        # load settings from file
        try:
            with open(f"{self.name}_settings.json", "r") as f:
                settings = json.loads(f.read())
                self.settings = echobot_settings(**settings)
        except FileNotFoundError:
            self.settings = echobot_settings()


    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Echobot.run(): not setup yet! Run `setup()` first!")

        print(f"Running `{self.name}` with prompt: `{prompt}`\nkwargs: {kwargs}")
        self.runnable(prompt)
    

    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            if key == 'caboose':
                new_value = new_value[:1]
            self.settings.__dict__[key] = new_value
            
            # save to file
            with open(f"{self.name}_settings.json", "w") as f:
                f.write(json.dumps(self.settings.model_dump()))


        st.toggle("Uppercase", key="uppercase", value=self.settings.uppercase, on_change=update, args=("uppercase",))
        st.toggle("Reverse", key="reverse", value=self.settings.reverse, on_change=update, args=("reverse",))
        st.slider("Sleep time", min_value=0.1, max_value=3.0, key="sleep_time", value=self.settings.sleep_time, on_change=update, args=("sleep_time",))
        st.text_input("Caboose", key="caboose", value=self.settings.caboose, on_change=update, args=("caboose",))

"""

data = sp.pydantic_form(key="my_form", model=get("construct").settings)

if data:
    st.json(data.json())
                
"""
