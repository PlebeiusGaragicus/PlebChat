import os
import yaml
import time

import streamlit as st
import streamlit_authenticator as stauth

from src.common import ASSETS_PATH

from src.interface.root_panel import root_panel
from src.main import main_page, init_if_needed

from src.common import not_init, get, cprint, Colors


# cprint(">>> LOGIN ROUTER PAGE", Colors.CYAN)
cprint(">>> Streamlit Server rerun~!", Colors.CYAN)

# print(f"\nf{colorize}>>> STREAMLIT SERVER RE-RUN")


# def login_router_page():
#     st.set_page_config(
#         page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
#         page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
#         layout="centered",
#         initial_sidebar_state="auto",
#         menu_items=None
#     )

#     try:
#         with open("./auth.yaml") as file:
#             config = yaml.safe_load(file)
#     except FileNotFoundError:
#         st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
#         # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
#         st.stop()


#     if 'authentication_status' not in st.session_state:

#         st.session_state.authenticator = stauth.Authenticate(
#             config["credentials"],
#             config["cookie"]["name"],
#             config["cookie"]["key"],
#             config["cookie"]["expiry_days"],
#             config["preauthorized"],
#         )
#         time.sleep(0.5)
#         # NOTE: HOLY SHIT THIS BUG REALLY SHOOK ME FOR AWHILE...!!!!
#         # https://github.com/mkhorasani/Streamlit-Authenticator/issues/131
#         # TODO - still not working well on mobile
#     else:
#         if st.session_state["authentication_status"] is None:
#             if 'appstate' in st.session_state:
#                 del st.session_state['appstate']
#                 st.error("Application state has been cleared!")



#         if st.session_state["authentication_status"]:

#             if st.session_state.username == 'root':
#                 root_panel()
#             else:
#                 init_if_needed()
#                 main_page()


#         if st.session_state["authentication_status"] is False:
#             st.error("Username/password is incorrect")

#         # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
#         # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
            

#         # TODO - do I want to limit concurrent users???~??~?
#         # time.sleep(0.5)
#         # st.session_state.authenticator.login(location="main", max_concurrent_users=1, fields={
#         st.session_state.authenticator.login(location="main", fields={
#             "Form name": "PlebChat login",
#             "Username": "Username",
#             "Password": "Password",
#             "Login": "Enter ye!",
#         })











"""
if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
"""



# def login_router_page():
#     st.set_page_config(
#         page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
#         page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
#         layout="centered",
#         initial_sidebar_state="auto",
#         menu_items=None
#     )

#     try:
#         with open("./auth.yaml") as file:
#             config = yaml.safe_load(file)
#     except FileNotFoundError:
#         st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
#         # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
#         st.stop()

#     # if not_init('authenticator'):
#     if 'authenticator' not in st.session_state:
#         print("Creating authenticator")
#         st.session_state.authenticator = stauth.Authenticate(
#                 config["credentials"],
#                 config["cookie"]["name"],
#                 config["cookie"]["key"],
#                 config["cookie"]["expiry_days"],
#                 config["preauthorized"],
#             )
#         time.sleep(0.5) # This prevents the flashing of the login page, if nothing else.
#         # time.sleep(0.05) # This prevents the flashing of the login page, if nothing else. #NOTE: BUT ONLY ON LOCALHOST?!?!?


#     if st.session_state["authentication_status"] is False:
#         st.error('Username/password is incorrect')


#     if st.session_state["authentication_status"] is None:
#         # get('authenticator').login()
#         st.session_state.authenticator.login()

#         # st.warning('Please enter your username and password')
#         # if 'appstate' in st.session_state:
#         #     del st.session_state['appstate']
#             # st.error("Application state has been cleared!")




#     if st.session_state["authentication_status"]:
#         # authenticator.logout()

#         if st.session_state.username == 'root':
#             # root_panel(authenticator)
#             root_panel()
#         else:
#             init_if_needed()
#             # main_page(authenticator)
#             main_page()













































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

    landing_page_container = st.empty()
    with landing_page_container.container(border=True):
        st.markdown("# PlebChat!")
        # NOTE: don't use images - they flash...
        # ... in fact, maybe a landing page isn't a good idea...
        # assistant_image = f"{ASSETS_PATH}/assistant2sm.png"
        # st.image(assistant_image)

    # loginform_placeholder = st.empty()

    # if st.button("Login to PlebChat"):
    # import time
    # time.sleep(0.02) # This runs EVERY action/st.rerun().. dont' use.
    # print("SLEEPING!!!")
    with st.expander("Login to plebchat", expanded=False):
        # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
        # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
        st.session_state.authenticator.login(location="main", max_concurrent_users=1, fields={
            "Form name": "PlebChat login",
            "Username": "Username",
            "Password": "Password",
            "Login": "Enter ye!",
        })

    if st.session_state["authentication_status"]:
        landing_page_container.empty()

        if st.session_state.username == 'root':
            root_panel()
        else:
            init_if_needed()
            main_page()
