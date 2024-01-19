import os
import base64
import time
import io
import yaml


import streamlit as st
import streamlit_authenticator as stauth

from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException
from openai import OpenAI

import logging
log = logging.getLogger(__file__)

print("\n\nLOADING AND RUNNING TOP-LEVEL CODE FOR EACH USER ACTION?!\n\n")


from src.VERSION import VERSION
from src.common import (
    ASSETS_PATH,
    ChatAppVars,
)

from src.chat_history import (
    save_chat_history,
    load_convo,
    delete_this_chat,
)

from src.settings import (
    settings_llm,
    settings_stt,
    settings_tts,
    settings_bottom_buttons,
    load_settings,
)

from src.interface import (
    column_fix,
    center_text,
    centered_button_trick,
    interrupt,
)

from src.tts import TTS


def home_page():
    st.set_page_config(
        page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="centered", # vs wide
        initial_sidebar_state="auto",
        # menu_items={"About": "https://plebby.me/"} # TODO
    )

    try:
        with open("./auth.yaml") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
        st.stop()

    st.session_state.authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    if st.session_state["authentication_status"] is None:
        # with centered_button_trick():
        #     st.image(os.path.join(ASSETS_PATH, "assistant2sm.png"))
        # center_text("p", "🗣️🤖💬", size=60) # or h1, whichever
        if 'appstate' in st.session_state:
            del st.session_state['appstate']
            st.error("Application state has been cleared!")

    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")

    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    st.session_state.authenticator.login("PlebChat login", "main")

    if st.session_state["authentication_status"]:
        init_if_needed()

        # from src.main_page import main_page
        main_page()



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
        # st.session_state["route"] = PageRoute.MAIN

        if 'speak_this' not in st.session_state:
            st.session_state.speak_this = None



