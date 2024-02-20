import os
import json

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
    # ChatAppVars,
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
    # settings_llm,
    settings_stt,
    settings_tts,
    settings_bottom_buttons,
    save_user_preferences,
    # init_model,
)

from src.user_preferences import (
    load_settings,
)

from src.interface.interface import (
    column_fix,
    center_text,
    centered_button_trick,
    # interrupt,
)

from src.sats import load_sats_balance

from src.speech import TTS

from src.persist import load_persistance, update_persistance

from src.flows import ChatThread



class ChatAppVars:
    def __init__(self):
        self.chat = ChatThread()

        self.chat_history_depth = 20
        self.chat_history = None # the list of past conversations list of (description, runlog file name)
        self.load_chat_history()


    def new_thread(self):
        self.chat = ChatThread()

    def increase_chat_history_depth(self):
        self.chat_history_depth += 20
        self.load_chat_history()

    def load_chat_history(self):
        # make sure the runlog directory exists
        os.makedirs(st.session_state.runlog_dir, exist_ok=True)

        self.chat_history = []
        runlogs = os.listdir(st.session_state.runlog_dir)
        runlogs.sort(reverse=True)
        self.truncated = len(runlogs) > self.chat_history_depth
        if self.truncated:
            runlogs = runlogs[:self.chat_history_depth]
        for runlog in runlogs:
            with open(os.path.join(st.session_state.runlog_dir, runlog), "r") as f:
                try:
                    file_contents = json.load(f)
                    description = file_contents["description"]
                except json.decoder.JSONDecodeError:
                    # file load error - skip this file
                    continue
            self.chat_history.append((description, runlog))





def init_if_needed():
    st.session_state.runlog_dir = os.path.join(os.getcwd(), "runlog", st.session_state.username)

    # initialize the appstate on first run
    if not_init('appstate'):
        try:
            st.session_state.appstate: ChatAppVars = ChatAppVars()
            # st.session_state['appstate'] = ChatAppVars()
            # st.session_state.appstate.
        except Exception as e:
            st.error(e)
            st.exception(e)
            st.stop()


    if not_init('speak_this'):
        set('speak_this', None)

# TODO
# CONSTRUCTS = ["echobot", "tommybot", "dummybot", "tavily"]
from src.flows.constructs import ALL_CONSTRUCTS


def load_proper_flow(construct):
    if is_init("construct"):
        # st.write(f"Construct loaded is: {get('construct').name}...")

        if get('construct').name != construct:
            # update_persistance('chosen_pill', construct)
            # update_persistance('chosen_pill', CONSTRUCTS.index(construct))
            update_persistance('chosen_pill', [c.name for c in ALL_CONSTRUCTS].index(construct))
            # update_persistance('chosen_pill', [c.name for c in ALL_CONSTRUCTS].index(construct))
            # st.write("CONSTRUCT CHANGE!")
            st.session_state.appstate.new_thread()
        else:
            # st.write("no change!")
            return

    print("load_proper_flow() - building contruct")

    # Use ALL_CONSTRUCTS to dynamically instantiate the correct construct
    for Construct in ALL_CONSTRUCTS:
        if Construct.name == construct:
            st.session_state["construct"] = Construct()
            st.rerun() # we need this to reload the page with the new construct
    else:
        raise Exception(f"Unknown construct: {construct} - fix this!")



# debug_placeholder = None


# def debug():
#     return debug_placeholder



