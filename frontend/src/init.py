import os
from PIL import Image

import streamlit as st


from src.config import APP_NAME, STATIC_PATH
from src.interface import Colors, cprint, hide_markdown_header_links, hide_stop_button, mobile_column_fix


def init():

    if st.session_state.get("DEBUG", None) is None:
        if os.getenv("DEBUG", None):
            st.session_state.debug = True
        else:
            st.session_state.debug = False

        ip_addr = st.context.headers.get('X-Forwarded-For', "?")
        user_agent = st.context.headers.get('User-Agent', "?")
        lang = st.context.headers.get('Accept-Language', "?")
        cprint(f"RUNNING for: {ip_addr} - {lang} - {user_agent}", Colors.YELLOW)


    #### PAGE SETUP
    if st.session_state.get("favicon", None) is None:
        favicon = Image.open(os.path.join(STATIC_PATH, "favicon.ico"))
        st.session_state.favicon = favicon

    st.set_page_config(
        page_title=APP_NAME,
        page_icon=st.session_state.favicon,
        layout="wide",
        # initial_sidebar_state="auto",
        initial_sidebar_state="expanded" if st.session_state.debug else "collapsed",
    )

    mobile_column_fix()
    hide_markdown_header_links()

    # only for debug because we use the "reload" and "always reload" buttons that appear on source code change
    if not st.session_state.debug:
        hide_stop_button()