import os
import json
import random
import math

import redis

import streamlit as st
from streamlit_pills import pills

from mistralai.models.chat_completion import ChatMessage


import logging
log = logging.getLogger(__file__)


from src.VERSION import VERSION
from src.common import (
    ASSETS_PATH,
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
)

from src.user_preferences import (
    load_settings,
)

from src.interface.interface import (
    column_fix,
    center_text,
    centered_button_trick,
)

from src.sats import (
    load_sats_balance,
    TOKENS_PER_SAT,
    display_invoice_link,
    display_invoice_pane
)

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
    
    # not sure if this should be here or in main...
    # st.session_state.sats = load_sats_balance()


    st.session_state.redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    user_sats = st.session_state.redis_conn.get(st.session_state.username)

    if user_sats is None:
        st.session_state.redis_conn.set(st.session_state.username, 0)
        st.toast("Welcome to the chat app!", icon="🎉")



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







# def main_page(authenticator):
def main_page():
    print("\n\n\nRERUN!!!!!!\n")

    load_persistance()
    load_settings()

    appstate = st.session_state.appstate



    ################### TOP OF MAIN CHAT ###################
    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever

    construct_names = [c.name for c in ALL_CONSTRUCTS]
    construct_icons = [c.emoji for c in ALL_CONSTRUCTS]
    pill_index = get("persistance")['chosen_pill']
    construct = pills(label="AI Construct",
                    options=construct_names,
                    icons=construct_icons,
                    index=pill_index
                )

    load_proper_flow(construct)
    
    cols2 = st.columns((1, 1, 1))
    with cols2[0]:
        st.toggle("🗣️🤖", key="speech_input", value=False)
        if get('speech_input') is True:
            st.toggle(
                # label="Confirm stt",
                label="✅❌",
                key="confirm_stt",
                value=st.session_state.user_preferences["confirm_stt"],
                on_change=save_user_preferences,
                kwargs={"toggle_key": "confirm_stt"},)

    with cols2[1]:
        st.toggle("🤖💬", key="read_to_me", value=False)
    
    with cols2[2]:
        show_tokens()




    if os.getenv("DEBUG", False):
        with st.expander("Debug", expanded=False):
            debug_placeholder = st.container()
            debug_placeholder.write(get("construct"))
            debug_placeholder.write(st.session_state.appstate.chat.messages)

    st.header("", divider="rainbow")


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
    cols2 = st.columns((1, 1))
    with cols2[0]:
        interrupt_button_placeholder = st.empty()
    with cols2[1]:
        sats_left_placeholder = st.empty()
    # thinking_placeholder = st.empty()
    bots_reply_placeholder = st.empty()
    before_speech_placeholder = st.empty()

    # if len(appstate.chat.messages) > 0:
    #     st.header("", divider="rainbow")






    ################### TOP OF SIDEBAR ###################
    construct_settings_placeholder = st.sidebar.empty()


    #### USER PROMPT AND ASSOCIATED LOGIC
    prompt = None
    if 'speech_draft' not in st.session_state:
        st.session_state.speech_draft = None
        st.session_state.speech_confirmed = False



    sats = load_sats_balance()
    if sats <= 0:
        st.error("You are out of tokens! Please add more to continue.")
        prompt = None
    else:
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

        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
        st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )


        if get("construct").agentic:
            # bots_reply_placeholder.container()
            init_graph(prompt, bots_reply_placeholder)
        else:
            with st.spinner("🧠 Thinking..."):
                # sats_left_placeholder = st.empty()
                reply = run_prompt(prompt, bots_reply_placeholder, sats_left_placeholder)



        #### AFTER-PROMPT PROCESSING ####
        new_chat = save_chat_history() # dummy variable for readability
        if new_chat:
            # A new chat thread has just been created, so we must update our list of past conversations
            appstate.load_chat_history()

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:
            st.session_state.speak_this = reply

        st.rerun() # we rerun the page so that TTS can be played if `read_to_me` is True





    ### READ IT AND NEW BUTTONS
    with before_speech_placeholder:
        if len(appstate.chat.messages) > 0:
            # if last message was from the bot, then we can read it aloud
            col2 = st.columns((1, 1, 1))
            col2[2].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True)
            col2[1].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="button_delete", use_container_width=True)
            if appstate.chat.messages[-1].role == "assistant":
                # centered_button_trick().button("🗣️ Speak", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)
                if st.session_state.read_to_me is False:
                    def on_click_read_to_me():
                        st.session_state.speak_this = appstate.chat.messages[-1].content
                    col2[0].button("🗣️ :blue[Speak]", on_click=on_click_read_to_me, key="button_read_to_me", use_container_width=True)








    ######################  SIDEBAR  ######################
    with st.sidebar:
        st.header("", divider="rainbow")
        st.write("## Past Conversations")

        if len(appstate.chat.messages) > 0:
            sidebar_new_button_placeholder = st.columns((1, 1))
            sidebar_new_button_placeholder[0].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="delbutton2", use_container_width=True)
            sidebar_new_button_placeholder[1].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True, key="newbutton2")
            center_text('p', "---", size=9)
        # with st.expander("Past Conversations", expanded=False):
        if len(appstate.chat_history) == 0:
            st.caption("No past conversations... yet")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        if appstate.truncated:
            st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
            st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        st.header("", divider="rainbow")

        # r = random.randint(1000, 5000)
        # st.button("⚡️ :green[add sats] ⚡️", key="add_sats", on_click=add_sats, args=(r,), use_container_width=True)
        # display_invoice_link()
        display_invoice_pane()

        with st.expander("Settings"):#,
            with st.container(border=True):
                settings_stt()
            with st.container(border=True):
                settings_tts()

            st.divider()

            # authenticator.logout(f":red[Logout] `{st.session_state.username}`")
            st.session_state.authenticator.logout(f":red[Logout] `{st.session_state.username}`")


        caption = f"Version :green[{VERSION}] | "
        if os.getenv("DEBUG", False):
            caption += ":orange[DEBUG] | "
        caption += "by PlebbyG 🧑🏻‍💻"
        st.caption(caption)


        # with st.expander("API Keys"):
        #     st.write("here")


    # we don't use an expander becuase the construct settings may need to have one
    # with construct_settings_placeholder.expander("Construct settings", expanded=True):
    with construct_settings_placeholder.container(border=False):
        st.write("## Construct configuration")
        get('construct').display_settings()




    ### THE AUDIO PLAYER FOR TTS
    if st.session_state.speak_this is not None:
        # on reload, if `speak_this` is set, then we speak it
        TTS(st.session_state.speak_this)
        st.session_state.speak_this = None













