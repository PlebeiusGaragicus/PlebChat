import os
import time
import json
import base64
import io

import streamlit as st
# from streamlit_mic_recorder import speech_to_text

# from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException

from openai import OpenAI

import logging
log = logging.getLogger(__file__)

from src.common import (
    ChatAppVars,
    OPENAI_TTS_MODELS,
    TTS_VOICE_CHOICES,
    save_chat_history,
    load_convo,
    delete_this_chat,
    COLUMN_FIX_CSS,
    PageRoute,
    center_text,
    centered_button_trick,
)

print("\n\nLOADING AND RUNNING TOP-LEVEL CODE FOR EACH USER ACTION?!\n\n")


def main_page(appstate: ChatAppVars):

    ###### HEADER ######
    st.write("""<p style="text-align: center; font-size: 60px;">🗣️🤖💬</p>""", unsafe_allow_html=True)
    st.header("", divider="rainbow")

    if st.session_state.get("echobot", False):
        st.caption("echobot mode")

    if appstate.debug:
        debugging_placeholder = st.empty()

    # with debugging_placeholder:
    #     with st.expander("# Debugging"):
    #         st.write(appstate)
    #         # st.write(appstate.chat.messages)
    #         st.write(appstate.chat)
    #         # st.write("chat_history:", appstate.chat_history)

    with st.sidebar:
        # vanishing_sidebar = st.container(border=True)
        # settings_sidebar = st.container(border=False)
        settings_sidebar = st.empty()

    # settings_sidebar.caption(";)")
    # settings_sidebar.empty()
    sidebar(appstate, settings_sidebar)

    ###### TOP BUTTONS ######
    st.write(COLUMN_FIX_CSS, unsafe_allow_html=True)

    top_buttons = st.columns((2, 1))
    with top_buttons[0]:
        st.empty()

    ####### CONVERSATION #######
    for message in appstate.chat.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # This is so that we can later populate with the users' next prompt and the bots reply and allows the input field (or start recording button) to be at the bottom of the page
    my_next_prompt = st.empty()
    interrupt_button = st.empty()
    bots_reply = st.empty()
    # read_to_me_button = st.empty()


    #### USER PROMPT AND ASSOCIATED LOGIC
    prompt = None

    if "Text" in st.session_state["input_method"]:
        # if prompt := st.chat_input("Ask a question."):
        prompt = st.chat_input("Ask a question.")
    else:
        # TODO - naive thinking that let me to think having us import here would increase page performance... lol, oh well
        from streamlit_mic_recorder import speech_to_text
        prompt = speech_to_text( language='en', use_container_width=True, just_once=True, key='STT')

    # st.toggle("🔊", key="toggle_sound")
    if prompt:
        settings_sidebar.empty()

        # with st.sidebar:
            #  st.markdown("`Settings disabled during interence`")
        interrupt_button.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt.chat_message("user").markdown(prompt)
        reply = run_prompt(prompt, bots_reply)

        new_chat = save_chat_history() # dummy variable for readability
        if new_chat:
            # A new chat thread has just been created, so we must update our list of past conversations
            appstate.load_chat_history()

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:
            st.session_state.tts = reply

        st.rerun()
        # sidebar(appstate, settings_sidebar) # this will cause a KeyError because of dupicate key widget keys

    if 'tts' not in st.session_state:
        st.session_state.tts = None

    # if st.session_state.tts is not None:
    #     TTS(st.session_state.tts)
    #     st.session_state.tts = None
        # TTS(reply) # may throw an exception

    #### AFTER-PROMPT PROCESSING ####
    # put things here to update the UI _AFTER_ the prompt has been run

    def on_click_read_to_me():
        st.session_state.tts = appstate.chat.messages[-1].content
        # st.rerun()

    if len(appstate.chat.messages) > 0:
        # if last message was from the bot, then we can read it aloud
        if appstate.chat.messages[-1].role == "assistant" and st.session_state.tts is None:
            # with centered_button_trick():
                # read_to_me_button.button("Read this 🗣️👂", on_click=on_click_read_to_me, key="button_read_to_me")
            centered_button_trick().button("🗣️ Speak", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)

        with top_buttons[0]:
            st.button("🌱 New chat", on_click=lambda: appstate.new_thread(), use_container_width=True)
        with top_buttons[1]:
            st.button("🗑️ Delete", on_click=delete_this_chat, key="button_delete")

    if st.session_state.tts is not None:
        TTS(st.session_state.tts)
        st.session_state.tts = None


    with st.sidebar:
        with st.expander("Past conversations", expanded=False):
            for description, runlog in appstate.chat_history:
                st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])

        st.write("---")
        st.button(f"⚙️ Configure", on_click=settings, use_container_width=True)
        st.caption(f"Logged in as: `{st.session_state.appstate.username}`")


    if appstate.debug:
        with debugging_placeholder:
            with st.expander("# Debugging"):
                st.write(appstate)
                st.write(appstate.chat)
                # st.write(appstate.chat.messages)


    ### outside of the if prompt block


