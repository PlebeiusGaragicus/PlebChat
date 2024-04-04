import os
import json

import streamlit as st

from src.common import get
from src.interface import center_text

from src.chat_history import (
    save_chat_history,
    load_convo,
    delete_this_chat,
)



def cmp_chat_history():
    # return

    with st.sidebar:
        st.header("", divider="rainbow")
        # st.write("## :rainbow[Past Conversations]")
        st.write("## :orange[Conversation History]")

        with st.container(border=True):
            st.button("Nothing yet", use_container_width=True)
            st.button("Something", use_container_width=True)
            st.button("Nope, nothing", use_container_width=True)

        return
        if len(st.session_state.thread.messages) > 0:
            sidebar_new_button_placeholder = st.columns((1, 1))
            sidebar_new_button_placeholder[0].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="delbutton2", use_container_width=True)
            sidebar_new_button_placeholder[1].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True, key="newbutton2")
            center_text('p', "---", size=9)
        # with st.expander("Past Conversations", expanded=False):
        if len(appstate.chat_history) == 0:
            st.caption("No past conversations... yet")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        if appstate.truncated:
            st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
            st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        st.header("", divider="rainbow")





class ChatAppVars:
    def __init__(self):
        self.chat_history_depth = 20
        self.chat_history = None # the list of past conversations list of (description, runlog file name)
        # self.load_chat_history()

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
