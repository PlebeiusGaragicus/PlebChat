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
    delete_this_chat
)

print("\n\nLOADING AND RUNNING TOP-LEVEL CODE FOR EACH USER ACTION?!\n\n")


def center_text(type, text, size):
    st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)

def center_text(type, text):
    st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)


def main_page():
    # initialize the appstate on first run
    if 'appstate' not in st.session_state:
        try:
            st.session_state['appstate']: ChatAppVars = ChatAppVars()
        except Exception as e:
            st.warning("No Mistral API key found.  Enter one in the settings page.")
            st.error(e)
            st.stop()

    appstate = st.session_state.appstate

    ###### HEADER ######
    st.write("""<p style="text-align: center; font-size: 60px;">🗣️🤖💬</p>""", unsafe_allow_html=True)
    if appstate.debug:
        st.caption(f"session: {appstate.chat.session_start_time}")
        with st.expander("# Debugging"):
            st.text_input("mistral API key", appstate.api_key_mistral, key="api_key_mistral", disabled=True)
            st.text_input("OpenAI API key", appstate.api_key_openai, key="api_key_openai", disabled=True)
            st.write(f"Description: `{appstate.chat.description}`")
            st.write(appstate.chat.messages)
    st.write("---")

    sidebar(appstate)

    # sidecol = st.columns((1, 1))
    # with sidecol[0]:
    #     st.button("New chat +", on_click=lambda: appstate.new_thread())
    # with sidecol[1]:
    #     if appstate.chat.messages != []:
    #         st.button("Delete 🗑️", on_click=delete_this_chat)
    newbutton, deletebutton, emptyspace = st.columns((1, 1, 4))
    newbutton.button("New chat +", on_click=lambda: appstate.new_thread())
    # if appstate.chat.messages != []:
    # if len(appstate.chat.messages) > 0:
    #     deletebutton.button("Delete 🗑️", on_click=delete_this_chat)

    ####### CONVERSATION #######
    for message in appstate.chat.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # This is so that we can later populate with the users' next prompt and the bots reply and allows the input field (or start recording button) to be at the bottom of the page
    my_next_prompt = st.empty()
    bots_reply = st.empty()


    #### USER PROMPT AND ASSOCIATED LOGIC
    # if 'input_method' not in st.session_state or "Text" in st.session_state["input_method"]:
    prompt = None

    if "Text" in st.session_state["input_method"]:
        # if prompt := st.chat_input("Ask a question."):
        prompt = st.chat_input("Ask a question.")
    else:
        # if prompt := speech_to_text( language='en', use_container_width=True, just_once=False, key='STT'):
        # with st.spinner("Loading speech-to-text..."):
        # TODO - naive thinking that let me to think having us import here would increase page performance... lol, oh well
        from streamlit_mic_recorder import speech_to_text
        prompt = speech_to_text( language='en', use_container_width=True, just_once=True, key='STT')

    if prompt:
        my_next_prompt.chat_message("user").markdown(prompt)
        run_prompt(prompt, bots_reply)
        save_chat_history()

    if appstate.chat.not_yet_saved:
        # A new chat thread has just been created, so we must update our list of past conversations
        appstate.load_chat_history()

    with st.sidebar:
        # with st.expander("# Past conversations", expanded=True):
        st.write("---")
        center_text("h3", "Past conversations")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])

    if len(appstate.chat.messages) > 0:
        deletebutton.button("Delete 🗑️", on_click=delete_this_chat)

    with st.sidebar:
        st.write("---")
        # st.button(f"{st.session_state.authenticator.username}", on_click=None)
        st.button(f"Profile Settings ⚙️", on_click=settings, use_container_width=True)
    # st.session_state.authenticator.logout("Logout", "sidebar")

    ####### SIDEBAR #######
    # sidebar(appstate)


    ### outside of the if prompt block


def settings():
    st.toast("Settings not yet implemented", icon="🚧")



