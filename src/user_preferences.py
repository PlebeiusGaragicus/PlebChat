import yaml
import pathlib
import streamlit as st


PREFERENCES_PATH = pathlib.Path(__file__).parent.parent / "preferences"



# def load_settings():
#     appstate = st.session_state

#     if 'user_preferences' not in st.session_state:
#         try:
#             preferences_file = PREFERENCES_PATH / f"{appstate.username}.yaml"
#             appstate.user_preferences = yaml.load(open(preferences_file), Loader=yaml.loader.SafeLoader)

#         except FileNotFoundError:
#             # Use default preferences
#             from src.settings import LLM_OPTIONS, STT_OPTIONS, TTS_OPTIONS, TTS_VOICE_CHOICES
#             appstate.user_preferences = {
#                 "assemblyai_api_key": None,
#                 "language_model": LLM_OPTIONS.MISTRAL_API,
#                 "mistral_api_key": None,
#                 "mistral_model": "mistral-medium",
#                 "mistral_safemode": True,
#                 "openai_api_key": None,
#                 "openai_tts_rate": 1.2,
#                 "openai_voice": TTS_VOICE_CHOICES[0],
#                 "settings_on_sidebar": False,
#                 "stt": STT_OPTIONS.PYTHON,
#                 "tts": TTS_OPTIONS.GOOGLE,
#                 "confirm_stt": True,
#             }

#             st.error("user preferences yaml file not found. Creating a new one with default settings.")
#             with open(preferences_file, "w") as f:
#                 yaml.dump(appstate.user_preferences, f)
def load_settings():
    appstate = st.session_state

    if 'user_preferences' not in st.session_state:
        try:
            preferences_file = PREFERENCES_PATH / f"{appstate.username}.yaml"
            appstate.user_preferences = yaml.load(open(preferences_file), Loader=yaml.loader.SafeLoader)

        except FileNotFoundError:
            # Use default preferences
            from src.settings import STT_OPTIONS, TTS_OPTIONS
            appstate.user_preferences = {
                "stt": STT_OPTIONS.PYTHON,
                "tts": TTS_OPTIONS.GOOGLE,
                "confirm_stt": True,
            }

            st.error("user preferences yaml file not found. Creating a new one with default settings.")
            with open(preferences_file, "w") as f:
                yaml.dump(appstate.user_preferences, f)



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
