import os
import base64
import time
import io
import yaml
from yaml.loader import SafeLoader

import streamlit as st

from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException
from openai import OpenAI


import logging
log = logging.getLogger(__file__)

from src.VERSION import VERSION
from src.common import (
    ChatAppVars,
    OPENAI_TTS_MODELS,
    TTS_VOICE_CHOICES,
    save_chat_history,
    load_convo,
    delete_this_chat,
    center_text,
    centered_button_trick,
    column_fix,
    PREFERENCES_PATH,
    LLM_OPTIONS,
    STT_OPTIONS,
    TTS_OPTIONS,
    MISTRAL_MODELS
)

from src.interface import (
    autoplay_audio,
    interrupt,
)

print("\n\nLOADING AND RUNNING TOP-LEVEL CODE FOR EACH USER ACTION?!\n\n")


def load_settings():
    appstate = st.session_state

    if 'user_preferences' not in st.session_state:
        try:
            preferences_file = PREFERENCES_PATH / f"{appstate.username}.yaml"
            appstate.user_preferences = yaml.load(open(preferences_file), Loader=SafeLoader)
        except FileNotFoundError:
            appstate.user_preferences = DEFAULT_USER_PREFERENCES  # Use default preferences
            st.error("user preferences yaml file not found. Creating a new one with default settings.")
            with open(preferences_file, "w") as f:
                yaml.dump(appstate.user_preferences, f)
# if 'user_preferences' not in st.session_state:
# #     appstate.user_preferences = load_user_preferences(appstate.username)
#     try:
#         appstate.user_preferences = yaml.load(open("user_preferences.yaml"), Loader=SafeLoader)
#     except FileNotFoundError:
#         user_preferences = {}
#         # write to file
#         with open("user_preferences.yaml", "w") as f:
#             yaml.dump(user_preferences, f)
#         st.error("user_preferences.yaml not found.  Creating a new one.")
# if 'user_preferences' not in st.session_state:
#     try:
#         preferences_file = PREFERENCES_PATH / f"{appstate.username}.yaml"
#         appstate.user_preferences = yaml.load(open(preferences_file), Loader=SafeLoader)
#     except FileNotFoundError:
#         appstate.user_preferences = DEFAULT_USER_PREFERENCES  # Use default preferences
#         st.error("user preferences yaml file not found. Creating a new one with default settings.")
#         with open(preferences_file, "w") as f:
#             yaml.dump(appstate.user_preferences, f)



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
        settings_llm()
        settings_stt()
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



# Define default user preferences
DEFAULT_USER_PREFERENCES = {
    "settings_on_sidebar": False,
    "language_model": LLM_OPTIONS.MISTRAL_API,
    "stt": STT_OPTIONS.PYTHON,
    "tts": TTS_OPTIONS.GOOGLE,
    "mistral_safemode": True,
    "mistral_model": "mistral-medium",
    "mistral_api_key": None,
    "openai_api_key": None,
    "openai_voice": TTS_VOICE_CHOICES[0],
    "openai_tts_rate": 1.2,
}

# @st.cache_data()
def load_user_preferences(username):
    preferences_file = PREFERENCES_PATH / f"{username}.yaml"
    try:
        with open(preferences_file) as f:
            return yaml.load(f, Loader=SafeLoader)
    except FileNotFoundError:

        return DEFAULT_USER_PREFERENCES


def save_user_preferences(update_key=None, toggle_key=None):
    # appstate = st.session_state.appstate
    # appstate = st.session_state
    print(f"save_user_preferences({update_key}, {toggle_key})")

    if update_key is None and toggle_key is None:
        raise ValueError("Either key_to_save or toggle_key must be set")

    print("CURRENT STATE:")
    print(st.session_state.user_preferences)

    if toggle_key is not None:
        print(f"Toggling: {toggle_key}")
        st.session_state.user_preferences[toggle_key] = False if st.session_state.user_preferences[toggle_key] is True else True
        # print(st.session_state.user_preferences)
        

    if update_key is not None:
        # user_preferences = {
        #     "settings_on_sidebar": st.session_state.user_preferences["settings_on_sidebar"], # This one is unique because we use a button and not a widget with a state
        #     "language_model": st.session_state.language_model,
        #     "stt": st.session_state.stt,
        #     "tts": st.session_state.tts,
        #     "mistral_safemode": st.session_state.mistral_safemode,
        #     "mistral_model": st.session_state.mistral_model,
        #     "mistral_api_key": st.session_state.mistral_api_key,
        #     "openai_api_key": st.session_state.openai_api_key,
        #     "openai_voice": st.session_state.openai_voice,
        #     "openai_tts_rate": st.session_state.openai_tts_rate,
        # }
    # else:
        # user_preferences = st.session_state.user_preferences
        # user_preferences[key_to_save] = st.session_state[key_to_save]
        st.session_state.user_preferences[update_key] = st.session_state[update_key]

    # print(user_preferences)
    print("SAVING THIS STATE:")
    print(st.session_state.user_preferences)

    preferences_file = PREFERENCES_PATH / f"{st.session_state.appstate.username}.yaml"
    with open(preferences_file, "w") as f:
        yaml.dump(st.session_state.user_preferences, f)

    del st.session_state.user_preferences
    # load_user_preferences.clear_cache()
    st.toast("User preferences saved!")
    # st.balloons()



