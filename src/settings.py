import os
import yaml
import pathlib

import streamlit as st

# from src.flows.abstract_model import (
#     Echobot,
#     MistralAPI,
#     MistralLocal,
#     OpenAIAPI,
# )

from src.user_preferences import save_user_preferences


# OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
OPENAI_TTS_MODELS = ["echo", "nova", "onyx"]
TTS_VOICE_CHOICES = ["👱🏼‍♂️", "👱🏻‍♀️", "🧔🏻‍♂️"]



# class LLM_OPTIONS:
#     MISTRAL_API = "Mistral API"
#     MISTRAL_LOCAL = "Mistral (local)"
#     OPENAI = "OpenAI"
#     ECHOBOT = "echobot" # Debug only

class STT_OPTIONS:
    PYTHON = "Python SpeechRecognition"
    ASSEMBLYAI = "AssemblyAI"

class TTS_OPTIONS:
    GOOGLE = "Google TTS"
    OPENAI = "OpenAI TTS"



# def settings_llm():
#     if os.getenv("DEBUG", False):
#         llm_options = [
#             LLM_OPTIONS.ECHOBOT,
#             LLM_OPTIONS.MISTRAL_LOCAL,
#             LLM_OPTIONS.MISTRAL_API,
#             LLM_OPTIONS.OPENAI,
#         ]
#     else:
#         llm_options = [
#             LLM_OPTIONS.ECHOBOT,
#             LLM_OPTIONS.MISTRAL_API,
#             LLM_OPTIONS.OPENAI,
#         ]

#     selected_llm_index = llm_options.index(st.session_state.user_preferences["language_model"])
#     st.selectbox("🧠 Language Model",
#                 options=llm_options,
#                 index=selected_llm_index,
#                 key="language_model",
#                 on_change=save_user_preferences,
#                 kwargs={"update_key": "language_model"},
#             )

#     # if st.session_state.user_preferences["language_model"] == LLM_OPTIONS.ECHOBOT:
#     #     st.caption("no settings for `echobot` - it just repeats what you say mainly for testing.")

#     if st.session_state.user_preferences["language_model"] == LLM_OPTIONS.OPENAI:
#         st.text_input(
#             "OpenAI API key",
#             key="openai_api_key",
#             value=st.session_state.user_preferences["openai_api_key"],
#             on_change=save_user_preferences,
#             kwargs={"update_key": "openai_api_key"},
#             disabled=(st.session_state.username == 'demo'),
#             type='password' if st.session_state.username == 'demo' else 'default'
#         )

#     # elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.MISTRAL_LOCAL:
#     #     st.caption("no settings for local `mistral` - good luck!")

#     # elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.LLAMA2_LOCAL:
#     #     st.caption("no settings for local `llama2` - good luck!")

#     elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.MISTRAL_API:
#         st.toggle(
#             "Safe mode",
#             key="mistral_safemode",
#             value=st.session_state.user_preferences["mistral_safemode"],
#             on_change=save_user_preferences,
#             kwargs={"toggle_key": "mistral_safemode"},
#             help="Safe mode is not yet implemented by mistral ai.  It also turns mistral into a little bitch... you don't want that, do you?",
#             disabled=True
#         )

#         from src.flows.abstract_model import MistralAPI
#         # MISTRAL_MODELS = ['mistral-medium', 'mistral-small', 'mistral-tiny']

#         st.radio("Mistral model select",
#             key="mistral_model",
#             options=MistralAPI.MISTRAL_MODELS,
#             index=MistralAPI.MISTRAL_MODELS.index(st.session_state.user_preferences["mistral_model"]),
#             on_change=save_user_preferences,
#             kwargs={"update_key": "mistral_model"},
#         )

#         st.text_input(
#             "Mistral API key",
#             key="mistral_api_key",
#             value=st.session_state.user_preferences["mistral_api_key"],
#             on_change=save_user_preferences,
#             kwargs={"update_key": "mistral_api_key"},
#             disabled=(st.session_state.username == 'demo'),
#             type='password' if st.session_state.username == 'demo' else 'default'
#         )
    


