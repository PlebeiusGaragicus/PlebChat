import os
import yaml
import time

import streamlit as st
import streamlit_authenticator as stauth

from src.common import ASSETS_PATH

from src.interface.root_panel import root_panel
from src.main import main_page, init_if_needed

from src.common import not_init, get, cprint, Colors


cprint(">>> Streamlit Server rerun~!", Colors.CYAN)




def login_router_page():
    """
    ```python
        if st.session_state["authentication_status"]:
            authenticator.logout()
            st.write(f'Welcome *{st.session_state["name"]}*')
            st.title('Some content')
        elif st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
    ```
    """

    st.set_page_config(
        # page_title="DEBUG!" if os.getenv("DEBUG", False) else "NOS4A2",
        page_title="PlebChat!",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="wide",
        initial_sidebar_state="auto",
    )

    try:
        with open("./auth.yaml") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        st.error("This instance has not been configured.  Missing `auth.yaml` file.")
        # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
        st.stop()

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["pre-authorized"],
    )
    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    authenticator.login(location="main", max_concurrent_users=1, fields={
        "Form name": "PlebChat!",
        "Username": "Username",
        "Password": "Password",
        "Login": "Welcome!",
    })


    if st.session_state["authentication_status"]:
        # init_if_needed()
        # main_page(authenticator)
        if st.session_state.username == 'root':
            root_panel(authenticator)
        else:
            init_if_needed()
            main_page(authenticator)


    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")

    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
        if 'appstate' in st.session_state:
            del st.session_state['appstate']
            st.error("Application state has been cleared!")
        # st.error("logged out... refresh page to continue") # TODO - i'm using an is-init kind of var in session state... I may need to clear this on logout
