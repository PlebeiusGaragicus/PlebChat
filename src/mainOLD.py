import os

import streamlit as st

from mistralai.models.chat_completion import ChatMessage

from langchain_core.messages.function import FunctionMessage


from src.common import (
    AVATAR_PATH,
    not_init,
    get,
)

from src.chat_history import (
    save_chat_history,
    delete_this_chat,
)

from src.settings import (
    save_user_preferences,
)

from src.interface import (
    centered_button_trick,
)






def main_page():

    cols2 = st.columns((1, 1, 1))
    with cols2[0]:
        st.toggle("🗣️🤖", key="speech_input", value=False)
        if get('speech_input') is True:
            st.toggle(
                label="❌✅",
                key="confirm_stt",
                value=st.session_state.user_preferences["confirm_stt"],
                on_change=save_user_preferences,
                kwargs={"toggle_key": "confirm_stt"},)

    with cols2[1]:
        st.toggle("🤖💬", key="read_to_me", value=False)




    


    prompt = st.chat_input("Ask a question.")

    if prompt:
        interrupt_button_placeholder.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
        st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )


        if get("construct").agentic:
            reply = run_graph(prompt, bots_reply_placeholder)
        else:
            with st.spinner("🧠 Thinking..."):
                reply = run_prompt(prompt, bots_reply_placeholder, sats_left_placeholder)



        #### AFTER-PROMPT PROCESSING ####
        new_chat = save_chat_history() # dummy variable for readability
        if new_chat:
            # A new chat thread has just been created, so we must update our list of past conversations
            appstate.load_chat_history()

        if 'read_to_me' in st.session_state and st.session_state.read_to_me == True:
            st.session_state.speak_this = reply

        st.rerun() # we rerun the page so that TTS can be played if `read_to_me` is True





    






    ######################  SIDEBAR  ######################
    if not_init('runlog_dir'):
        # st.session_state.runlog_dir = os.path.join(os.getcwd(), "runlog", st.session_state.username)
        st.session_state.runlog_dir = os.path.join(os.getcwd(), "runlog")
    appstate.load_chat_history()



    # we don't use an expander becuase the construct settings may need to have one
    # with construct_settings_placeholder.expander("Construct settings", expanded=True):
    with construct_settings_placeholder.container(border=False):
        st.write("## :orange[Configuration]")
        get('construct').display_settings()







def run_graph(prompt, bots_reply_placeholder):
    if get('construct').graph is None:
        error_reply = "I'm not configured properly... 🥺  Check my settings.  Do I have all my API keys?"
        st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=error_reply))
        return error_reply


    avatar_filename = f"{AVATAR_PATH}/{get('construct').avatar_filename}"
    with bots_reply_placeholder.chat_message("assistant", avatar=avatar_filename):

        # TODO - this does NOT provide a good enough context for an agent... at least when opening an stale conversation.
        # for node, output in get('construct').run(str(st.session_state.appstate.chat.messages)):
        for node, output in get('construct').invoke(str(st.session_state.appstate.chat.messages)): # TODO - don't typecast to a str() dude.. don't be a noob!

            if node != "__end__":
                try:
                    message = output['messages'][0]
                except KeyError:
                    message = output

                # <class 'langchain_core.messages.ai.AIMessage'>
                # <class 'langchain_core.messages.function.FunctionMessage'>
                # <class 'langchain_core.messages.human.HumanMessage'>

                if type(message) is FunctionMessage:

                    content = f"**Function returned:**\n{message.content}"
                    st.markdown(f"{content}")

                    st.session_state.appstate.chat.messages.append(
                                            ChatMessage(role="assistant",
                                            content=content))

                elif hasattr(message, 'additional_kwargs'):
                    if message.additional_kwargs != {}:
                        print(message.additional_kwargs)
                        print(type(message.additional_kwargs))
                        # {'function_call': {'arguments': '{"query":"weather in San Francisco"}', 'name': 'tavily_search_results_json'}}

                        function_name = message.additional_kwargs['function_call']['name']

                        content = f"**Calling Function:**\n{function_name}({message.additional_kwargs['function_call']['arguments']})"

                        st.markdown(content)
                        st.session_state.appstate.chat.messages.append(
                                            ChatMessage(role="assistant",
                                            content=content))

            else:
                # TODO - FIX THIS.... this logic should be placed inside the Graph class for each chain
                try:
                    message = output['messages'][-1]
                    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=message.content))
                except TypeError:
                    message = output
                    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=message))

    try:
        return message.content
    except AttributeError:
        return message




def interrupt():
    """ callback for the interrupt button """
    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
    st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))

    if save_chat_history():
        st.session_state.appstate.load_chat_history()
