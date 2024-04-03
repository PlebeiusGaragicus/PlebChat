import streamlit as st

from src.common import (
    AVATAR_PATH,
    not_init,
    is_init,
    get
)

from mistralai.models.chat_completion import ChatMessage
from src.flows import ChatThread



def cmp_chat_window():
    if not_init("construct"):

        # >> CLEAR THE VARIABLES USED IN THIS COMPONENT
        if is_init("thread"):
            st.toast("deleting thread")
            del st.session_state.thread

        return


    



    with st.container(border=True):

        human_avatar = f"{AVATAR_PATH}/user0.png"
        ai_avatar = f"{AVATAR_PATH}/{get('construct').avatar_filename}"

        if is_init("thread"):
            for message in st.session_state.thread.messages:
                with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
                    st.markdown(message.content)


        my_next_prompt_placeholder = st.empty()

        prompt = st.chat_input("Ask a question.")

        if prompt:
            if not_init("thread"):
                st.toast("new thread!!")
                st.session_state.thread = ChatThread()

            my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
            st.session_state.thread.messages.append( ChatMessage(role="user", content=prompt) )
