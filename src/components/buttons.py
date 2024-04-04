import streamlit as st

from src.flows import ChatThread

from src.common import (
    not_init,
)

def new_thread():
    st.toast("new thread!!")
    st.session_state.thread = ChatThread()

def del_thread():
    st.toast("deleting thread")
    st.toast("Not yet implemented!!")
    del st.session_state.thread
    st.session_state.thread = ChatThread()


### READ IT AND NEW BUTTONS
# def bmp_buttons(before_speech_placeholder):
def bmp_buttons():
    if not_init("thread"):
        return

    # appstate = st.session_state.appstate
    # with before_speech_placeholder:
    with st.container():
    # with before_speech_placeholder.container():
        if len(st.session_state.thread.messages) > 0:
            # if last message was from the bot, then we can read it aloud
            col2 = st.columns((1, 1, 1))
            col2[2].button("🌱 :green[New]", on_click=new_thread, use_container_width=True)
            # if col2[2].button("🌱 :green[New]", use_container_width=True):
                # st.toast("new thread!!")
                # st.session_state.thread = ChatThread()

            col2[1].button("🗑️ :red[Delete]", on_click=del_thread, use_container_width=True)
            # if col2[1].button("🗑️ :red[Delete]", key="button_delete", use_container_width=True):
                # st.toast("Not yet implemented!!")
                # st.toast("deleting thread")
                # del st.session_state.thread
                # st.session_state.thread = ChatThread()
                # st.rerun()


            # if st.session_state.thread.messages[-1].role == "assistant":
                # centered_button_trick().button("🗣️ Speak", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)
                # if st.session_state.read_to_me is False:
                    # def on_click_read_to_me():
                    #     st.session_state.speak_this = st.session_state.thread.messages[-1].content
                    # col2[0].button("🗣️ :blue[Speak]", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)

