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
    centered_button_trick,
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
    # column_fix() # TODO put in main()???
    # center_text("h1", "🧰 ⌥ ⚙️", 60)
    center_text("h1", "⚙️", 60)

    # st.write("---")

    def go_to_main_page():
        if 'appstate' in st.session_state:
            # This will force a reload of the appstate so we'll load the new API keys
            del st.session_state.appstate
        st.session_state.route = PageRoute.MAIN

    with centered_button_trick():
        st.button("👈 back", on_click=go_to_main_page, use_container_width=True)




    with open("./auth.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    LLM_options = [
        "echobot",
        "GPT-3",
        "Mistral",
    ]

    with st.expander("Select a language model", expanded=True):
        col2 = st.columns((1, 2))
        with col2[0]:
            st.radio("Available LLMs",
                        options=LLM_options,
                        index=1,
                        key="language_model",
                    )

        with col2[1]:
            with st.container(border=True):
                # st.write("### LLM settings")
                center_text("h3", "LLM settings", 20)

                if st.session_state.language_model == "echobot":
                    st.write("no settings for `echobot`")

                elif st.session_state.language_model == "GPT-3":
                    st.write("no settings yet")

                elif st.session_state.language_model == "Mistral":
                    st.radio("Mistral",
                        options=["tiny", "small", "medium"],
                        index=2,
                        key="settings",
                    )
                    st.toggle("Safe mode", key="safe_mode", value=False)
                    st.text_input("API key", key="api_key_mistral", value=st.session_state["api_key_mistral"])



    # if not st.session_state.username == "demo":
    #     show_api_keys_entry()
    # else:
    #     st.info("Editing API keys are disabled in demo mode.")

    st.markdown("---")
    # st.button("About this project", on_click=lambda: st.session_state.update({"route": PageRoute.ABOUT}), use_container_width=False)
    st.session_state.authenticator.logout(f"Logout `{st.session_state['username']}`", "main")

    st.caption(f"running version {VERSION}")

    if appstate.debug:
        with st.expander("Debugging", expanded=True):
            st.write(f"username: `{st.session_state['username']}`")
            st.write(appstate)
    else:
        st.caption("Running in production mode.")
