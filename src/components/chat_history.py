import streamlit as st

from src.interface import center_text

from src.chat_history import (
    save_chat_history,
    load_convo,
    delete_this_chat,
)



def cmp_chat_history():
    appstate = st.session_state.appstate

    with st.sidebar:
        st.header("", divider="rainbow")
        # st.write("## :rainbow[Past Conversations]")
        st.write("## :orange[Conversation History]")

        if len(appstate.chat.messages) > 0:
            sidebar_new_button_placeholder = st.columns((1, 1))
            sidebar_new_button_placeholder[0].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="delbutton2", use_container_width=True)
            sidebar_new_button_placeholder[1].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True, key="newbutton2")
            center_text('p', "---", size=9)
        # with st.expander("Past Conversations", expanded=False):
        if len(appstate.chat_history) == 0:
            st.caption("No past conversations... yet")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        if appstate.truncated:
            st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
            st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        st.header("", divider="rainbow")
