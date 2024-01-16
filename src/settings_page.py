import os
import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

import logging
log = logging.getLogger()

from src.VERSION import VERSION
from src.common import (
    ChatAppVars,
    PageRoute,
    column_fix,
    center_text,
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


def centered_button_trick():
    """ Use this in a `with` statement to center a button.
    
    Example:
    ```python
    with centered_button_trick():
        st.button(
            "👈 back",
            on_click=go_to_main_page,
            use_container_width=True)
    ```
    """
    columns = st.columns((1, 2, 1))
    with columns[0]:
        st.empty()
    # with columns[1]:
        # normally the button logic would go here
    with columns[2]:
        st.empty()

    return columns[1]


def settings_page(appstate: ChatAppVars, authenticator: stauth.Authenticate):
    def go_to_main_page():
        if 'appstate' in st.session_state:
            # This will force a reload of the appstate so we'll load the new API keys
            del st.session_state.appstate
        st.session_state.route = PageRoute.MAIN
    
    column_fix()

    center_text("h1", "⚙️", 60)
    with centered_button_trick():
        st.button("👈 back", on_click=go_to_main_page, use_container_width=True)
    # st.write("")
    st.write("---")
    # center_text("h1", "🧰 ⌥ ⚙️", 60)


    if not st.session_state.username == "demo":
        show_api_keys_entry()
    else:
        st.info("Editing API keys are disabled in demo mode.")

    st.markdown("---")
    st.caption(f"username: `{st.session_state['username']}`")
    with centered_button_trick():
        st.session_state.authenticator.logout("Logout", "main")
    st.caption(f"running version {VERSION}")

    if appstate.debug:
        # with st.expander("Debugging", expanded=True):
        #     st.write(f"username: `{st.session_state['username']}`")
        #     st.write(appstate)

        st.warning("Running in debug mode.")
    else:
        st.caption("Running in production mode.")
