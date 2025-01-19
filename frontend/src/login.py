import yaml

import streamlit as st
import streamlit_authenticator as stauth

# https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
# https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io

AUTH_YAML_PATH = "/app/auth.yaml"




def login() -> bool:
    """ Return True if logged in, False otherwise """

    # first time run - load authenticator
    if st.session_state.get("authenticator", None) is None:
        try:
            with open(AUTH_YAML_PATH) as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            st.error("This instance has not been configured.  Missing `auth.yaml` file.")
            # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
            st.stop()

        st.session_state.authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            # config["pre-authorized"],
        )

    st.session_state.authenticator.login(location="main", max_concurrent_users=1, fields={
        "Form name": ":rainbow[PlebChat!]",
        "Username": ":blue[Username]",
        "Password": ":red[Password]",
        "Login": ":green[Welcome!]",
    })

    if st.session_state["authentication_status"]:
        return True

    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return False

    elif st.session_state["authentication_status"] is None:
        return False

    return False # 🤷 should never get here - just in case