def main_page():
    appstate = st.session_state.appstate

    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever

    load_settings()
    sidebar_new_button_placeholder = st.sidebar.empty()

    ### SETTINGS EXPANDER
    if st.session_state.user_preferences["settings_on_sidebar"]:
        settings_placeholder = st.sidebar.empty()
    else:
        settings_placeholder = st.empty()

    with settings_placeholder.expander("Settings",
                                       # expand the settings expander if the settings are on the sidebar
                                       expanded=st.session_state.user_preferences["settings_on_sidebar"]):
        with st.container(border=True):
            settings_llm()
        with st.container(border=True):
            settings_stt()
        with st.container(border=True):
            settings_tts()

        settings_bottom_buttons()

    ### INPUT BUTTONS
    top_buttons = st.columns((2, 1, 1))
    with top_buttons[0]:
        st.toggle("🗣️🤖", key="speech_input", value=False)
    with top_buttons[1]:
        st.toggle("🤖💬", key="read_to_me", value=False)

    ### DELETE BUTTON
    if len(appstate.chat.messages) > 0:
        with top_buttons[2]:
            st.button("🗑️ Delete", on_click=delete_this_chat, key="button_delete", use_container_width=True)

    ### RAINBOW DIVIDER
    st.header("", divider="rainbow")
    # st.caption(f"LLM: {st.session_state.user_preferences['language_model']}, STT: {st.session_state.user_preferences['stt']}, TTS: {st.session_state.user_preferences['tts']}")
    st.caption(f"Using: `{st.session_state.user_preferences['language_model']}`")



    ####### CONVERSATION #######
    for message in appstate.chat.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # This is so that we can later populate with the users' next prompt
    # and the bots reply and allows the input field (or start recording button)
    # to be at the bottom of the page
    my_next_prompt_placeholder = st.empty()
    interrupt_button_placeholder = st.empty()
    bots_reply_placeholder = st.empty()
    before_speech_placeholder = st.empty()

    if len(appstate.chat.messages) > 0:
        st.header("", divider="rainbow")


    #### USER PROMPT AND ASSOCIATED LOGIC
    prompt = None
    if 'speech_draft' not in st.session_state:
        st.session_state.speech_draft = None
        st.session_state.speech_confirmed = False

    if not st.session_state.get("speech_input", False):
        prompt = st.chat_input("Ask a question.")
    else:
        # TODO - naive thinking that let me to think having us import here would increase page performance... lol, oh well
        from streamlit_mic_recorder import speech_to_text
        # if not appstate.speech_confirmed:
        with centered_button_trick():
            # https://pypi.org/project/SpeechRecognition/
            speech_draft = speech_to_text(
                            start_prompt="🎤 Speak",
                            stop_prompt="🛑 Stop",
                            language='en',
                            use_container_width=True,
                            just_once=True,
                            key='STT'
                    )
        if st.session_state.confirm_stt is False:
        #     speech_draft = speech
        # else:
            prompt = speech_draft
            speech_draft = None

        if speech_draft:
            with st.container(border=True):
                def edit_draft(x):
                    # st.session_state.speech_draft_edit = x
                    st.session_state.speech_draft = x
                    # st.session_state.speech_confirmed = False
                    # st.session_state.speech_draft = speech_draft

                # st.text_input("You said:", value=speech_draft, key="speech_draft_edit", on_change=edit_draft)
                # st.text_input("You said:", value=speech_draft, key="speech_draft_edit")
                st.text_area("You said:", value=speech_draft, key="speech_draft_edit")

                def user_confirms_speech():
                    st.session_state.speech_confirmed = True
                    st.session_state.speech_draft = st.session_state.speech_draft_edit

                def user_cancels_speech():
                    st.session_state.speech_confirmed = False
                    st.session_state.speech_draft = None

                confirms = st.columns((2, 1, 1))
                confirms[0].button("✅", on_click=user_confirms_speech, use_container_width=True)
                confirms[2].button("❌", on_click=user_cancels_speech, use_container_width=True)

                # if st.button("Confirm"):
                #     st.session_state.speech_confirmed = True
                #     st.session_state.speech_draft = speech_draft



    if st.session_state.speech_confirmed:
        prompt = st.session_state.speech_draft
        st.session_state.speech_draft = None

    if prompt:
        st.session_state.speech_confirmed = False
        interrupt_button_placeholder.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt_placeholder.chat_message("user").markdown(prompt)
        reply = run_prompt(prompt, bots_reply_placeholder)

        new_chat = save_chat_history() # dummy variable for readability
        if new_chat:
            # A new chat thread has just been created, so we must update our list of past conversations
            appstate.load_chat_history()

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:
            st.session_state.speak_this = reply

        st.rerun() # we rerun the page for a reason that I forgot...
    #### AFTER-PROMPT PROCESSING ####
    # put things here to update the UI _AFTER_ the prompt has been run


    ### READ IT AND NEW BUTTONS
    with before_speech_placeholder:
        if len(appstate.chat.messages) > 0:
            # if last message was from the bot, then we can read it aloud
            col2 = st.columns((1, 1))
            col2[1].button("🌱 New", on_click=lambda: appstate.new_thread(), use_container_width=True)
            if appstate.chat.messages[-1].role == "assistant":
                # centered_button_trick().button("🗣️ Speak", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)
                if st.session_state.read_to_me is False:
                    def on_click_read_to_me():
                        st.session_state.speak_this = appstate.chat.messages[-1].content
                    col2[0].button("🗣️ read it", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)



    ### SIDEBAR WITH CONVERSATION HISTORY
    with st.sidebar:
        if len(appstate.chat.messages) > 0:
            # with centered_button_trick():
            sidebar_new_button_placeholder.button("🌱 New", on_click=lambda: appstate.new_thread(), use_container_width=True, key="newbutton2")
        st.write("## Past Conversations")
        # with st.container(border=True):
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        if appstate.truncated:
            st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
            st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        st.write("---")
        st.session_state.authenticator.logout(f"Logout `{st.session_state['username']}`", "main")
        st.caption(f"running version `{VERSION}`")
        if os.getenv("DEBUG", False) == False:
            st.caption("Running in production mode.")



    ### THE AUDIO PLAYER FOR TTS
    if st.session_state.speak_this is not None:
        # on reload, if `tts` is set, then we speak it
        TTS(st.session_state.speak_this)
        st.session_state.speak_this = None

    # st.caption(".") # I was trying to do this so that the page scrolls to the bottom... but I don't think it works.





def run_prompt(prompt, bots_reply_placeholder):
    st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )

    # With streaming
    with bots_reply_placeholder.chat_message("assistant"):
        st.session_state.incomplete_stream = ""
        place_holder = st.empty()

        try:
            with st.spinner("🧠 Thinking..."):
                try:
                    client = st.session_state.appstate.get_client()
                except Exception as e:
                    # TODO missing API keys will throw an exception here
                    # WE NEED TO AVOID THIS by limiting the options in the sidebar - don't let the user pick a model that won't work!
                    st.error(e)
                    st.stop()

                # for chunk in st.session_state.appstate.get_client():
                for chunk in client:
                    try:
                        st.session_state.incomplete_stream += chunk.choices[0].delta.content
                    except TypeError:
                        #TODO - not sure why this error happens...
                        # st.session_state.incomplete_stream += chunk.choices[0].message.content
                        print("TypeError in run_prompt()")
                        pass
                    place_holder.markdown(st.session_state.incomplete_stream)
        except MistralAPIException as e:
            st.error(e)
            st.stop()

        reply = st.session_state.incomplete_stream

    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))

    return reply
