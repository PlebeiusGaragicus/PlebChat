import os
import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

import logging
log = logging.getLogger()

from src.VERSION import VERSION, CHANGELOG
from src.common import (
    ChatAppVars,
    PageRoute,
    column_fix
)



def show_api_keys_entry():
    with open("./auth.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)


    with st.expander("API Keys"):
        try:
            key = config["credentials"]["usernames"][st.session_state["username"]]["api_key_openai"]
        except KeyError:
            key = ""
        st.text_input("OpenAI", key="api_key_openai", value=key)

        try:
            key = config["credentials"]["usernames"][st.session_state["username"]]["api_key_assemblyai"]
        except KeyError:
            key = ""
        st.text_input( "Assembly AI", key="api_key_assemblyai", value=key)

        try:
            key = config["credentials"]["usernames"][st.session_state["username"]]["api_key_mistral"]
        except KeyError:
            key = ""
        st.text_input( "Mistral", key="api_key_mistral", value=key)

        st.button("Save API Keys", on_click=save_api_keys)


def save_api_keys():
    with open("./auth.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    log.debug(config["credentials"]["usernames"])

    current_user = st.session_state["username"]
    config["credentials"]["usernames"][current_user]["api_key_openai"] = st.session_state["api_key_openai"]
    config["credentials"]["usernames"][current_user]["api_key_assemblyai"] = st.session_state["api_key_assemblyai"]
    config["credentials"]["usernames"][current_user]["api_key_mistral"] = st.session_state["api_key_mistral"]

    with open("./auth.yaml", "w") as file:
        yaml.dump(config, file)

    st.toast("API keys saved!", icon="🔑")



def settings_page(appstate: ChatAppVars, authenticator: stauth.Authenticate):
    def go_to_main_page():
        st.session_state.route = PageRoute.MAIN

    st.write("# Settings")
    column_fix()

    st.button("👈 back", on_click=go_to_main_page, use_container_width=True)
    # top_buttons = st.columns((2, 1))
    # with top_buttons[0]:
    #     st.button("👈 back", on_click=go_to_main_page, use_container_width=True)
    # with top_buttons[1]:
    #     # authenticator.logout_button("🚪 Logout")
    #     st.session_state.authenticator.logout("🚪 Logout", "main")


    st.write("---")

    if not st.session_state.username == "demo":
        show_api_keys_entry()
    else:
        st.info("Editing API keys are disabled in demo mode.")

    st.markdown("---")
    st.caption(f"username: `{st.session_state['username']}`")
    st.session_state.authenticator.logout("🚪 Logout", "main")
    st.caption(f"running version {VERSION}")

    if appstate.debug:
        with st.expander("Debugging", expanded=True):
            st.write(f"username: `{st.session_state['username']}`")
            st.write(appstate)

        # st.warning("Running in debug mode.")
    else:
        st.caption("Running in production mode.")

        st.write(CHANGELOG)
