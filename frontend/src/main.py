import os
import enum
import requests
from PIL import Image
import json
# from pathlib import Path
# import base64
from functools import partial
from pydantic import BaseModel, Field
from enum import Enum

import streamlit as st
import streamlit_pydantic as sp
# https://st-pydantic.streamlit.app

# import ollama
from ollama import Client

models = Client("http://host.docker.internal:11434").list()

print(type(models))
print(models.__dict__['models'])

for m in models.__dict__['models']:
    print(m.__dict__.keys())


# MATERIAL SYMBOLS
# https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded


## TODO: get markdown to show local images
# https://discuss.streamlit.io/t/local-image-button/5409/6
#######################################################################################################################







#######################################################################################################################

from src.config import APP_NAME, LANGSERVE_ENDPOINT, PORT, STATIC_PATH
from src.interface import Colors, cprint, center_text, hide_markdown_header_links, hide_stop_button, mobile_column_fix
from src.login import login
from src.agents import AGENTS, get_agent_by_endpoint


AVATAR_HUMAN = f"{STATIC_PATH}/user2.png"
AVATAR_AI = f"{STATIC_PATH}/assistant.png"

HOME_SCREEN_TEXT = """
## Welcome to :rainbow[PlebChat!]

This is a collection of my __self-hosted__ machine learning tools.

Please login with your username and password to continue.
"""


# @st.cache_data
# def img_to_bytes(img_path):
#     img_bytes = Path(img_path).read_bytes()
#     encoded_img = base64.b64encode(img_bytes).decode()
#     # print(encoded_img)
#     return encoded_img



class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content




def new_thread():
    st.session_state.messages = []



# def edit_message():
#     """Remove the last user and assistant messages and set the placeholder to the last user message."""
#     if len(st.session_state.messages) >= 2:
#         # Get the last user message before removing it
#         last_user_message = st.session_state.messages[-2]["content"]
#         # Remove last assistant and user messages
#         st.session_state.messages = st.session_state.messages[:-2]
#         # Set the placeholder to the last user message
#         # st.session_state.placeholder = last_user_message
#         # st.session_state.query = last_user_message



################################################################################################
def cmp_options():
    # with st.popover("", icon=":material/menu:"):
    icon_color = "orange"
    # icon = f":{icon_color}[:material/smart_toy:]"
    icon = f":{icon_color}[:material/smart_toy:] :rainbow[PlebChat]"

    # with st.popover("", icon=icon):
    with st.popover(icon):
        # st.markdown("### :grey[:material/settings:] :rainbow[Intellence Settings]")
        # st.markdown("### :grey[:material/settings:] :rainbow[Intelligent Agents]")

        # with st.container(height=200, border=False):
        # with st.container(height=150):
        # with st.container(border=False):
        # st.markdown("### :grey[Select Agent]")
        st.radio(
            "Choose your Agent",
            [agent_class().endpoint for agent_class in AGENTS],
            horizontal=True,
            index=0,
            key="model",
            format_func=lambda x: get_agent_by_endpoint(x).display_name,
            on_change=new_thread,
            label_visibility="collapsed"
        )

        st.session_state.selected_agent = get_agent_by_endpoint(st.session_state.model)
        # with st.expander(":grey[:material/settings: Configure]", expanded=False):
        with st.container(border=True):

            if st.session_state.selected_agent.Config == None:
                st.write("No configuration required for this agent")
                st.session_state.config = {}
                st.header("No config")
                return

            if data := sp.pydantic_input(key=f"config_{st.session_state.selected_agent.endpoint}", model=st.session_state.selected_agent.Config):
                # st.session_state[f"config_{current_agent.endpoint}"] = data

                st.session_state.config = data

                # st.write(data)
                st.divider()
                st.write( st.session_state.config )
################################################################################################






################################################################################################
def main_page():
    if os.getenv("DEBUG", None): # should be the only time we call this
        st.session_state.debug = True
    else:
        st.session_state.debug = False

    ip_addr = st.context.headers.get('X-Forwarded-For', "?")
    user_agent = st.context.headers.get('User-Agent', "?")
    lang = st.context.headers.get('Accept-Language', "?")
    cprint(f"RUNNING for: {ip_addr} - {lang} - {user_agent}", Colors.YELLOW)


    #### PAGE SETUP
    favicon = Image.open(os.path.join(STATIC_PATH, "favicon.ico"))
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=favicon,
        layout="wide",
        # initial_sidebar_state="auto",
        initial_sidebar_state="expanded" if st.session_state.debug else "collapsed",
    )

    mobile_column_fix()
    hide_markdown_header_links()

    # hide_stop_button()
    if not st.session_state.debug:
        hide_stop_button()


