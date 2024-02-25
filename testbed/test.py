import asyncio

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
    if not_init('username'):
        st.session_state.username = "satoshi"

    if not_init('thread'):
        st.session_state.thread = ChatThread()
    
    if not_init('construct'):
        st.session_state.construct = ChainReflectionBot()



def main_page():

    ################### TOP OF MAIN CHAT ###################
    column_fix()
    center_text("p", "🔬🧪", size=60)


    #### TODO init construct here, if not
    init()

    with st.expander("message history", expanded=False):
        st.write(get('thread').messages)
    with st.expander("debug", expanded=False):
        st.write(get('construct').settings)

    if get('construct').agentic:
        with st.container(border=True):
            st.markdown("### :red[workflow variables:]")
            get('construct').display_workplace_variables()

    st.divider()

    # prompt_copy_paste = """Generate an essay on the topicality of The Little Prince and its message in modern life."""
    prompt_copy_paste = """Generate a short essay on the topicality of The Little Prince and its message in modern life. Keep it no more than 200 words."""
    st.write(prompt_copy_paste)


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
            reply = invoke_graph(prompt, bots_reply_placeholder)
        else:
            raise Exception("only agentic workflows are tested here")
        
        st.rerun()




    ### READ IT AND NEW BUTTONS
    with before_speech_placeholder:
        if len(get('thread').messages) > 0:
            col2 = st.columns((1, 1, 1))
            if col2[2].button("🌱 :green[New]", use_container_width=True):
                st.session_state.thread = ChatThread()



    with construct_settings_placeholder.container(border=False):
        st.write("## :orange[Configuration]")
        get('construct').display_settings()




def invoke_graph(prompt, bots_reply_placeholder):
    # async def run_generator(prompt):
    #     construct = get('construct')
    #     async for event in construct.run(prompt):
    #         # cprint(f"event: {event}", Colors.YELLOW)
    #         yield event # {"node_name": output}


    # NOTE: yield is not allowed in this function... we simply return the ultimate result of the graph
    async def update_UI(prompt, bots_reply_placeholder):

        # async for event in run_generator(prompt):
        construct = get('construct')
        async for event in construct.run(prompt):
            node = list(event.keys())[0]
            output = event[node]

            cprint(f"node: {node}", Colors.BLUE)
            cprint(f"output: {output}", Colors.GREEN)

            # This causes the generator to stop and the function to return.. this is not what we want as LangSmith sees a GeneratorExit exception.
            # if node == "__end__":
            #     return "__end__"
            if node == "__end__":
                # break
                continue # this allows the generator to continue at signal that it's done


            with bots_reply_placeholder.chat_message("assistant", avatar=f"{AVATAR_PATH}/assistant.png"):

                content = None
                get('thread').messages.append( ChatMessage(role="assistant", content=output.content) )

                # if type(output) is AIMessage: # no.. the reflect step returns a HumanMessage for the AI's benefit
                if type(output) is FunctionMessage:
                    content = f"**Function returned:**\n{output.content}"

                elif hasattr(output, 'additional_kwargs'):
                    if output.additional_kwargs != {}:
                        print(output.additional_kwargs)
                        print(type(output.additional_kwargs))
                        # {'function_call': {'arguments': '{"query":"weather in San Francisco"}', 'name': 'tavily_search_results_json'}}

                        function_name = output.additional_kwargs['function_call']['name']
                        content = f"**Calling Function:**\n{function_name}({output.additional_kwargs['function_call']['arguments']})"

                if content is None:
                    content = output.content
                st.markdown(content)

        return "__end__"


    # NOTE: asyncio.run() cannot be a generator!!!  So we have to wrap it and deal with all interface updates, state changes and sats deductions there.
    ret = asyncio.run(update_UI(prompt, bots_reply_placeholder))
    return ret








# def run_graph(prompt, bots_reply_placeholder):
#     if get('construct').graph is None:
#         error_reply = "I'm not configured properly... 🥺  Check my settings.  Do I have all my API keys?"
#         get('thread').messages.append(ChatMessage(role="assistant", content=error_reply))
#         return error_reply


#     avatar_filename = f"{AVATAR_PATH}/{get('construct').avatar_filename}"
#     with bots_reply_placeholder.chat_message("assistant", avatar=avatar_filename):

#         # TODO - this does NOT provide a good enough context for an agent... at least when opening an stale conversation.
#         # for node, output in get('construct').run(str(st.session_state.appstate.chat.messages)):
#         # for node, output in get('construct').invoke(str(st.session_state.appstate.chat.messages)): # TODO - don't typecast to a str() dude.. don't be a noob!
#         for node, output in get('construct').invoke(str(get('thread').messages)):

#             if node is None:
#                 cprint("node is None", Colors.RED)
#                 break

#             if node != "__end__":
#                 try:
#                     message = output['messages'][0]
#                 except KeyError:
#                     message = output

#                 # <class 'langchain_core.messages.ai.AIMessage'>
#                 # <class 'langchain_core.messages.function.FunctionMessage'>
#                 # <class 'langchain_core.messages.human.HumanMessage'>

#                 if type(message) is FunctionMessage:

#                     content = f"**Function returned:**\n{message.content}"
#                     st.markdown(f"{content}")

#                     get('thread').messages.append(
#                                             ChatMessage(role="assistant",
#                                             content=content))

#                 elif hasattr(message, 'additional_kwargs'):
#                     if message.additional_kwargs != {}:
#                         print(message.additional_kwargs)
#                         print(type(message.additional_kwargs))
#                         # {'function_call': {'arguments': '{"query":"weather in San Francisco"}', 'name': 'tavily_search_results_json'}}

#                         function_name = message.additional_kwargs['function_call']['name']

#                         content = f"**Calling Function:**\n{function_name}({message.additional_kwargs['function_call']['arguments']})"

#                         st.markdown(content)
#                         get('thread').messages.append(
#                                             ChatMessage(role="assistant",
#                                             content=content))

#             else:
#                 # TODO - FIX THIS.... this logic should be placed inside the Graph class for each chain
#                 try:
#                     message = output['messages'][-1]
#                     get('thread').messages.append(ChatMessage(role="assistant", content=message.content))
#                 except TypeError:
#                     message = output
#                     get('thread').messages.append(ChatMessage(role="assistant", content=message))

#     try:
#         return message.content
#     except AttributeError:
#         return message



def main():
    # st.write("main()")
    cprint("\n\nRERUN!!!!!!\n", Colors.RED)
    main_page()
