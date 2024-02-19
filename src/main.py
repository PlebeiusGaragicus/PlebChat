import os

import streamlit as st

from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException

from streamlit_option_menu import option_menu

import logging
log = logging.getLogger(__file__)


from src.VERSION import VERSION
from src.common import (
    ASSETS_PATH,
    ChatAppVars,
)

from src.chat_history import (
    save_chat_history,
    load_convo,
    delete_this_chat,
)

from src.settings import (
    settings_llm,
    settings_stt,
    settings_tts,
    settings_bottom_buttons,
    init_model,
)

from src.user_preferences import (
    load_settings,
)

from src.interface.interface import (
    column_fix,
    center_text,
    centered_button_trick,
    interrupt,
)

from src.speech import TTS





def init_if_needed():
    st.session_state.runlog_dir = os.path.join(os.getcwd(), "runlog", st.session_state.username)

    # initialize the appstate on first run
    if 'appstate' not in st.session_state:
        try:
            st.session_state['appstate']: ChatAppVars = ChatAppVars()
        except Exception as e:
            st.error(e)
            st.exception(e)
            st.stop()


    if 'speak_this' not in st.session_state:
        st.session_state.speak_this = None



def main_page():
    appstate = st.session_state.appstate

    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever

    load_settings()

    ### SETTINGS EXPANDER
    if st.session_state.user_preferences["settings_on_sidebar"]:
        settings_placeholder = st.sidebar.empty()
    else:
        settings_placeholder = st.empty()

    with settings_placeholder.expander("Settings"):#,
                                       # expand the settings expander if the settings are on the sidebar
                                    #    expanded=st.session_state.user_preferences["settings_on_sidebar"]):
        with st.container(border=True):
            settings_llm()
        with st.container(border=True):
            settings_stt()
        with st.container(border=True):
            settings_tts()

        # settings_bottom_buttons()

    init_model()



    with centered_button_trick():
        from src.settings import TTS_OPTIONS, save_user_preferences
        flows = ["flow 1", "flow 2"]
        # selected_tts = tts_options.index(st.session_state.user_preferences["tts"])
        st.selectbox(
            label="🦜⛓",
            options=flows,
            # index=selected_tts,
            key="flow",
            # on_change=save_user_preferences,
            # kwargs={"update_key": "language_model"},
        )
    
    load_proper_flow()


    ### INPUT BUTTONS
    top_buttons = st.columns((1, 1, 1))
    with top_buttons[0]:
        st.toggle("🗣️🤖", key="speech_input", value=False)
    with top_buttons[1]:
        st.toggle("🤖💬", key="read_to_me", value=False)
    with top_buttons[2]:
        st.empty()
        # if len(appstate.chat.messages) > 0:
            # st.button("🗑️ Delete", on_click=delete_this_chat, key="button_delete", use_container_width=True)

    ### RAINBOW DIVIDER
    st.header("", divider="rainbow")
    # st.caption(f"Using: `{st.session_state.model.name}`")



    ####### CONVERSATION #######
    for message in appstate.chat.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # This is so that we can later populate with the users' next prompt
    # and the bots reply and allows the input field (or start recording button)
    # to be at the bottom of the page
    my_next_prompt_placeholder = st.empty()
    interrupt_button_placeholder = st.empty()
    bots_reply_placeholder = st.empty()
    before_speech_placeholder = st.empty()

    if len(appstate.chat.messages) > 0:
        st.header("", divider="rainbow")


    #### USER PROMPT AND ASSOCIATED LOGIC
    prompt = None
    if 'speech_draft' not in st.session_state:
        st.session_state.speech_draft = None
        st.session_state.speech_confirmed = False

    if not st.session_state.get("speech_input", False):
        prompt = st.chat_input("Ask a question.")
    else:
        # TODO - naive thinking that let me to think having us import here would increase page performance... lol, oh well
        from streamlit_mic_recorder import speech_to_text

        with centered_button_trick():
            # https://pypi.org/project/SpeechRecognition/
            speech_draft = speech_to_text(
                            start_prompt="🎤 Speak",
                            stop_prompt="🛑 Stop",
                            language='en',
                            use_container_width=True,
                            just_once=True,
                            key='STT'
                    )
        if st.session_state.confirm_stt is False:
            prompt = speech_draft
            speech_draft = None

        if speech_draft:
            with st.container(border=True):

                st.text_area("You said:", value=speech_draft, key="speech_draft_edit")

                def user_confirms_speech():
                    st.session_state.speech_confirmed = True
                    st.session_state.speech_draft = st.session_state.speech_draft_edit

                def user_cancels_speech():
                    st.session_state.speech_confirmed = False
                    st.session_state.speech_draft = None

                confirms = st.columns((2, 1, 1))
                confirms[0].button("✅", on_click=user_confirms_speech, use_container_width=True)
                confirms[2].button("❌", on_click=user_cancels_speech, use_container_width=True)




    if st.session_state.speech_confirmed:
        prompt = st.session_state.speech_draft
        st.session_state.speech_draft = None

    if prompt:
        st.session_state.speech_confirmed = False
        interrupt_button_placeholder.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt_placeholder.chat_message("user").markdown(prompt)
        st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )
        # with bots_reply_placeholder.chat_message("assistant"):
        with st.spinner("🧠 Thinking..."):
            import asyncio
            reply = asyncio.run(run_prompt(prompt, bots_reply_placeholder))

        new_chat = save_chat_history() # dummy variable for readability
        if new_chat:
            # A new chat thread has just been created, so we must update our list of past conversations
            appstate.load_chat_history()

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:
            st.session_state.speak_this = reply

        st.rerun() # we rerun the page for a reason that I forgot...
    #### AFTER-PROMPT PROCESSING ####
    # put things here to update the UI _AFTER_ the prompt has been run


    ### READ IT AND NEW BUTTONS
    with before_speech_placeholder:
        if len(appstate.chat.messages) > 0:
            # if last message was from the bot, then we can read it aloud
            col2 = st.columns((1, 1, 1))
            col2[2].button("🌱 New", on_click=lambda: appstate.new_thread(), use_container_width=True)
            col2[1].button("🗑️ Delete", on_click=delete_this_chat, key="button_delete", use_container_width=True)
            if appstate.chat.messages[-1].role == "assistant":
                # centered_button_trick().button("🗣️ Speak", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)
                if st.session_state.read_to_me is False:
                    def on_click_read_to_me():
                        st.session_state.speak_this = appstate.chat.messages[-1].content
                    col2[0].button("🗣️ read it", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)



    ### SIDEBAR WITH CONVERSATION HISTORY
    with st.sidebar:
        if len(appstate.chat.messages) > 0:
            sidebar_new_button_placeholder = st.columns((1, 1))
            sidebar_new_button_placeholder[0].button("🗑️ Delete", on_click=delete_this_chat, key="delbutton2", use_container_width=True)
            sidebar_new_button_placeholder[1].button("🌱 New", on_click=lambda: appstate.new_thread(), use_container_width=True, key="newbutton2")
        st.write("## Past Conversations")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        if appstate.truncated:
            st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
            st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        st.write("---")
        st.session_state.authenticator.logout(f"Logout `{st.session_state.username}`", "main")
        st.caption(f"running version `{VERSION}`")
        if os.getenv("DEBUG", False) == False:
            st.caption("Running in production mode.")


    ### THE AUDIO PLAYER FOR TTS
    if st.session_state.speak_this is not None:
        # on reload, if `speak_this` is set, then we speak it
        TTS(st.session_state.speak_this)
        st.session_state.speak_this = None



