import io
import base64

import streamlit as st

from src.settings import (
    OPENAI_TTS_MODELS,
    TTS_VOICE_CHOICES,
    TTS_OPTIONS
)


from openai import OpenAI

# def autoplay_audio(file_path: str):
def autoplay_audio(audio_base64: str):
    """ https://discuss.streamlit.io/t/how-to-play-an-audio-file-automatically-generated-using-text-to-speech-in-streamlit/33201 """

    md = f"""
        <audio id="myAudio" controls autoplay="true">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            document.getElementById('myAudio').playbackRate = 1.5;
        </script>
        """

    if st.session_state.user_preferences["tts"] == TTS_OPTIONS.GOOGLE:
        with st.sidebar:
            with st.expander(".", expanded=False):
                st.components.v1.html(md)
    else:
        st.write(md, unsafe_allow_html=True) # won't speed up the playback

    # st.write("""
    # st.components.v1.html("""
    #     <script>
    #         document.getElementsByTagName('audio')[0].playbackRate = 1.5;
    #     </script>
    #                       """)
        # unsafe_allow_html=True)

    # doesn't look so good on mobile...
    # with centered_button_trick():
        # st.markdown(md, unsafe_allow_html=True)


# NOTE: you need to adjust the website setting in safari to allow auto play media
def TTS(text, language='en', slow=False):
    with st.spinner("💬 Generating speech..."):
        if st.session_state.user_preferences["tts"] == TTS_OPTIONS.GOOGLE:
            try:
                # TODO - attempting to do delayed imports for speed (not sure if this works)
                from gtts import gTTS, gTTSError
                tts = gTTS(text=text, lang=language, slow=slow)

                with io.BytesIO() as file_stream:
                    tts.write_to_fp(file_stream) # Write the speech data to the file stream
                    file_stream.seek(0) # Move to the beginning of the file stream
                    audio_base64 = base64.b64encode(file_stream.read()).decode('utf-8') # Read the audio data and encode it in base64
                autoplay_audio(audio_base64)
            except gTTSError as e:
                st.error(e)
                st.exception(e)


        if st.session_state.user_preferences["tts"] == TTS_OPTIONS.OPENAI:
            if st.session_state.user_preferences["openai_api_key"] in [None, ""]:
                raise Exception("OpenAI API key not set.")

            import openai
            openai_client = OpenAI(api_key=st.session_state.user_preferences["openai_api_key"])

            voice = st.session_state.openai_voice
            # OPENAI_TTS_MODELS = ["echo", "onyx", "nova"]
            if voice == TTS_VOICE_CHOICES[0]:
                tts_model = OPENAI_TTS_MODELS[0]
            elif voice == TTS_VOICE_CHOICES[1]:
                tts_model = OPENAI_TTS_MODELS[1]
            else:
                tts_model = OPENAI_TTS_MODELS[2]

            try: #TODO -rerun this code if there's a timeout error
                speech = openai_client.audio.speech.create(
                        model="tts-1",
                        voice=tts_model,
                        # response_format="opus",
                        response_format="mp3",
                        input=f"{text}",
                        speed=st.session_state.openai_tts_rate
                    )
            except openai.APITimeoutError as e:
                st.error(e)
                st.exception(e)

            # Extract audio data from the response
            audio_data = speech.content

            # Convert audio data to Base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            autoplay_audio(audio_base64)
