import os

import streamlit as st

from src.common import (
    is_init,
    get,
    cprint, 
    Colors,
)

from src.components.header import cmp_header, cmp_pills, cmp_intro
from src.components.construct_settings import cmp_construct_settings
from src.components.chat_window import cmp_chat_window
from src.components.chat_history import cmp_chat_history
from src.components.tail import cmp_tail


def main_page():
    cprint("\n\nRERUN!!!!!!\n", Colors.YELLOW)

    cmp_header()
    cmp_pills()
    cmp_construct_settings()

    # cmp_intro()
    cmp_chat_window()
    cmp_chat_history()

    st.sidebar.header("", divider="rainbow")
    cmp_tail()






    # cmp_debug()
# def cmp_debug():
    if not os.getenv("DEBUG", False):
        return

    with st.sidebar:
        # with st.popover("🔧 :red[Debug]"):
        with st.expander("debug", expanded=True):
            debug_placeholder = st.container()
            st.write(st.session_state)
            if is_init("construct"):
                with st.popover("Construct"):
                    st.write(get("construct"))
            if is_init("thread"):
                debug_placeholder.write(st.session_state.thread.messages)