def run_prompt(prompt, bots_reply_placeholder, sats_left_placeholder):

    sats_left = load_sats_balance()
    total_cost = 0
    st.session_state.token_cost_accumulator = 0


    with bots_reply_placeholder.chat_message("assistant", avatar=f"{ASSETS_PATH}/assistant_avatar.png"):

        st.session_state.incomplete_stream = ""
        place_holder = st.empty()

        # we don't want to use write_stream because we need to keep track of the cost (and other things), as we go.
        # reply = st.write_stream(get('construct').run(prompt))
        for chunk in get('construct').run(prompt):

            tokens = len(chunk) # TODO - this is not accurate, but it's a start
            cost_for_this_chunk = tokens / TOKENS_PER_SAT # tokens charged per satoshi

            st.session_state.token_cost_accumulator += cost_for_this_chunk
            total_cost += cost_for_this_chunk
            sats_left -= cost_for_this_chunk

            if os.getenv("DEBUG", True):
                sats_left_placeholder.markdown(f"⚡️ :red[-{total_cost:,.0f}] / :green[{sats_left:,.0f}]")
            else:
                sats_left_placeholder.markdown(f":red[-{total_cost:,.0f}]")

            if st.session_state.token_cost_accumulator >= 10:
                st.session_state.redis_conn.decrby(st.session_state.username, int(st.session_state.token_cost_accumulator))
                st.session_state.token_cost_accumulator -= 10

            if sats_left < -1000:
                interrupt()

            st.session_state.incomplete_stream += chunk
            place_holder.markdown(st.session_state.incomplete_stream)

        print(sats_left)
        remaining = st.session_state.redis_conn.decrby(st.session_state.username, math.ceil(st.session_state.token_cost_accumulator))
        print(remaining)

        reply = st.session_state.incomplete_stream
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




# def sats_display():
#     with st.sidebar:
#         sats_cols = st.columns((1, 1))
#         with sats_cols[0]:
#             # st.button("🔁 Refresh", on_click=load_sats_balance, key="refresh_sats", use_container_width=True)
#             # st.button("❇️ :green[add sats]", key="add_sats", use_container_width=True)
#             r = random.randint(0, 100)
#             st.button("⚡️ :green[add sats] ⚡️", key="add_sats", on_click=add_sats, args=(r,), use_container_width=True)
#         with sats_cols[1]:
#             sats = load_sats_balance()
#             st.write(f":orange[₿] `{sats:,.0f}` sats")


def show_tokens():
    # with st.sidebar:
        # cols2 = st.columns((1, 1))
        # with cols2[0]:
    # st.text_input(label=f":orange[Tokens Available:]", value=f"{get('sats'):,.0f}", disabled=True)
        # sats = load_sats_balance()
    # st.write(f":orange[Tokens Available:]   **{get('sats'):,.0f}**")

    # st.write(f"⚡️ :green[{get('sats'):,.0f}]")

    # sats = int(st.session_state.redis_conn.get(st.session_state.username))
    sats = load_sats_balance()
    if sats is None:
        sats = 0
    st.write(f"⚡️ :green[{sats:,.0f}]")


def interrupt():
    """ callback for the interrupt button """
    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
    st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))

    st.session_state.redis_conn.decrby(st.session_state.username, st.session_state.token_cost_accumulator)
    st.session_state.token_cost_accumulator = 0
    # save_sats_balance()

    if save_chat_history():
        st.session_state.appstate.load_chat_history()







# # async def run_prompt(prompt, bots_reply_placeholder):
# def run_prompt(prompt, bots_reply_placeholder):
#     with bots_reply_placeholder.chat_message("assistant"):
#         st.session_state.incomplete_stream = ""
#         place_holder = st.empty()

###########  OLD CODE  ############

#         reply = st.session_state.incomplete_stream
#         st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
#         return reply