def settings():
    # st.toast("Settings not yet implemented", icon="🚧")
    st.session_state.route = PageRoute.SETTINGS


def sidebar(appstate, settings_sidebar):
    #Note: we do this at the end so that a new chat history will be displayed after the users first message
    
    # with st.sidebar:
    # with settings_sidebar:
    with settings_sidebar.container(border=True):
        if appstate.debug:
            # st.checkbox("Echobot", key="echobot", value=appstate.debug)
            st.toggle("Echobot", key="echobot", value=appstate.debug)

        st.radio("Input method:", ["Text ⌨️", "Voice 🗣️"], index=0, key="input_method")
        if appstate.api_key_openai in [None, ""]:
            st.info("Enter OpenAI key in settings to enable text-to-speech")
        else:
            st.toggle("Read aloud 👂", key="read_to_me", value=False, on_change=None) #on_change must be None or else a re-run of last prompt happens

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:

            st.toggle("gTTS", key="gtts", value=True)

            if not st.session_state.get("gtts", False):
                cols = st.columns((1, 1))
                cols[0].radio("Voice model", TTS_VOICE_CHOICES, index=1, key="openai_voice")
                cols[1].radio("Talking speed", [1.0, 1.2, 1.5], index=1, key="tts_rate")
        st.write("---")
        st.toggle("Safe mode", key="mistrel_safemode", value=False, help="Safe mode is not yet implemented by mistral ai", disabled=True)
        st.radio("Model",
                appstate.mistral_models,
                index=2 if appstate.debug else 0,
                key="mistrel_model")

        # vanishing_sidebar = st.empty()
    # return vanishing_sidebar


def run_prompt(prompt, bots_reply):
    st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )

    # With streaming
    with bots_reply.chat_message("assistant"):
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


# def autoplay_audio(file_path: str):
def autoplay_audio(audio_base64: str):
    """ https://discuss.streamlit.io/t/how-to-play-an-audio-file-automatically-generated-using-text-to-speech-in-streamlit/33201 """

    md = f"""
        <audio controls autoplay="True">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
    
    with centered_button_trick():
        st.markdown(md, unsafe_allow_html=True)


# NOTE: you need to adjust the website setting in safari to allow auto play media
def TTS(text, language='en', slow=False):
    #TODO if we persist the client, we may save some time here

    with st.spinner("💬 Generating speech..."):
        # if os.getenv("DEBUG", False):
        if st.session_state.get("gtts", True):
            # Create a gTTS object
            # TODO - attempting to do delayed imports for speed (not sure if this works)
            try:
                from gtts import gTTS, gTTSError
                tts = gTTS(text=text, lang=language, slow=slow)

                # Create a BytesIO object
                with io.BytesIO() as file_stream:
                    # Write the speech data to the file stream
                    tts.write_to_fp(file_stream)

                    # Move to the beginning of the file stream
                    file_stream.seek(0)

                    # Read the audio data and encode it in base64
                    audio_base64 = base64.b64encode(file_stream.read()).decode('utf-8')
                autoplay_audio(audio_base64)
            except gTTSError as e:
                st.error(e)
                st.error(f"Could not create audio: ")

        else:
            # if "openai_client" not in st.session_state:
            #     st.session_state.openai_client = 
            openai_client = OpenAI(api_key=st.session_state.appstate.api_key_openai)


            voice = st.session_state.openai_voice
            # OPENAI_TTS_MODELS = ["echo", "onyx", "nova"]
            if voice == TTS_VOICE_CHOICES[0]:
                tts_model = OPENAI_TTS_MODELS[0]
            elif voice == TTS_VOICE_CHOICES[1]:
                tts_model = OPENAI_TTS_MODELS[1]
            else:
                tts_model = OPENAI_TTS_MODELS[2]

            # speech = st.session_state.openai_client.audio.speech.create(
            speech = openai_client.audio.speech.create(
                    model="tts-1",
                    voice=tts_model,
                    # response_format="opus",
                    response_format="mp3",
                    input=f"{text}",
                    speed=st.session_state.tts_rate
                )
            # stub.empty()

            # Extract audio data from the response
            audio_data = speech.content

            # Convert audio data to Base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            autoplay_audio(audio_base64)


def interrupt():
    # st.session_state.interrupt = True
    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
    st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))
    # save_chat_history()
    # st.session_state.appstate.load_chat_history()

    if save_chat_history():
        st.session_state.appstate.load_chat_history()

    # st.rerun() # not allowed in on_click handlers (callbacks)
