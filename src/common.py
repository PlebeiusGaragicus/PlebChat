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
        # self.session_start_time = None
        self.session_start_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.description = None
        self.messages: list[ChatMessage] = []
        # self.not_yet_saved = True



class ChatAppVars:
    def __init__(self):
        self.username = st.session_state.username

        self.client = None
        self.chat_history_depth = 20

        # make sure the runlog directory exists
        self.runlog_dir = os.path.join(os.getcwd(), "runlog", self.username)
        os.makedirs(self.runlog_dir, exist_ok=True)

        # self.session_start_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        self.chat = ChatThread()
        self.chat_history = None
        self.load_chat_history()

        # SETTINGS
        self.debug = os.getenv("DEBUG", False)
        self.mistral_models = ['mistral-medium', 'mistral-small', 'mistral-tiny']


    def get_debug_generator(self):
        time.sleep(0.7)
        echo = st.session_state.appstate.chat.messages[-1].content

        # split the message into words
        echo = echo.split(" ")
        for e in echo:
            yield DeltaContentChunk(f" {e}")
            time.sleep(0.04)

    def get_client(self):
        if st.session_state.language_model == LLM_OPTIONS.ECHOBOT:
            return self.get_debug_generator()
        elif st.session_state.language_model == LLM_OPTIONS.MISTRAL_API:
            if st.session_state.mistral_api_key in [None, ""]:
                raise Exception("Mistral API key not set.")

            # if 'client' not in st.session_state.:
            #     st.session_state.client = MistralClient(api_key=self.api_key_mistral)
            if self.client is None:
                self.client = MistralClient(api_key=st.session_state.mistral_api_key) # TODO add error handling here

            return self.client.chat_stream(
                model=st.session_state.mistral_model,
                messages=self.chat.messages,
                safe_mode=st.session_state.mistral_safemode
            )
        elif st.session_state.language_model == LLM_OPTIONS.MISTRAL_LOCAL:
            st.error("Not yet implemented")
            st.stop()
        elif st.session_state.language_model == LLM_OPTIONS.GPT3_5:
            st.error("Not yet implemented")
            st.stop()
        else:
            st.error("Invalid language model")
            st.stop()

    def new_thread(self):
        self.chat = ChatThread()

    def increase_chat_history_depth(self):
        self.chat_history_depth += 20
        self.load_chat_history()

    def load_chat_history(self):
        self.chat_history = []
        runlogs = os.listdir(self.runlog_dir)
        runlogs.sort(reverse=True)
        self.truncated = len(runlogs) > self.chat_history_depth
        if self.truncated:
            runlogs = runlogs[:self.chat_history_depth]
        for runlog in runlogs:
            with open(os.path.join(self.runlog_dir, runlog), "r") as f:
                try:
                    file_contents = json.load(f)
                    description = file_contents["description"]
                except json.decoder.JSONDecodeError:
                    # file load error - skip this file
                    continue
            # st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
            self.chat_history.append((description, runlog))
        # if self.truncated:
        #     with st.sidebar:
        #         # st.caption("Only showing last 20 conversations")
        #         st.button("Show more")






class Content:
    def __init__(self, word_chunk):
        self.content = word_chunk

class Delta:
    def __init__(self, word_chunk):
        self.delta = Content(word_chunk)

class DeltaContentChunk:
    def __init__(self, word_chunk):
        self.choices = [
                Delta(word_chunk),
            ]