############################################
    if not login():
        with st.container(border=True):
            cols2 = st.columns(2)
        with cols2[1]:
            st.markdown("![PlebChat](app/static/assistant_big_nobg.png)")
        with cols2[0]:
            st.markdown(HOME_SCREEN_TEXT)

        st.stop()
############################################


    # center_text("p", "🗣️🤖💬", size=60)
    # cmp_options()

    header_placeholder = st.empty()
    cmp_options()
    with header_placeholder:
        st.header("" + get_agent_by_endpoint(st.session_state.model).display_name, divider="rainbow")

        # image_base64 = img_to_bytes(MICROSOFT)
        # html = f"""<div style="display: flex; align-items: center;">
        #     <img src='data:image/png;base64,{image_base64}' style="height: 32px; margin-right: 10px;">
        #     <h1 style="margin: 0;">{format_agents(st.session_state.model)}</h2>
        # </div>"""
        # st.markdown(html, unsafe_allow_html=True)
        # st.divider()
        # st.header("" + format_agents(st.session_state.model), divider="rainbow")






########################################################################################################
    if "messages" not in st.session_state:
        st.session_state.messages = []

        ## FIRST RUN TOAST BANNER
        # st.toast(":rainbow[Welcome to PlebChat!]", icon=":material/smart_toy:")
        # st.toast("#### :rainbow[Welcome to PlebChat!]")

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=AVATAR_HUMAN if message["role"] == "user" else AVATAR_AI):
            st.markdown(message["content"])


    # if st.session_state.get("placeholder", None) is None:
    #     st.session_state.placeholder = "What do you want to learn?"

    placeholder = st.session_state.selected_agent.placeholder

    if prompt := st.chat_input(placeholder=placeholder, key="query"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_HUMAN):
            st.markdown(prompt)


        with st.chat_message("assistant", avatar=AVATAR_AI):
        # with st.empty():
            try:
                response = requests.post(
                    url=f"{LANGSERVE_ENDPOINT}:{PORT}/{st.session_state.model}",
                    json={
                        "user_message": prompt,
                        "messages": st.session_state.messages,
                        "body": {}, #TODO user_id
                    },
                    stream=True,
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                message_placeholder = st.empty()
                full_response = ""

                # Create a status container
                # with st.status("🧠 Agent at work...", expanded=True) as status:
                # status_updater = st.empty()
                # status_updater.status("🧠 Agent at work...", expanded=True)

                current_node = None

                # with st.spinner("🧠 Thinking"):
                with st.status("🧠 Agent at work...", expanded=True) as status:
                    try:
                        for line in response.iter_lines():
                            if line:
                                # decode the SSE into a proper JSON object
                                line = line.decode()
                                line = line[6:]
                                line = line.replace('\\n', '\n')

                                try:
                                    j = json.loads(line)

                                except json.JSONDecodeError as e:
                                    print(f"Error decoding JSON: {e}")
                                    print(line)
                                    continue



                                ###### TAGS
                                tags = j.get('tags', None)
                                if tags:
                                    if 'langsmith:hidden' in tags:
                                        print(f" >> SKIPPING A HIDDEN UPDATE STEP for Node: {current_node}")
                                        continue


                                ###### NODE
                                try:
                                    node_name = j.get("metadata", None).get('langgraph_node', None)

                                    if node_name:
                                        if current_node != node_name:
                                            current_node = node_name
                                            status.update(label=f"{current_node}", state="running", expanded=True)

                                            # st.write("\n\n")
                                            full_response += "\n\n---\n\n"
                                            message_placeholder.markdown(full_response + "▌")

                                except:
                                    node_name = None


                                ###### DATA
                                data = j.get('data', None)
                                if data:
                                    chunk = data.get('chunk', None)

                                    if chunk:
                                        content = chunk.get('content', None)

                                        if content:
                                            full_response += content


                                print(f"{json.dumps(j, indent=4)}")


                                ###### EVENT
                                # event = j.get('event', None)
                                # if current_node != event:
                                #     current_node = event
                                #     status_name = f"{event}"

                                #     if event == "on_chat_model_stream":
                                #         status_name = "🧠 Generating response..."

                                #     # status.update(label=status_name, state="running", expanded=True)
                                #     with status:
                                #         st.write(status_name)
                                #         status.update(label=status_name, state="running", expanded=True)

                                    # match event_type:
                                    #     case 'on_chain_start':
                                    #         status.update(label="Starting chain...", state="running")
                                    #     case 'on_chat_model_start':
                                    #         status.update(label="Model thinking...", state="running")
                                    #     case 'on_llm_new_token':
                                    #         if 'data' in j and 'token' in j['data']:
                                    #             content = j['data']['token']
                                    #             full_response += content
                                    #             message_placeholder.markdown(full_response + "▌")
                                    #     case 'on_chain_end':
                                    #         status.update(label="Chain complete", state="complete")
                                    #     case _:
                                    #         # Handle other event types or unknown events
                                    #         pass

                                ###### WRITE IT OUT
                                message_placeholder.markdown(full_response + "▌")


                        # Update final status
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

                        # with status_updater as status:
                        #     status.update(label="✅ Response complete!", state="complete")

                    except (requests.exceptions.ChunkedEncodingError, requests.exceptions.RequestException) as e:
                        error_details = str(e)
                        try:
                            if hasattr(e, 'response') and e.response is not None:
                                error_json = e.response.json()
                                error_details = f"{str(e)}\nServer details: {error_json}"
                        except:
                            pass
                        st.error(f"Error while streaming response: {error_details}")
                        if not full_response:  # If we haven't received any response yet
                            message_placeholder.markdown("❌ Sorry, there was an error processing your request. Please try again.")
                        else:  # If we have partial response, show it
                            message_placeholder.markdown(full_response + "\n\n❌ *Note: Response was cut off due to an error*")
                            st.session_state.messages.append({"role": "assistant", "content": full_response})

            except requests.exceptions.RequestException as e:
                error_details = str(e)
                try:
                    if hasattr(e, 'response') and e.response is not None:
                        error_json = e.response.json()
                        error_details = f"{str(e)}\nServer details: {error_json}"
                except:
                    pass
                st.error(f"Failed to connect to the server: {error_details}")
                message_placeholder = st.empty()
                message_placeholder.markdown("❌ Sorry, there was an error connecting to the server. Please try again later.")

    if len(st.session_state.messages):
        # TODO: USE THIS WHEN WE ACTUALLY GET A FEW MORE ACTIONS
        # with st.popover("", icon=":material/construction:"):


        if st.button(":grey[:material/undo: Undo last message]", type="tertiary"):
            st.session_state.messages = st.session_state.messages[:-2]
            st.rerun()





    if st.session_state.debug:
        with st.sidebar:
            st.header("session state")
            st.write(st.session_state)
            st.header("cookies")
            st.write(st.context.cookies)
            st.header("headers")
            st.write(st.context.headers)
            st.header("secrets")
            st.write(st.secrets)

    with st.sidebar:
        st.divider()

        st.session_state.authenticator.logout(f":red[Logout] `{st.session_state.name}`")
###############################################################################################################








def run_prompt():
    pass





# THESE ARE THE KINDS GENERATED FROM OUR LANDGRAPH AGENT
# on_chat_model_start -> 
# on_chat_model_stream
# on_chat_model_end
# on_llm_start
# on_llm_stream
# on_llm_end
# on_chain_start
# on_chain_stream
# on_chain_end
# on_tool_start
# on_tool_stream
# on_tool_end
# on_retriever_start
# on_retriever_chunk
# on_retriever_end
# on_prompt_start
# on_prompt_end



# {
#     'event': 'on_chain_end',
#     'data':
#         {
#             'output':
#                 {
#                     'messages': [{'role': 'user', 'content': 'asdfasdf'}]
#                 },
#             'input':
#                 {
#                     'messages': [{'role': 'user', 'content': 'asdfasdf'}]
#                 }
#         },
#     'run_id': 'c7ef8f48-7006-4972-9987-6984ed414250',
#     'name': '_write',
#     'tags': ['seq:step:3', 'langsmith:hidden', 'langsmith:hidden'],
#     'metadata':
#         {
#             'langgraph_step': 0,
#             'langgraph_node': '__start__',
#             'langgraph_triggers': ['__start__'],
#             'langgraph_path': ('__pregel_pull', '__start__'),
#             'langgraph_checkpoint_ns': '__start__:e50a3d9d-8a95-5331-0282-fe1c1d9172e7'
#         },
#     'parent_ids': ['2ffdf17d-0b9e-49e6-8bc2-38bf974abec2', '1b0ed343-bbbc-4dcf-9ac7-5b64156c22f7']
# }
