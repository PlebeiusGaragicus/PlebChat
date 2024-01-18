import os
import base64
import time
import io
import yaml

import streamlit as st

from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException
from openai import OpenAI


import logging
log = logging.getLogger(__file__)

from src.VERSION import VERSION
from src.common import (
    save_chat_history,
    load_convo,
    delete_this_chat,
    center_text,
    centered_button_trick,
    column_fix,
)

from src.settings import (
    settings_llm,
    settings_stt,
    settings_tts,
    settings_bottom_buttons,
    load_settings,
    OPENAI_TTS_MODELS,
    TTS_VOICE_CHOICES,
)


from src.interface import (
    autoplay_audio,
    interrupt,
)


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
    my_next_prompt = st.empty()
    interrupt_button = st.empty()
    bots_reply = st.empty()
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

        if speech_draft:
            with st.container(border=True):
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
        interrupt_button.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt.chat_message("user").markdown(prompt)
        reply = run_prompt(prompt, bots_reply)

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
                    speed=st.session_state.openai_tts_rate
                )
            # stub.empty()

            # Extract audio data from the response
            audio_data = speech.content

            # Convert audio data to Base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            autoplay_audio(audio_base64)
