import os
import yaml
import pathlib

import streamlit as st

from src.abstract_model import (
    Echobot,
    UppercaseBot,
    MistralAPI,
    MistralLocal,
    Llama2Local,
    OpenAIAPI
)


PREFERENCES_PATH = pathlib.Path(__file__).parent.parent / "preferences"

# OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
OPENAI_TTS_MODELS = ["echo", "nova", "onyx"]
TTS_VOICE_CHOICES = ["👱🏼‍♂️", "👱🏻‍♀️", "🧔🏻‍♂️"]

MISTRAL_MODELS = ['mistral-medium', 'mistral-small', 'mistral-tiny']

class LLM_OPTIONS:
    MISTRAL_API = "Mistral API"
    MISTRAL_LOCAL = "Mistral (local)"
    LLAMA2_LOCAL = "Llama2 (local)"
    OPENAI = "OpenAI"
    ECHOBOT = "echobot" # Debug only
    UPPERCASEBOT = "uppercasebot" # Debug only

class STT_OPTIONS:
    PYTHON = "Python SpeechRecognition"
    ASSEMBLYAI = "AssemblyAI"

class TTS_OPTIONS:
    GOOGLE = "Google TTS"
    OPENAI = "OpenAI TTS"




# Define default user preferences
DEFAULT_USER_PREFERENCES = {
    "assemblyai_api_key": None,
    "language_model": LLM_OPTIONS.MISTRAL_API,
    "mistral_api_key": None,
    "mistral_model": "mistral-medium",
    "mistral_safemode": True,
    "openai_api_key": None,
    "openai_tts_rate": 1.2,
    "openai_voice": TTS_VOICE_CHOICES[0],
    "settings_on_sidebar": False,
    "stt": STT_OPTIONS.PYTHON,
    "tts": TTS_OPTIONS.GOOGLE,
}


def load_settings():
    appstate = st.session_state

    if 'user_preferences' not in st.session_state:
        try:
            preferences_file = PREFERENCES_PATH / f"{appstate.username}.yaml"
            appstate.user_preferences = yaml.load(open(preferences_file), Loader=yaml.loader.SafeLoader)
        except FileNotFoundError:
            appstate.user_preferences = DEFAULT_USER_PREFERENCES  # Use default preferences
            st.error("user preferences yaml file not found. Creating a new one with default settings.")
            with open(preferences_file, "w") as f:
                yaml.dump(appstate.user_preferences, f)


def load_user_preferences(username):
    preferences_file = PREFERENCES_PATH / f"{username}.yaml"
    try:
        with open(preferences_file) as f:
            return yaml.load(f, Loader=yaml.loader.SafeLoader)
    except FileNotFoundError:

        return DEFAULT_USER_PREFERENCES


def save_user_preferences(update_key=None, toggle_key=None):
    print(f"save_user_preferences({update_key}, {toggle_key})")

    if update_key is None and toggle_key is None:
        raise ValueError("Either key_to_save or toggle_key must be set")


    if toggle_key is not None:
        st.session_state.user_preferences[toggle_key] = False if st.session_state.user_preferences[toggle_key] is True else True
        

    if update_key is not None:
        st.session_state.user_preferences[update_key] = st.session_state[update_key]

    preferences_file = PREFERENCES_PATH / f"{st.session_state.username}.yaml"
    with open(preferences_file, "w") as f:
        yaml.dump(st.session_state.user_preferences, f)

    del st.session_state.user_preferences
    st.toast("User preferences saved!")

    # we need to ensure we destory the old client so a new one with the new settings is init'd
    if 'model' in st.session_state:
        del st.session_state.model