def settings_llm():
    ### LANGUAGE MODEL ###
    llm_options = [
        LLM_OPTIONS.MISTRAL_API,
        LLM_OPTIONS.MISTRAL_LOCAL,
        LLM_OPTIONS.GPT3_5,
        LLM_OPTIONS.ECHOBOT,
    ]
    selected_llm_index = llm_options.index(st.session_state.user_preferences["language_model"])
    with st.container(border=True):
        st.selectbox("🧠 Language Model",
                    options=llm_options,
                    index=selected_llm_index,
                    key="language_model",
                    on_change=save_user_preferences,
                    # args=("language_model",)
                    kwargs={"update_key": "language_model"},
                )

        if st.session_state.user_preferences["language_model"] == LLM_OPTIONS.ECHOBOT:
            st.write("no settings for `echobot`")

        elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.GPT3_5:
            st.write("no settings yet")

        elif st.session_state.user_preferences["language_model"] == LLM_OPTIONS.MISTRAL_API:
            st.toggle(
                "Safe mode",
                key="mistral_safemode",
                value=st.session_state.user_preferences["mistral_safemode"],
                on_change=save_user_preferences,
                # args=("mistral_safemode",),
                kwargs={"toggle_key": "mistral_safemode"},
                help="Safe mode is not yet implemented by mistral ai.  It also turns mistral into a little bitch... you don't want that, do you?",
                # disabled=True
            )

            st.radio("Mistral model select",
                key="mistral_model",
                options=MISTRAL_MODELS,
                index=MISTRAL_MODELS.index(st.session_state.user_preferences["mistral_model"]),
                on_change=save_user_preferences,
                # args=("mistral_model",)
                kwargs={"update_key": "mistral_model"},

            )

            st.text_input(
                "Mistral API key",
                key="mistral_api_key",
                value=st.session_state.user_preferences["mistral_api_key"],
                on_change=save_user_preferences,
                # args=("mistral_api_key",),
                kwargs={"update_key": "mistral_api_key"},
                disabled=(st.session_state.appstate.username == 'demo'),
                type='password' if st.session_state.appstate.username == 'demo' else 'default'
            )


def settings_stt():
    ### SPEECH TO TEXT ###
    with st.container(border=True):
        stt_options = [STT_OPTIONS.PYTHON, STT_OPTIONS.ASSEMBLYAI]
        selected_stt = stt_options.index(st.session_state.user_preferences["stt"])
        st.selectbox(
                label="🗣️🤖 Voice transcription",
                options=stt_options,
                index=selected_stt,
                key="stt",
                on_change=save_user_preferences,
                # args=("stt",)
                kwargs={"update_key": "stt"},
            )


def settings_tts():
    ### TEXT TO SPEECH ###
    with st.container(border=True):
        tts_options = [TTS_OPTIONS.GOOGLE, TTS_OPTIONS.OPENAI]
        selected_tts = tts_options.index(st.session_state.user_preferences["tts"])
        st.selectbox(
            label="🤖💬 Text to speech",
            options=tts_options,
            index=selected_tts,
            key="tts",
            on_change=save_user_preferences,
            # args=("tts",)
            kwargs={"update_key": "tts"},
        )


        if st.session_state.get("tts") == "Google TTS":
            st.caption("No settings for Google TTS.  It's free and it works ;)")

        if st.session_state.get("tts") == "OpenAI TTS":
            cols = st.columns((1, 1))
            cols[0].radio(
                "Voice model",
                options=TTS_VOICE_CHOICES,
                index=TTS_VOICE_CHOICES.index(st.session_state.user_preferences['openai_voice']),
                on_change=save_user_preferences,
                # args=("openai_voice",),
                kwargs={"update_key": "openai_voice"},
                key="openai_voice")

            talking_speed_options = [1.0, 1.2, 1.5]
            cols[1].radio(
                "Talking speed",
                options=talking_speed_options,
                index=talking_speed_options.index(st.session_state.user_preferences['openai_tts_rate']),
                on_change=save_user_preferences,
                # args=("openai_tts_rate",),
                kwargs={"update_key": "openai_tts_rate"},
                key="openai_tts_rate")
        
            st.text_input(
                "OpenAI API key",
                key="openai_api_key",
                value=st.session_state.user_preferences["openai_api_key"],
                on_change=save_user_preferences,
                # args=("openai_api_key",),
                kwargs={"update_key": "openai_api_key"},
                disabled=(st.session_state.username == 'demo'),
                type='password' if st.session_state.username == 'demo' else 'default'
            )


def settings_bottom_buttons():
    col2 = st.columns((1, 1))
    ### LOGOUT BUTTON
    # with col2[0]:
        # st.session_state.authenticator.logout(f"Logout `{st.session_state['username']}`", "main")

    ### SWITCH SETTINGS LOCATION BUTTON
    with col2[1]:
        move_button_text = f"Move to {'main' if st.session_state.user_preferences['settings_on_sidebar'] else 'sidebar'}"
        st.button(move_button_text,
                    on_click=save_user_preferences,
                    kwargs={"toggle_key": "settings_on_sidebar"},
                    key="button_move_to_main",
                    use_container_width=True)




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
