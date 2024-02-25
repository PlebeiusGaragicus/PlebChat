import streamlit as st



from mistralai.models.chat_completion import ChatMessage

from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.function import FunctionMessage



from testbed.chain_reflection import ChainReflectionBot



from src.common import (
    ASSETS_PATH,
    AVATAR_PATH,
    is_init,
    not_init,
    get,
    set,
    cprint,
    Colors
)


from src.interface.interface import (
    column_fix,
    center_text,
    centered_button_trick,
)

from src.flows import ChatThread


def init():
    if not_init('thread'):
        st.session_state.thread = ChatThread()
    
    if not_init('construct'):
        st.session_state.construct = ChainReflectionBot()

    if not_init('username'):
        st.session_state.username = "satoshi"


def main_page():

    ################### TOP OF MAIN CHAT ###################
    column_fix()
    center_text("p", "🔬🧪", size=60)


    #### TODO init construct here, if not
    init()



    # TODO - turn this into a settings
    human_avatar = f"{AVATAR_PATH}/user5.png"
    ai_avatar = f"{AVATAR_PATH}/assistant.png"

    for message in get('thread').messages:
        with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
            st.markdown(message.content)


    my_next_prompt_placeholder = st.empty()
    interrupt_button_placeholder = st.empty()
    bots_reply_placeholder = st.empty()
    before_speech_placeholder = st.empty()





    ################### TOP OF SIDEBAR ###################
    construct_settings_placeholder = st.sidebar.empty()


    prompt = None
    
    prompt = st.chat_input("Ask a question.")

    if prompt:
        st.session_state.speech_confirmed = False

        # interrupt_button_placeholder.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
        get('thread').messages.append( ChatMessage(role="user", content=prompt) )


        if get("construct").agentic:
            reply = run_graph(prompt, bots_reply_placeholder)
        else:
            raise Exception("only agentic workflows are tested here")




    ### READ IT AND NEW BUTTONS
    with before_speech_placeholder:
        if len(get('thread').messages) > 0:
            col2 = st.columns((1, 1, 1))
            if col2[2].button("🌱 :green[New]", use_container_width=True):
                st.session_state.thread = ChatThread()



    with construct_settings_placeholder.container(border=False):
        st.write("## :orange[Configuration]")
        get('construct').display_settings()










def run_graph(prompt, bots_reply_placeholder):
    if get('construct').graph is None:
        error_reply = "I'm not configured properly... 🥺  Check my settings.  Do I have all my API keys?"
        get('thread').messages.append(ChatMessage(role="assistant", content=error_reply))
        return error_reply


    avatar_filename = f"{AVATAR_PATH}/{get('construct').avatar_filename}"
    with bots_reply_placeholder.chat_message("assistant", avatar=avatar_filename):

        # TODO - this does NOT provide a good enough context for an agent... at least when opening an stale conversation.
        # for node, output in get('construct').run(str(st.session_state.appstate.chat.messages)):
        # for node, output in get('construct').invoke(str(st.session_state.appstate.chat.messages)): # TODO - don't typecast to a str() dude.. don't be a noob!
        for node, output in get('construct').invoke(str(get('thread').messages)):

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

                    get('thread').messages.append(
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
                        get('thread').messages.append(
                                            ChatMessage(role="assistant",
                                            content=content))

            else:
                # TODO - FIX THIS.... this logic should be placed inside the Graph class for each chain
                try:
                    message = output['messages'][-1]
                    get('thread').messages.append(ChatMessage(role="assistant", content=message.content))
                except TypeError:
                    message = output
                    get('thread').messages.append(ChatMessage(role="assistant", content=message))

    try:
        return message.content
    except AttributeError:
        return message



def main():
    # st.write("main()")
    cprint("\n\nRERUN!!!!!!\n", Colors.RED)
    main_page()