def settings_llm():
    if os.getenv("DEBUG", False):
        llm_options = [
            LLM_OPTIONS.ECHOBOT,
            LLM_OPTIONS.UPPERCASEBOT,
            LLM_OPTIONS.MISTRAL_LOCAL,
            LLM_OPTIONS.LLAMA2_LOCAL,
            LLM_OPTIONS.MISTRAL_API,
            LLM_OPTIONS.OPENAI,
        ]
    else:
        llm_options = [
            LLM_OPTIONS.ECHOBOT,
            LLM_OPTIONS.MISTRAL_API,
            LLM_OPTIONS.OPENAI,
        ]

    selected_llm_index = llm_options.index(st.session_state.user_preferences["language_model"])
    st.selectbox("🧠 Language Model",
                options=llm_options,
                index=selected_llm_index,
                key="language_model",
                on_change=save_user_preferences,
                kwargs={"update_key": "language_model"},
            )

    if st.session_state.user_preferences["language_model"] == LLM_OPTIONS.ECHOBOT:
        st.caption("no settings for `echobot` - it just repeats what you say mainly for testing.")

    elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.OPENAI:
        st.text_input(
            "OpenAI API key",
            key="openai_api_key",
            value=st.session_state.user_preferences["openai_api_key"],
            on_change=save_user_preferences,
            kwargs={"update_key": "openai_api_key"},
            disabled=(st.session_state.username == 'demo'),
            type='password' if st.session_state.username == 'demo' else 'default'
        )

    elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.MISTRAL_LOCAL:
        st.caption("no settings for local `mistral` - good luck!")

    elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.LLAMA2_LOCAL:
        st.caption("no settings for local `llama2` - good luck!")

    elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.MISTRAL_API:
        st.toggle(
            "Safe mode",
            key="mistral_safemode",
            value=st.session_state.user_preferences["mistral_safemode"],
            on_change=save_user_preferences,
            kwargs={"toggle_key": "mistral_safemode"},
            help="Safe mode is not yet implemented by mistral ai.  It also turns mistral into a little bitch... you don't want that, do you?",
            disabled=True
        )

        st.radio("Mistral model select",
            key="mistral_model",
            options=MISTRAL_MODELS,
            index=MISTRAL_MODELS.index(st.session_state.user_preferences["mistral_model"]),
            on_change=save_user_preferences,
            kwargs={"update_key": "mistral_model"},
        )

        st.text_input(
            "Mistral API key",
            key="mistral_api_key",
            value=st.session_state.user_preferences["mistral_api_key"],
            on_change=save_user_preferences,
            kwargs={"update_key": "mistral_api_key"},
            disabled=(st.session_state.username == 'demo'),
            type='password' if st.session_state.username == 'demo' else 'default'
        )
    


def settings_stt():
    # with st.container(border=True):
    stt_options = [STT_OPTIONS.PYTHON, STT_OPTIONS.ASSEMBLYAI]
    selected_stt = stt_options.index(st.session_state.user_preferences["stt"])
    st.selectbox(
            label="🗣️🤖 Voice transcription",
            options=stt_options,
            index=selected_stt,
            key="stt",
            on_change=save_user_preferences,
            kwargs={"update_key": "stt"},
        )
    
    if st.session_state.get("stt") == STT_OPTIONS.PYTHON:
        st.caption("No settings for `python` - it's free and it works")
    
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


def settings_tts():
    # with st.container(border=True):
    tts_options = [TTS_OPTIONS.GOOGLE, TTS_OPTIONS.OPENAI]
    selected_tts = tts_options.index(st.session_state.user_preferences["tts"])
    st.selectbox(
        label="🤖💬 Text to speech",
        options=tts_options,
        index=selected_tts,
        key="tts",
        on_change=save_user_preferences,
        kwargs={"update_key": "tts"},
    )


    if st.session_state.get("tts") == "Google TTS":
        st.caption("No settings for `gTTS` - it's free and it works")

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
        st.toggle("Confirm stt", key="confirm_stt", value=False)

    ### SWITCH SETTINGS LOCATION BUTTON
    with col2[1]:
        move_button_text = f"Move to {'main' if st.session_state.user_preferences['settings_on_sidebar'] else 'sidebar'}"
        st.button(move_button_text,
                    on_click=save_user_preferences,
                    kwargs={"toggle_key": "settings_on_sidebar"},
                    key="button_move_to_main",
                    use_container_width=True)



def init_model():
    if 'model' in st.session_state:
        return

    if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.ECHOBOT:
        st.session_state.model = Echobot()
    
    if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.UPPERCASEBOT:
        st.session_state.model = UppercaseBot()
    
    if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.MISTRAL_API:
        st.session_state.model = MistralAPI()

    if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.MISTRAL_LOCAL:
        st.session_state.model = MistralLocal()

    if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.LLAMA2_LOCAL:
        st.session_state.model = Llama2Local()

    if st.session_state.user_preferences['language_model'] == LLM_OPTIONS.OPENAI:
        st.session_state.model = OpenAIAPI()