def load_proper_flow():
    if st.session_state.flow is None:
        raise ValueError("Flow is not set - how the fuck did this happen?")

    if st.session_state.flow == "flow 1":
        from src.flows.simple import compiled_graph
        st.session_state.graph = compiled_graph()

def init_flow():
    pass





async def run_prompt(prompt, bots_reply_placeholder):
    with bots_reply_placeholder.chat_message("assistant"):
        st.session_state.incomplete_stream = ""
        place_holder = st.empty()

        # if st.session_state.flow is None:
        #     init_flow()



        from langchain_core.messages import HumanMessage
        inputs = {"messages": [HumanMessage(content=prompt)]}

        async for output in st.session_state.graph.astream_log(inputs, include_types=["llm"]):
            # astream_log() yields the requested logs (here LLMs) in JSONPatch format
            for op in output.ops:
                print(op)
                continue

                if op["path"] == "/streamed_output/-":
                    # this is the output from .stream()
                    # print(op["value"])
                    print(op['value'])
                    # st.session_state.incomplete_stream += op["value"]
                    # place_holder.markdown(st.session_state.incomplete_stream)

                elif op["path"].startswith("/logs/") and op["path"].endswith("/streamed_output/-"):
                    # because we chose to only include LLMs, these are LLM tokens
                    print("STREAMING LLM TOKENS!!!!!!!!")
                    print(op["value"])
                    # st.session_state.incomplete_stream += op["value"]
                    # place_holder.markdown(st.session_state.incomplete_stream)

        # from langchain_core.messages import HumanMessage
        # inputs = {"messages": [HumanMessage(content=prompt)]}
        # for output in st.session_state.graph.stream(inputs):
        #     # stream() yields dictionaries with output keyed by node name
        #     for key, value in output.items():
        #         st.session_state.incomplete_stream = f"{key}: {value}"
        #         place_holder.markdown(st.session_state.incomplete_stream)
        #         # st.write(f"{key}: {value}")
        #         print(f"Output from node '{key}':")
        #         print(value)

        # try:
        #     client = st.session_state.model.get_client()
        # except Exception as e:
        #     st.error(e)
        #     st.exception(e)
        #     st.stop()

        # for chunk in st.session_state.model.get_streamed_tokens(client):
            # st.session_state.incomplete_stream += chunk
            # place_holder.markdown(st.session_state.incomplete_stream)

        reply = st.session_state.incomplete_stream
        st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
        return reply








# def run_prompt(prompt, bots_reply_placeholder):
#     with bots_reply_placeholder.chat_message("assistant"):
#         st.session_state.incomplete_stream = ""
#         place_holder = st.empty()


#         try:
#             client = st.session_state.model.get_client()
#         except Exception as e:
#             st.error(e)
#             st.exception(e)
#             st.stop()

#         # for chunk in client:
#         for chunk in st.session_state.model.get_streamed_tokens(client):
#             st.session_state.incomplete_stream += chunk
#             place_holder.markdown(st.session_state.incomplete_stream)

#         reply = st.session_state.incomplete_stream
#         st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
#         return reply
