import os
import json
from datetime import datetime

import streamlit as st

from mistralai.models.chat_completion import ChatMessage
from mistralai.client import MistralClient

from src.settings import LLM_OPTIONS


def serialize_messages(msg: ChatMessage):
    s = {
            "role": msg.role,
            "content": msg.content
        }
    return s


def deserialize_messages(msg):
    d = ChatMessage(role=msg["role"], content=msg["content"])
    return d



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