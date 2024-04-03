import streamlit as st

### READ IT AND NEW BUTTONS
def cmp_button(before_speech_placeholder):
    appstate = st.session_state.appstate
    with before_speech_placeholder:
        if len(st.session_state.thread.messages) > 0:
            # if last message was from the bot, then we can read it aloud
            col2 = st.columns((1, 1, 1))
            col2[2].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True)
            col2[1].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="button_delete", use_container_width=True)
            if st.session_state.thread.messages[-1].role == "assistant":
                # centered_button_trick().button("🗣️ Speak", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)
                if st.session_state.read_to_me is False:
                    def on_click_read_to_me():
                        st.session_state.speak_this = thread.messages[-1].content
                    col2[0].button("🗣️ :blue[Speak]", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)

