import os
import time
import json
import pathlib

import streamlit as st

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.settings import LLM_OPTIONS

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"


class ChatThread:
    def __init__(self):
        self.session_start_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.description = None
        self.messages: list[ChatMessage] = []



class ChatAppVars:
    def __init__(self):
        self.chat = ChatThread()

        self.chat_history_depth = 20
        self.chat_history = None # the list of past conversations list of (description, runlog file name)
        self.load_chat_history()


    def new_thread(self):
        self.chat = ChatThread()

    def increase_chat_history_depth(self):
        self.chat_history_depth += 20
        self.load_chat_history()

    def load_chat_history(self):
        # make sure the runlog directory exists
        os.makedirs(st.session_state.runlog_dir, exist_ok=True)

        self.chat_history = []
        runlogs = os.listdir(st.session_state.runlog_dir)
        runlogs.sort(reverse=True)
        self.truncated = len(runlogs) > self.chat_history_depth
        if self.truncated:
            runlogs = runlogs[:self.chat_history_depth]
        for runlog in runlogs:
            with open(os.path.join(st.session_state.runlog_dir, runlog), "r") as f:
                try:
                    file_contents = json.load(f)
                    description = file_contents["description"]
                except json.decoder.JSONDecodeError:
                    # file load error - skip this file
                    continue
            self.chat_history.append((description, runlog))
