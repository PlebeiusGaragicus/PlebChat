import time
import json

from pydantic import BaseModel

import streamlit as st

from src.flows import StreamingLLM
from src.persist import PREFERENCES_PATH
from src.common import get



class echobot_settings(BaseModel):
    uppercase: bool = False
    reverse: bool = False
    sleep_time: float = 0.05



class testing_echobot(StreamingLLM):
    """ This is the base class for the testing echobots """
    def just_echo(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("Echobot.run(): not setup yet! Run `setup()` first!")

        echo = prompt

        if self.settings.reverse:
            echo = echo[::-1]

        if self.settings.uppercase:
            echo = echo.upper()

        echo = [echo[i:i+5] for i in range(0, len(prompt), 5)]

        for e in echo:
            time.sleep(self.settings.sleep_time)
            yield f"{e}"



class echobot(testing_echobot):
    emoji = "🤖"
    name = "echobot"
    avatar_filename = "echobot.png"
    preamble = "Huh - what did you say?!"


    def __init__(self):
        super().__init__()

    def setup(self):
        self._is_setup = True
        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = echobot_settings(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = echobot_settings()


    def run(self, prompt, **kwargs):
        return self.just_echo(prompt, **kwargs)


    
    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            # if key == 'caboose':
            #     new_value = new_value[:1]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        st.toggle("Uppercase", key="uppercase", value=self.settings.uppercase, on_change=update, args=("uppercase",))
        st.toggle("Reverse", key="reverse", value=self.settings.reverse, on_change=update, args=("reverse",))
        st.slider("Sleep time", min_value=0.0, max_value=0.5, key="sleep_time", value=self.settings.sleep_time, on_change=update, args=("sleep_time",))


    def display_model_card(self):
        st.caption(self.preamble)
        st.warning("This bot is just for testing!!!")




class dummybot(testing_echobot):
    emoji = "🥴"
    name = "dummybot"

    def __init__(self):
        super().__init__()
        # self.settings = echobot_settings()

        self.preamble = "I can do this if I keep trying.  Don't give up and you'll get there!"

    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = echobot_settings(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = echobot_settings()


    def run(self, prompt, **kwargs):
        return self.just_echo(f"{prompt} ...I'm so dumB!", **kwargs)


    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            # if key == 'caboose':
            #     new_value = new_value[:1]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        st.toggle("Uppercase", key="uppercase", value=self.settings.uppercase, on_change=update, args=("uppercase",))
        st.toggle("Reverse", key="reverse", value=self.settings.reverse, on_change=update, args=("reverse",))
        st.slider("Sleep time", min_value=0.05, max_value=1.0, key="sleep_time", value=self.settings.sleep_time, on_change=update, args=("sleep_time",))
        # st.text_input("Caboose", key="caboose", value=self.settings.caboose, on_change=update, args=("caboose",))




class tommybot(testing_echobot):
    emoji = "💪🏼"
    name = "tommybot"

    def __init__(self):
        super().__init__()
        # self.settings = echobot_settings() #NOTE: DO NOT DO THIS.. IT OVERWRITES THE SETTINGS TO DEFAULT

        self.preamble = "I can do this, but I can't do it alone!  Stay connected with your network!"

    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = echobot_settings(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = echobot_settings()


    def run(self, prompt, **kwargs):
        return self.just_echo("Hey, my name's Tommy! 💪", **kwargs)


    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            # if key == 'caboose':
            #     new_value = new_value[:1]
            self.settings.__dict__[key] = new_value
            
            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))


        st.toggle("Uppercase", key="uppercase", value=self.settings.uppercase, on_change=update, args=("uppercase",))
        st.toggle("Reverse", key="reverse", value=self.settings.reverse, on_change=update, args=("reverse",))
        st.slider("Sleep time", min_value=0.05, max_value=1.0, key="sleep_time", value=self.settings.sleep_time, on_change=update, args=("sleep_time",))
        # st.text_input("Caboose", key="caboose", value=self.settings.caboose, on_change=update, args=("caboose",))

"""

data = sp.pydantic_form(key="my_form", model=get("construct").settings)

if data:
    st.json(data.json())
                
"""
