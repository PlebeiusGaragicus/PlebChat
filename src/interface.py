import streamlit as st

from src.common import (
    ChatMessage,
    save_chat_history,
)

from src.settings import (
    TTS_OPTIONS
)



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








def interrupt():
    """ callback for the interrupt button """
    # st.session_state.interrupt = True
    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
    st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))
    # save_chat_history()
    # st.session_state.appstate.load_chat_history()

    if save_chat_history():
        st.session_state.appstate.load_chat_history()

    # st.rerun() # not allowed in on_click handlers (callbacks)


# def settings():
#     """ callback for the configuration button """
#     # st.toast("Settings not yet implemented", icon="🚧")
#     st.session_state.route = PageRoute.SETTINGS
