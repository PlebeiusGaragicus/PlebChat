import yaml

import streamlit as st
import streamlit_authenticator as stauth

import logging
log = logging.getLogger()

from src.main_page import main_page




def main():
    st.set_page_config(
        page_title="Pleb Chat",
        layout="centered",
        initial_sidebar_state="auto",
        # menu_items={"About": "https://plebby.me/"} # TODO
    )

    with open("./auth.yaml") as file:
        config = yaml.load(file, Loader=yaml.loader.SafeLoader)

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
        main_page()
