import os
import pathlib
import yaml

import streamlit as st
import streamlit_authenticator as stauth

import logging
log = logging.getLogger()

from src.common import init_if_needed, PageRoute
from src.main_page import main_page
from src.settings_page import settings_page
import pathlib
import yaml

# ASSETS_PATH = pathlib.Path(__file__).parent / "assets"
ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"


def main():
    st.set_page_config(
        page_title="Pleb Chat",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="centered", # vs wide
        initial_sidebar_state="auto",
        # menu_items={"About": "https://plebby.me/"} # TODO
    )

    # st.image(os.path.join(ASSETS_PATH, "favicon.ico"))

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

    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")

    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    st.session_state.authenticator.login("ACCESS RESTRICTED", "main")

    if st.session_state["authentication_status"]:
        ### PAGE ROUTING GOES HERE ###
        init_if_needed()

        appstate = st.session_state.appstate
        if st.session_state["route"] == PageRoute.MAIN:
            main_page(appstate)

        elif st.session_state["route"] == PageRoute.SETTINGS:
            settings_page(appstate, None)

        elif st.session_state["route"] == PageRoute.ABOUT:
            st.write("About")
