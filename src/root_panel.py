import os
import json
import yaml
import streamlit as st

from src.chat_history import (
    deserialize_messages
)

# from src.interface import centered_button_trick

# Streamlit-Authenticator, Part 2: Adding advanced features to your authentication component
# https://blog.streamlit.io/streamlit-authenticator-part-2-adding-advanced-features-to-your-authentication-component/



def root_panel():
    # with centered_button_trick():
    # st.write("# 🌲 I am groot!")
    st.write("# 🤴🏻 ROOT PANEL")
    st.session_state.authenticator.logout(f"Logout `{st.session_state.username}`", "main")
    st.header("", divider="rainbow")

    if 'toast_message' in st.session_state:
        st.toast(st.session_state.toast_message)


    with open("./auth.yaml") as file:
        config = yaml.safe_load(file)

    list_of_usernames = config['credentials']['usernames']
    st.write("""## Authorized users""")
    with st.container(border=True, height=400):
        st.write(list_of_usernames)

    ### CREATE USER
    with st.form("new_user_form", clear_on_submit=True, border=True):
        st.write("## Create user")

        st.text_input("Username", key="new_username")
        st.text_input("Password", key="new_password")

        if st.form_submit_button("🐣 CREATE USER"):
            if st.session_state.new_username in [None, ""] or \
                st.session_state.new_password in [None, ""]:
                    st.error("Enter a username and password")
            else:
                 create_new_user(list_of_usernames=list_of_usernames,
                                 username=st.session_state.new_username,
                                 password=st.session_state.new_password)

    ### DELETE USER
    with st.form("delete_user", clear_on_submit=True, border=True):
        st.write("## Delete user")
        st.selectbox("Username", options=list_of_usernames, key="user_to_delete", index=None)

        if st.form_submit_button(f"💥 DELETE USER"):
                if st.session_state.user_to_delete is None:
                    st.error("Select a user to delete from the dropdown.")
                else:
                    delete_user(st.session_state.user_to_delete)

    ### READ USER CHATS
    # with st.form("read_user_chats", clear_on_submit=True, border=True):
    #     st.write("## Read user's chat history")
    #     st.selectbox("Username", options=list_of_usernames, key="user_to_snoop", index=None)

    #     if st.form_submit_button(f"🤓 Load user's chats"):
    #         load_user_chat_history(st.session_state.user_to_snoop)
    read_user_chats_form = st.form("read_user_chats", clear_on_submit=True, border=True)
    read_user_chats_form.write("## Read user's chat history")
    read_user_chats_form.selectbox("Username", options=list_of_usernames, key="user_to_snoop", index=None)

    if read_user_chats_form.form_submit_button(f"🤓 Load user's chats"):
        if st.session_state.user_to_snoop is None:
            st.error("Must select a user")
        else:
            load_user_chat_history(st.session_state.user_to_snoop)



def create_new_user(list_of_usernames, username: str, password: str):
    # check if username is unique
    if username in list_of_usernames:
         st.error(f"User: `{username}` already exists")
         return
    
    import streamlit_authenticator as stauth
    password_hash = stauth.Hasher([password]).generate()[0]

    with open("./auth.yaml") as file:
        config = yaml.safe_load(file)

    # add user to list and save to file
    config['credentials']['usernames'][username] = {'password': password_hash}

    with open("./auth.yaml", 'w') as file:
        yaml.dump(config, file)
    
    st.session_state.toast_message = f"created user: `{username}`"
    st.rerun()



def delete_user(username: str):

    with open("./auth.yaml") as file:
        config = yaml.safe_load(file)

    # remove 'username' from config
    del config['credentials']['usernames'][username]

    with open("./auth.yaml", 'w') as file:
        yaml.dump(config, file)

    st.session_state.toast_message = f"deleting user: `{username}`"
    st.rerun()




def load_user_chat_history(username: str):
    if username in [None, ""]:
        st.session_state.toast_message = "Select a user"
        st.rerun()
        return

    runlog_dir = os.path.join(os.getcwd(), "runlog", username)
    st.write(f"`{runlog_dir}`")
    # os.makedirs(runlog_dir, exist_ok=True)

    chat_history = []
    runlogs = os.listdir(runlog_dir)
    runlogs.sort(reverse=True)
    # truncated = len(runlogs) > chat_history_depth
    # if truncated:
    #     runlogs = runlogs[:self.chat_history_depth]
    for runlog in runlogs:
        with open(os.path.join(runlog_dir, runlog), "r") as f:
            try:
                file_contents = json.load(f)
                description = file_contents["description"]
            except json.decoder.JSONDecodeError:
                # file load error - skip this file
                continue
        chat_history.append((description, runlog))

    with st.container(border=True):
        for ch in chat_history:
            with st.expander(ch[0], expanded=False):
                load_user_chat(runlog_dir=runlog_dir, chat_filename=ch[1])
                # st.button(f"Load `{ch[1]}`", on_click=load_user_chat, args=(runlog_dir, ch[1],))

        # for ch in chat_history:
        #     # st.write(description, runlog)
        #     st.button(f"Chat: {ch[0]}")


def load_user_chat(runlog_dir, chat_filename):
    with open(os.path.join(runlog_dir, chat_filename), "r") as f:
        file_contents = f.read()

    """ Load a previous conversation from a runlog file"""

    # load the runlog file
    # os.path.join(os.getcwd(), "runlog", st.session_state.username)
    with open(os.path.join(runlog_dir, chat_filename), "r") as f:
        file_contents = json.load(f)

        messages = file_contents["messages"]
        messages = [deserialize_messages(m) for m in messages]

        for message in messages:
            with st.chat_message(message.role):
                st.markdown(message.content)
