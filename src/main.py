import os
import json
import random
import math

import streamlit as st
from streamlit_pills import pills

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

from src.interface import (
    column_fix,
    center_text,
    centered_button_trick,
)

# from DEPRECATED.sats import (
#     load_sats_balance,
#     TOKENS_PER_SAT,
#     display_invoice_pane
# )

from src.speech import TTS

from src.persist import load_persistance, update_persistance

from src.flows import ChatThread



# TODO
# CONSTRUCTS = ["echobot", "tommybot", "dummybot", "tavily"]
from src.flows.constructs import ALL_CONSTRUCTS




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

















def the_rest():
    ### info card
    with st.expander("Information about this AI workflow", expanded=False):
        # if construct:
        get('construct').display_model_card()

    st.header("", divider="rainbow")



    if os.getenv("DEBUG", False):
        # with st.expander(":red[Debug] ❤️‍🩹", expanded=False):
        with st.popover("🔧 :red[Debug]"):
            debug_placeholder = st.container()
            # if construct:
            debug_placeholder.write(get("construct"))
            debug_placeholder.write(st.session_state.appstate.chat.messages)




    human_avatar = f"{AVATAR_PATH}/user0.png"
    ai_avatar = f"{AVATAR_PATH}/{get('construct').avatar_filename}"

    for message in get("chat").messages:
        with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
            st.markdown(message.content)


    my_next_prompt_placeholder = st.empty()

    prompt = st.chat_input("Ask a question.")

    if prompt:
        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)














def main_page():
    # print("\n\n\nRERUN!!!!!!\n")
    cprint("\n\nRERUN!!!!!!\n", Colors.YELLOW)

    load_persistance()
    load_settings()

    if not_init('appstate'):
        st.session_state.appstate: ChatAppVars = ChatAppVars()

    appstate = st.session_state.appstate



    ################### TOP OF MAIN CHAT ###################
    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever

    pills("always here", ["always", "here"])

    # return

    construct_names = [c.name for c in ALL_CONSTRUCTS]
    construct_icons = [c.emoji for c in ALL_CONSTRUCTS]
    # pill_index = get("persistance")['chosen_pill']
    # if we play around in debug and switch to production, we need to make sure we don't go out of bounds

    construct = pills(label="Choose an AI workflow:",
                    options=construct_names,
                    icons=construct_icons,
                    # clearable=True,
                    # index=None,
                    key="selected_construct"
                )


    st.caption(f"Construct: {construct}")

    if get("selected_construct"):


    # if construct:
        st.caption(f"Construct: {construct}")

    # if construct:
        # load_proper_flow(construct)


        the_rest()


