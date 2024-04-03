import os
import json
import random
import math

import streamlit as st

from mistralai.models.chat_completion import ChatMessage

# import tiktoken
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.function import FunctionMessage


from src.VERSION import VERSION
from src.common import (
    ASSETS_PATH,
    AVATAR_PATH,
    is_init,
    not_init,
    get,
    set,
    cprint,
    Colors,
)

from src.chat_history import (
    save_chat_history,
    load_convo,
    delete_this_chat,
)

from src.settings import (
    # settings_llm,
    settings_stt,
    settings_tts,
    settings_bottom_buttons,
    save_user_preferences,
)

from src.user_preferences import (
    load_settings,
)

from src.interface import centered_button_trick

from src.persist import load_persistance, update_persistance

from src.flows import ChatThread



from src.components.header import cmp_header, cmp_pills
from src.components.settings import cmp_construct_settings



class ChatAppVars:
    def __init__(self):
        self.chat = ChatThread()

        self.chat_history_depth = 20
        self.chat_history = None # the list of past conversations list of (description, runlog file name)
        # self.load_chat_history()


    def new_thread(self):
        self.chat = ChatThread()

    def increase_chat_history_depth(self):
        self.chat_history_depth += 20
        self.load_chat_history()

    def load_chat_history(self):
        # make sure the runlog directory exists
        dir = os.path.join(st.session_state.runlog_dir, get('construct').name)
        # os.makedirs(st.session_state.runlog_dir, exist_ok=True)
        os.makedirs(dir, exist_ok=True)

        self.chat_history = []
        runlogs = os.listdir(dir)
        runlogs.sort(reverse=True)
        self.truncated = len(runlogs) > self.chat_history_depth
        if self.truncated:
            runlogs = runlogs[:self.chat_history_depth]
        for runlog in runlogs:
            # continue if runlog is a directory
            if os.path.isdir(os.path.join(st.session_state.runlog_dir, runlog)):
                continue
            # Create directory if it doesn't exist
            # os.makedirs(os.path.join(st.session_state.runlog_dir, runlog), exist_ok=True)

            with open(os.path.join(dir, runlog), "r") as f:
                try:
                    file_contents = json.load(f)
                    description = file_contents["description"]
                except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                    # file load error or UnicodeDecodeError - skip this file
                    st.toast(f"Error loading {runlog}", icon="⚠️")
                    continue
            self.chat_history.append((description, runlog))




def cmp_chat():
    if not_init("construct"):
        return

    human_avatar = f"{AVATAR_PATH}/user0.png"
    ai_avatar = f"{AVATAR_PATH}/{get('construct').avatar_filename}"

    for message in get("chat").messages:
        with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
            st.markdown(message.content)


    my_next_prompt_placeholder = st.empty()

    prompt = st.chat_input("Ask a question.")

    if prompt:
        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)



def cmp_intro():
    if is_init("construct"):
        return

    st.markdown("## Welcome to :rainbow[PlebChat!]")
    # with centered_button_trick():
        # st.image(f"{ASSETS_PATH}/" + "assistant2sm.png")




def cmp_debug():
    # if os.getenv("DEBUG", False):

    with st.sidebar:
        # with st.popover("🔧 :red[Debug]"):
        with st.expander("debug", expanded=True):
            debug_placeholder = st.container()
            st.write(st.session_state)
            if is_init("construct"):
                debug_placeholder.write(get("construct"))
            debug_placeholder.write(st.session_state.appstate.chat.messages)





def main_page():
    cprint("\n\nRERUN!!!!!!\n", Colors.YELLOW)

    # load_persistance()
    # load_settings()

    if not_init('appstate'):
        st.session_state.appstate: ChatAppVars = ChatAppVars()

    appstate = st.session_state.appstate


    cmp_header()

    cmp_pills()
    st.header("", divider="rainbow")

    cmp_construct_settings()


    cmp_intro()
    cmp_chat()

    cmp_debug()