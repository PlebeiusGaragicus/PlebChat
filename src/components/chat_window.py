import streamlit as st

from src.common import (
    AVATAR_PATH,
    not_init,
    get
)


def cmp_chat_window():
    if not_init("construct"):
        return

    human_avatar = f"{AVATAR_PATH}/user0.png"
    ai_avatar = f"{AVATAR_PATH}/{get('construct').avatar_filename}"

    for message in st.session_state.appstate.chat.messages:
        with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
            st.markdown(message.content)


    my_next_prompt_placeholder = st.empty()

    prompt = st.chat_input("Ask a question.")

    if prompt:
        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