def main_page(authenticator):
    load_persistance()
    print("\n\n\nRERUN!!!!!!\n")
    appstate = st.session_state.appstate
    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever
    

    load_settings()


    construct_names = [c.name for c in ALL_CONSTRUCTS]
    construct_icons = [c.emoji for c in ALL_CONSTRUCTS]
    pill_index = get("persistance")['chosen_pill']
    construct = pills(label="AI Construct",
                    options=construct_names,
                    #   icons=["🤖", "🤖", "🤖", "🕸️"],
                    icons=construct_icons,
                    #   index=CONSTRUCTS.index(get("persistance")['chosen_pill'])
                    index=pill_index
                )

    load_proper_flow(construct)
    
    cols2 = st.columns((1, 1, 1))
    with cols2[0]:
        st.toggle("🗣️🤖", key="speech_input", value=False)
        if get('speech_input') is True:
            st.toggle(
                label="Confirm stt",
                key="confirm_stt",
                value=st.session_state.user_preferences["confirm_stt"],
                on_change=save_user_preferences,
                kwargs={"toggle_key": "confirm_stt"},)

    with cols2[1]:
        st.toggle("🤖💬", key="read_to_me", value=False)


    # cols2 = st.columns((1, 1, 1))
    # with cols2[0]:
    #     st.toggle("🗣️🤖", key="speech_input", value=False)
    # if get('speech_input') is True:
    #     with cols2[1]:
    #         confirm_stt = st.session_state.user_preferences["confirm_stt"]
    #         st.toggle(
    #             label="Confirm stt",
    #             key="confirm_stt",
    #             value=confirm_stt,
    #             on_change=save_user_preferences,
    #             kwargs={"toggle_key": "confirm_stt"},
    #         )



    ### INPUT BUTTONS
    # with st.sidebar:
    #     top_buttons = st.columns((1, 1))
    #     with top_buttons[0]:
    #     #     st.toggle("🗣️🤖", key="speech_input", value=False)
    #         sats = load_sats_balance()
    #         # bitcoin_symbol = "₿"
    #         st.write(f":orange[₿]: `{sats:,.0f}` sats")
    #     with top_buttons[1]:
    #         st.toggle("🤖💬", key="read_to_me", value=False)



    ################### TOP OF SIDEBAR ###################
    sats_display()

    # construct_settings_placeholder = st.sidebar.empty()
    with st.sidebar.expander("Construct settings", expanded=True):
            get('construct').display_settings()



    ### RAINBOW DIVIDER
    st.header("", divider="rainbow")


    if os.getenv("DEBUG", False):
        with st.expander("Debug", expanded=False):
            debug_placeholder = st.container()
            debug_placeholder.write(get("construct"))
            # debug_placeholder.write(get("construct").preamble)
            # debug_placeholder.write(get("construct").settings)
            debug_placeholder.write(st.session_state.appstate.chat.messages)

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
        

        def interrupt():
            """ callback for the interrupt button """
            st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
            st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))

            if save_chat_history():
                st.session_state.appstate.load_chat_history()

        interrupt_button_placeholder.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
        st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )
        # with bots_reply_placeholder.chat_message("assistant"):
        if get("construct").agentic:
            # bots_reply_placeholder.container()
            init_graph(prompt, bots_reply_placeholder)
        else:
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
        if len(appstate.chat_history) == 0:
            st.caption("No past conversations... yet")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        if appstate.truncated:
            st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
            st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        # st.write("---")
        st.header("", divider="rainbow")

        # sats_display()


        # settings_placeholder = st.sidebar.empty()
        # with settings_placeholder.expander("Settings"):#,
        with st.expander("Settings"):#,
            # with st.container(border=True):
            #     settings_llm()
            with st.container(border=True):
                settings_stt()
            with st.container(border=True):
                settings_tts()


        # logoutcols = st.columns((1, 1))
        # with logoutcols[0]:
        authenticator.logout(f":red[Logout] `{st.session_state.username}`")
            # authenticator.logout(f":red[Logout]")
        # with logoutcols[1]:
            # st.caption(f"user:`{get('username')}`")

        # st.session_state.authenticator.logout(f"Logout `{st.session_state.username}`", "main")
        st.caption(f"running version `{VERSION}`")
        if os.getenv("DEBUG", False) == False:
            st.caption("Running in production mode.")
        
        # with st.expander("API Keys"):
        #     st.write("here")
        
        # with st.expander("Construct settings", expanded=True):
        #     get('construct').display_settings()

    # TODO - fuck.. the settings expander closes every time you make an adjustment!!!
    # with construct_settings_placeholder.expander("Construct settings"):
    # with construct_settings_placeholder.expander("Construct settings", expanded=True):
    #         get('construct').display_settings()




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
    with bots_reply_placeholder.chat_message("assistant", avatar=f"{ASSETS_PATH}/assistant_avatar.png"):
        # st.session_state.incomplete_stream = ""
        # place_holder = st.empty()


        # if get("construct").agentic:
        #     for node, output in get('construct').run(prompt):
        #         st.write(f"Output from node '{node}':")
        #         st.write("---")
        #         st.write(output)
        #         # st.session_state.incomplete_stream += chunk
        #         # place_holder.markdown(st.session_state.incomplete_stream)
        # else:
        reply = st.write_stream(get('construct').run(prompt))
        # for chunk in get('construct').run(prompt):
            # st.session_state.incomplete_stream += chunk
            # place_holder.markdown(st.session_state.incomplete_stream)
            # st.write_stream(chunk)

        # reply = st.session_state.incomplete_stream
        st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
        return reply




def init_graph(prompt, bots_reply_placeholder):
    bots_reply_placeholder.container()


    for node, output in get('construct').run(prompt):
        st.write(f"Output from node '{node}':")
        st.write("---")
        st.write(output)
        # st.session_state.incomplete_stream += chunk
        # place_holder.markdown(st.session_state.incomplete_stream)




def sats_display():
    with st.sidebar:
        sats_cols = st.columns((1, 1))
        with sats_cols[0]:
            # st.button("🔁 Refresh", on_click=load_sats_balance, key="refresh_sats", use_container_width=True)
            # st.button("❇️ :green[add sats]", key="add_sats", use_container_width=True)
            st.button("⚡️ :green[add sats] ⚡️", key="add_sats", use_container_width=True)
        with sats_cols[1]:
            sats = load_sats_balance()
            st.write(f":orange[₿] `{sats:,.0f}` sats")
