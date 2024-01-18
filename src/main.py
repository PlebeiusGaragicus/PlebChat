import os
import yaml

import streamlit as st
import streamlit_authenticator as stauth

import logging
log = logging.getLogger()

from src.common import (
    init_if_needed,
    ASSETS_PATH
)

from src.main_page import main_page


print("\n\nLOADING AND RUNNING TOP-LEVEL CODE FOR EACH USER ACTION?!\n\n")


def main():
    st.set_page_config(
        page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="centered", # vs wide
        initial_sidebar_state="auto",
        # menu_items={"About": "https://plebby.me/"} # TODO
    )

    try:
        with open("./auth.yaml") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
        st.stop()

    st.session_state.authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    if st.session_state["authentication_status"] is None:
        # with centered_button_trick():
        #     st.image(os.path.join(ASSETS_PATH, "assistant2sm.png"))
        # center_text("p", "🗣️🤖💬", size=60) # or h1, whichever
        if 'appstate' in st.session_state:
            del st.session_state['appstate']
            st.error("Application state has been cleared!")

    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")

    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    st.session_state.authenticator.login("PlebChat login", "main")

    if st.session_state["authentication_status"]:
        init_if_needed()

        # from src.main_page import main_page
        main_page()
