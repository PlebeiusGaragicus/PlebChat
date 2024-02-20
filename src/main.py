import os

import streamlit as st
from streamlit_pills import pills

from mistralai.models.chat_completion import ChatMessage
from mistralai.exceptions import MistralAPIException

# from streamlit_option_menu import option_menu

import logging
log = logging.getLogger(__file__)


from src.VERSION import VERSION
from src.common import (
    ASSETS_PATH,
    ChatAppVars,
    is_init,
    not_init,
    get,
    set,
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

from src.persist import load_persistance, update_persistance





def init_if_needed():
    st.session_state.runlog_dir = os.path.join(os.getcwd(), "runlog", st.session_state.username)

    # initialize the appstate on first run
    if not_init('appstate'):
        try:
            st.session_state['appstate']: ChatAppVars = ChatAppVars()
        except Exception as e:
            st.error(e)
            st.exception(e)
            st.stop()


    if not_init('speak_this'):
        set('speak_this', None)




def load_proper_flow(construct):
    if is_init("construct"):
        st.write(f"Construct loaded is: {get('construct').name}...")

        if get('construct').name != construct:
            update_persistance('chosen_pill', construct)
            st.write("CONSTRUCT CHANGE!")
        else:
            st.write("no change!")
            return

    print("load_proper_flow() - building contruct")

    # ["echobot", "Mistral", "GPT"] # TODO
    if construct == 'echobot':
        st.write("init echobot construct")
        from src.flows import echobot
        st.session_state["construct"] = echobot()
        st.rerun()
    elif construct == 'tommybot':
        from src.flows import tommybot
        st.session_state["construct"] = tommybot()
        st.rerun()
        # raise Exception("not yet made")
    elif construct == "dummybot":
        from src.flows import dummybot
        st.session_state["construct"] = dummybot()
        st.rerun()
        # raise Exception("not yet made")
    else:
        raise Exception("wtf how? - fix this!")

    st.write(f"Construct loaded is: {get('construct').name}...")



def main_page():
    load_persistance()
    print("\n\n\nRERUN!!!!!!\n")
    appstate = st.session_state.appstate
    column_fix()

    load_settings()


    CONSTRUCTS = ["echobot", "tommybot", "dummybot"]

    construct = pills(label="AI Construct",
                      options=CONSTRUCTS,
                      icons=["🤖", "🤖", "🤖"],
                      index=CONSTRUCTS.index(get("persistance")['chosen_pill'])
                )
    st.caption(f"Using: `{construct}`")

    # check_change = st.session_state.get("construct", None)
    # if check_change is not None or check_change.name != st.session_state.get("construct").name:
    load_proper_flow(construct)




    ### INPUT BUTTONS
    with st.sidebar:
        top_buttons = st.columns((1, 1))
        with top_buttons[0]:
            st.toggle("🗣️🤖", key="speech_input", value=False)
        with top_buttons[1]:
            st.toggle("🤖💬", key="read_to_me", value=False)
        # with top_buttons[2]:
        #     st.empty()
        # if len(appstate.chat.messages) > 0:
            # st.button("🗑️ Delete", on_click=delete_this_chat, key="button_delete", use_container_width=True)

    construct_settings_placeholder = st.sidebar.empty()


    ### RAINBOW DIVIDER
    st.header("", divider="rainbow")
    # st.caption(f"Using: `{st.session_state.model.name}`")


    st.write(get("construct").preamble)
    st.write(get("construct").settings)

    human_avatar = f"{ASSETS_PATH}/human_avatar.png"
    ai_avatar = f"{ASSETS_PATH}/assistant_avatar.png"

    ####### CONVERSATION #######
    for message in appstate.chat.messages:
        with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
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

    if not get("speech_input"):
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
            reply = run_prompt(prompt, bots_reply_placeholder)

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
        # with st.expander("Past Conversations", expanded=False):
        st.header("", divider="rainbow")
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
        
        # with st.expander("API Keys"):
        #     st.write("here")
        
        # with st.expander("Construct settings", expanded=True):
        #     get('construct').display_settings()

    with construct_settings_placeholder.expander("Construct settings", expanded=False):
            get('construct').display_settings()

    settings_placeholder = st.sidebar.empty()

    with settings_placeholder.expander("Settings"):#,
        with st.container(border=True):
            settings_llm()
        with st.container(border=True):
            settings_stt()
        with st.container(border=True):
            settings_tts()



    ### THE AUDIO PLAYER FOR TTS
    if st.session_state.speak_this is not None:
        # on reload, if `speak_this` is set, then we speak it
        TTS(st.session_state.speak_this)
        st.session_state.speak_this = None






# # async def run_prompt(prompt, bots_reply_placeholder):
# def run_prompt(prompt, bots_reply_placeholder):
#     with bots_reply_placeholder.chat_message("assistant"):
#         st.session_state.incomplete_stream = ""
#         place_holder = st.empty()




#         reply = st.session_state.incomplete_stream
#         st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
#         return reply








def run_prompt(prompt, bots_reply_placeholder):
    with bots_reply_placeholder.chat_message("assistant"):
        st.session_state.incomplete_stream = ""
        place_holder = st.empty()


        if get("construct").agentic:
            st.write("not yet supported")
        else:
            for chunk in get('construct').run(prompt):
                st.session_state.incomplete_stream += chunk
                place_holder.markdown(st.session_state.incomplete_stream)

        reply = st.session_state.incomplete_stream
        st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
        return reply
