import os
import yaml

import streamlit as st
import streamlit_authenticator as stauth

from src.common import ASSETS_PATH

from src.root_panel import root_panel
from src.main import main_page, init_if_needed


def login_router_page():
    st.set_page_config(
        page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="centered",
        initial_sidebar_state="auto",
    )

    try:
        with open("./auth.yaml") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
        # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
        st.stop()

    st.session_state.authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        # config["preauthorized"],
    )

    if st.session_state["authentication_status"] is None:
        if 'appstate' in st.session_state:
            del st.session_state['appstate']
            st.error("Application state has been cleared!")

    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")

    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    st.session_state.authenticator.login("PlebChat login", "main")

    if st.session_state["authentication_status"]:

        if st.session_state.username == 'root':
            root_panel()
        else:
            init_if_needed()
            main_page()
