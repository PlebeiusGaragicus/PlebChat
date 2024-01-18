import os
import time
import json
import yaml
import pathlib

import streamlit as st

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"
PREFERENCES_PATH = pathlib.Path(__file__).parent.parent / "preferences"

# OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
OPENAI_TTS_MODELS = ["echo", "nova", "onyx"]
TTS_VOICE_CHOICES = ["👱🏼‍♂️", "👱🏻‍♀️", "🧔🏻‍♂️"]

MISTRAL_MODELS = ['mistral-medium', 'mistral-small', 'mistral-tiny']

class LLM_OPTIONS:
    MISTRAL_API = "Mistral API"
    MISTRAL_LOCAL = "Mistral (local)"
    GPT3_5 = "GPT-3.5"
    ECHOBOT = "echobot" # Debug only

class STT_OPTIONS:
    PYTHON = "Python SpeechRecognition"
    ASSEMBLYAI = "AssemblyAI"

class TTS_OPTIONS:
    GOOGLE = "Google TTS"
    OPENAI = "OpenAI TTS"



COLUMN_FIX_CSS = """<style>
[data-testid="column"] {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>"""

def column_fix():
    st.write(COLUMN_FIX_CSS, unsafe_allow_html=True)


def center_text(type, text, size=None):
    if size == None:
        st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)
    else:
        st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)

# def center_text(type, text):
    # st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)



class PageRoute:
    MAIN = "main"
    SETTINGS = "settings"
    ABOUT = "about"


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

        # self.api_key_mistral = None
        # self.api_key_openai = None
        # self.api_key_assemblyai = None
        # self.get_api_keys()

        # self.client = MistralClient(self.api_key_mistral)
        self.client = None

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
    

    
    # def get_api_keys(self):
    #     with open("./auth.yaml") as file:
    #         config = yaml.load(file, Loader=yaml.loader.SafeLoader)

    #     # TODO find a better way?
    #     try:
    #         self.api_key_openai = config["credentials"]["usernames"][self.username]["api_key_openai"]
    #     except KeyError:
    #         self.api_key_openai = None

    #     try:
    #         self.api_key_mistral = config["credentials"]["usernames"][self.username]["api_key_mistral"]
    #     except KeyError:
    #         # This can't be none
    #         # self.api_key_mistral = None
    #         raise Exception("Mistral API key not found")

    #     try:
    #         self.api_key_assemblyai = config["credentials"]["usernames"][self.username]["api_key_assemblyai"]
    #     except KeyError:
    #         self.api_key_assemblyai = None

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
                self.client = MistralClient(api_key=self.st.session_state.mistral_api_key) # TODO add error handling here

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

    def load_chat_history(self):
        self.chat_history = []
        runlogs = os.listdir(self.runlog_dir)
        runlogs.sort(reverse=True)
        truncated = len(runlogs) > 40
        if truncated:
            runlogs = runlogs[:40]
        for runlog in runlogs:
            with open(os.path.join(self.runlog_dir, runlog), "r") as f:
                try:
                    file_contents = json.load(f)
                    description = file_contents["description"]
                except json.decoder.JSONDecodeError:
                    continue
                # except KeyError:
                    # description = "no description"
                    # TODO ##################################################################
                    # TODO ################################################################## fix the None
            # st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
            self.chat_history.append((description, runlog))
            # print(self.chat_history)
        if truncated:
            st.caption("Only showing last 40 conversations")











def load_convo(runlog):
    """ Load a previous conversation from a runlog file"""

    st.toast(f"Loading {runlog}...")

    # load the runlog file
    with open(os.path.join(st.session_state.appstate.runlog_dir, runlog), "r") as f:
        file_contents = json.load(f)

        messages = file_contents["messages"]
        st.session_state.appstate.chat.messages = [deserialize_messages(m) for m in messages]

        st.session_state.appstate.chat.session_start_time = file_contents["session_start_time"]
        st.session_state.appstate.chat.description = file_contents["description"]



def delete_this_chat():
    """ Delete the current chat history """

    runlog_file = os.path.join(st.session_state.appstate.runlog_dir, f'{st.session_state.appstate.chat.session_start_time}.txt')
    os.remove(runlog_file)

    st.session_state.appstate.new_thread()
    st.session_state.appstate.load_chat_history()



def get_description():
    # if st.session_state.mistral_api_key in [None, ""]:
    # if st.session_state.user_preferences["mistral_api_key"] in [None, ""]:
    if st.session_state.language_model == LLM_OPTIONS.ECHOBOT:
        # return "A friendly chat."
        content = st.session_state.appstate.chat.messages[0].content
        # return first 3 words, at most
        return " ".join(content.split(" ")[:3])

    # client = MistralClient(api_key=st.session_state.mistral_api_key)
    client = MistralClient(api_key=st.session_state.user_preferences["mistral_api_key"])
    messages = [
        ChatMessage(
            role="user",
            content=f"Reduce the following user query into 3 to 4 key words: `{st.session_state.appstate.chat.messages[0].content}`\nDo not answer questions. Your reply MUST be no more than 4 words!"
        )
    ]

    chat_response = client.chat(
        model="mistral-small",
        messages=messages,
    )
    # print(chat_response)
    # st.stop()
    return chat_response.choices[0].message.content



def save_chat_history() -> bool:
    """ Save the chat history to a file """

    new_chat_first_save = False

    # if st.session_state['description'] == None:
    if st.session_state.appstate.chat.description == None:
        new_chat_first_save = True
        desc = get_description()
        #ensure desc is no more than n words
        desc = " ".join(desc.split(" ")[:6]) # n=6
    else:
        desc = st.session_state.appstate.chat.description


    # serialize the messages
    messages = [serialize_messages(m) for m in st.session_state.appstate.chat.messages]

    # save the chat history to a file
    runlog_file = os.path.join(st.session_state.appstate.runlog_dir, f'{st.session_state.appstate.chat.session_start_time}.txt')
    with open(runlog_file, "w") as f:
        json.dump(
            {
                "description": desc,
                "session_start_time": st.session_state.appstate.chat.session_start_time,
                "messages": messages
            },
            f,
            indent=4
        )
    
    return new_chat_first_save




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



def serialize_messages(msg: ChatMessage):
    s = {
            "role": msg.role,
            "content": msg.content
        }
    return s


def deserialize_messages(msg):
    d = ChatMessage(role=msg["role"], content=msg["content"])
    return d



def init_if_needed():
    # initialize the appstate on first run
    if 'appstate' not in st.session_state:
        try:
            st.session_state['appstate']: ChatAppVars = ChatAppVars()
        except Exception as e:
            st.warning("No Mistral API key found.  Enter one in the settings page.")
            st.error(e)
            st.stop()
        
        ### SETUP STARTING ROUTE
        st.session_state["route"] = PageRoute.MAIN

        if 'speak_this' not in st.session_state:
            st.session_state.speak_this = None



def centered_button_trick():
    """ Use this in a `with` statement to center a button.
    
    Example:
    ```python
    with centered_button_trick():
        st.button(
            "👈 back",
            on_click=go_to_main_page,
            use_container_width=True)
    ```
    """
    columns = st.columns((1, 2, 1))
    with columns[0]:
        st.empty()
    # with columns[1]:
        # normally the button logic would go here
    with columns[2]:
        st.empty()

    return columns[1]