def settings_stt():
    # with st.container(border=True):
    # stt_options = [STT_OPTIONS.PYTHON, STT_OPTIONS.ASSEMBLYAI]
    stt_options = [STT_OPTIONS.PYTHON]
    selected_stt = stt_options.index(st.session_state.user_preferences["stt"])
    st.selectbox(
            label="🗣️🤖 Voice transcription",
            options=stt_options,
            index=selected_stt,
            key="stt",
            on_change=save_user_preferences,
            kwargs={"update_key": "stt"},
        )
    
    # if st.session_state.get("stt") == STT_OPTIONS.PYTHON:
        # st.caption("No settings for `python` - it's free and it works")
    
    if st.session_state.get("stt") == STT_OPTIONS.ASSEMBLYAI:
        st.text_input(
            "AssemblyAI API key",
            key="assemblyai_api_key",
            value=st.session_state.user_preferences["assemblyai_api_key"],
            on_change=save_user_preferences,
            kwargs={"update_key": "assemblyai_api_key"},
            disabled=(st.session_state.username == 'demo'),
            type='password' if st.session_state.username == 'demo' else 'default'
        )
    
    #NOTE: This has to be high in the flow as it is used for speech generation
    # confirm_stt = st.session_state.user_preferences["confirm_stt"]
    # st.toggle(
    #     label="Confirm stt",
    #     key="confirm_stt",
    #     value=confirm_stt,
    #     on_change=save_user_preferences,
    #     kwargs={"toggle_key": "confirm_stt"},
    # )


def settings_tts():
    # with st.container(border=True):
    # tts_options = [TTS_OPTIONS.GOOGLE, TTS_OPTIONS.OPENAI]
    tts_options = [TTS_OPTIONS.GOOGLE]
    selected_tts = tts_options.index(st.session_state.user_preferences["tts"])
    st.selectbox(
        label="🤖💬 Text to speech",
        options=tts_options,
        index=selected_tts,
        key="tts",
        on_change=save_user_preferences,
        kwargs={"update_key": "tts"},
    )


    # if st.session_state.get("tts") == "Google TTS":
    #     st.caption("No settings for `gTTS` - it's free and it works")

    if st.session_state.get("tts") == "OpenAI TTS":
        cols = st.columns((1, 1))
        cols[0].radio(
            "Voice model",
            options=TTS_VOICE_CHOICES,
            index=TTS_VOICE_CHOICES.index(st.session_state.user_preferences['openai_voice']),
            on_change=save_user_preferences,
            kwargs={"update_key": "openai_voice"},
            key="openai_voice")

        talking_speed_options = [1.0, 1.2, 1.5]
        cols[1].radio(
            "Talking speed",
            options=talking_speed_options,
            index=talking_speed_options.index(st.session_state.user_preferences['openai_tts_rate']),
            on_change=save_user_preferences,
            kwargs={"update_key": "openai_tts_rate"},
            key="openai_tts_rate")
    
        # TODO - need a better solution for this!  Need a central place to store the api keys!
        if 'openai_api_key' not in st.session_state:
            st.text_input(
                "OpenAI API key",
                key="openai_api_key",
                value=st.session_state.user_preferences["openai_api_key"],
                on_change=save_user_preferences,
                kwargs={"update_key": "openai_api_key"},
                disabled=(st.session_state.username == 'demo'),
                type='password' if st.session_state.username == 'demo' else 'default'
            )


def settings_bottom_buttons():
    col2 = st.columns((1, 1))
    ### LOGOUT BUTTON
    with col2[0]:
        confirm_stt = st.session_state.user_preferences["confirm_stt"]
        st.toggle(
            label="Confirm stt",
            key="confirm_stt",
            value=confirm_stt,
            on_change=save_user_preferences,
            kwargs={"toggle_key": "confirm_stt"},
        )

    ### SWITCH SETTINGS LOCATION BUTTON
    # with col2[1]:
    #     move_button_text = f"Move to {'main' if st.session_state.user_preferences['settings_on_sidebar'] else 'sidebar'}"
    #     st.button(move_button_text,
    #                 on_click=save_user_preferences,
    #                 kwargs={"toggle_key": "settings_on_sidebar"},
    #                 key="button_move_to_main",
    #                 use_container_width=True)


# def init_model():
#     if 'model' in st.session_state:
#         return

#     if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.ECHOBOT:
#         st.session_state.model = Echobot()

#     if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.MISTRAL_API:
#         st.session_state.model = MistralAPI()

#     if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.MISTRAL_LOCAL:
#         st.session_state.model = MistralLocal()

#     if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.OPENAI:
#         st.session_state.model = OpenAIAPI()