def sidebar(appstate):
    #Note: we do this at the end so that a new chat history will be displayed after the users first message
    with st.sidebar:
        # TODO ########################################################################################################################
        # TODO ########################################################################################################################
        # sidecol = st.columns((1, 1))
        # with sidecol[0]:
        #     st.button("New chat +", on_click=lambda: appstate.new_thread())
        # with sidecol[1]:
        #     if appstate.chat.messages != []:
        #         st.button("Delete 🗑️", on_click=delete_this_chat)

        # display a list of past runlogs
        # past_convos = st.empty()
        # with past_convos.expander("# Past conversations"):
        # with st.expander("# Past conversations"):
            # # TODO - wish I could only run this code if the expander is open... would save compute.
            # runlogs = os.listdir(appstate.runlog_dir)
            # runlogs.sort(reverse=True)
            # truncated = len(runlogs) > 40
            # if truncated:
            #     runlogs = runlogs[:40]
            # for runlog in runlogs:
            #     with open(os.path.join(appstate.runlog_dir, runlog), "r") as f:
            #         try:
            #             file_contents = json.load(f)
            #             description = file_contents["description"]
            #         except json.decoder.JSONDecodeError:
            #             continue
            #         # except KeyError:
            #             # description = "no description"
            #             # TODO ##################################################################
            #             # TODO ################################################################## fix the None
            #     st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
            # if truncated:
            #     st.caption("Only showing last 40 conversations")
            # for description, runlog in appstate.chat_history:
            #     print(runlog, description)
            #     # st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
            #     # add an element to the past_convos object
            #     st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])


        # st.write("---")
        # st.write("# Settings")
        # center_text("h3", "Settings")


        # st.radio("", ["Text ⌨️", "Voice 🗣️"], index=0, key="input_method")
        st.radio("Input method:", ["Text ⌨️", "Voice 🗣️"], index=0, key="input_method")
        if appstate.api_key_openai in [None, ""]:
            st.info("Enter OpenAI key in settings to enable text-to-speech")
        else:
            st.checkbox("Read aloud 👂", key="read_to_me", value=False, on_change=None) #on_change must be None or else a re-run of last prompt happens

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:

            cols = st.columns((1, 1))
            cols[0].radio("Voice model", TTS_VOICE_CHOICES, index=1, key="openai_voice")
            cols[1].radio("Talking speed", [1.0, 1.2, 1.5], index=1, key="tts_rate")
        st.write("---")
        st.radio("Model",
                 appstate.mistral_models,
                 index=0 if os.getenv("DEBUG", False) else 2,
                 key="mistrel_model")
        st.checkbox("Safe mode", key="mistrel_safemode", value=False, help="Safe mode is not yet implemented by mistral ai", disabled=True)

        # if appstate.debug:
        #     st.write("---")
        #     with st.expander("# Debugging", expanded=True):
        #         st.text_input("mistral API key", appstate.api_key_mistral, key="api_key_mistral", disabled=True)
        #         st.text_input("OpenAI API key", appstate.api_key_openai, key="api_key_openai", disabled=True)
        #         st.write(f"Description: `{appstate.chat.description}`")
        #         st.write(appstate.chat.messages)



def run_prompt(prompt, bots_reply):
    st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )

    # With streaming
    with bots_reply.chat_message("assistant"):
        incomplete_stream = ""
        place_holder = st.empty()

        try:
            with st.spinner("🧠 Thinking..."):
                client = st.session_state.appstate.get_client()
                # for chunk in st.session_state.appstate.get_client():
                for chunk in client:
                    try:
                        incomplete_stream += chunk.choices[0].delta.content
                    except TypeError:
                        #TODO - not sure why this error happens...
                        # st.session_state.incomplete_stream += chunk.choices[0].message.content
                        print("TypeError in run_prompt()")
                        pass
                    place_holder.markdown(incomplete_stream)
        except MistralAPIException as e:
            st.error(e)
            st.stop()

        reply = incomplete_stream

    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))

    # TODO ########################################################################################################################
    # TODO ########################################################################################################################
    # TODO ########################################################################################################################
    # save the chat history to a file
    # save_chat_history()

    # if st.session_state.output_method == "Voice":
    if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:
        # try:
        TTS(reply)
        # except gTTSError as e:
        #     st.error(e)
        #     st.stop()
    
    # st.info("Done! 🎉")






# def autoplay_audio(file_path: str):
def autoplay_audio(audio_base64: str):
    """ https://discuss.streamlit.io/t/how-to-play-an-audio-file-automatically-generated-using-text-to-speech-in-streamlit/33201 """

    md = f"""
        <audio controls autoplay="True">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )


# NOTE: you need to adjust the website setting in safari to allow auto play media
def TTS(text, language='en', slow=False):
    #TODO if we persist the client, we may save some time here

    with st.spinner("💬 Generating speech..."):
        if os.getenv("DEBUG", False):
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
                # st.stop()


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
