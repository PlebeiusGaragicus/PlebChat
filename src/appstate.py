import os
import json

from mistralai.models.chat_completion import ChatMessage

# import tiktoken
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.function import FunctionMessage

from src.flows import ChatThread

import streamlit as st

from src.common import get


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
