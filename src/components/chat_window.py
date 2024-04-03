import streamlit as st

from src.common import (
    AVATAR_PATH,
    not_init,
    is_init,
    get
)

from mistralai.models.chat_completion import ChatMessage
from src.flows import ChatThread



def cmp_chat_window():
    if not_init("construct"):

        # >> CLEAR THE VARIABLES USED IN THIS COMPONENT
        if is_init("thread"):
            st.toast("deleting thread")
            del st.session_state.thread

        return


    



    with st.container(border=True):

        human_avatar = f"{AVATAR_PATH}/user0.png"
        ai_avatar = f"{AVATAR_PATH}/{get('construct').avatar_filename}"

        if is_init("thread"):
            for message in st.session_state.thread.messages:
                with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
                    st.markdown(message.content)



        # This is so that we can later populate with the users' next prompt
        # and the bots reply and allows the input field (or start recording button)
        # to be at the bottom of the page
        my_next_prompt_placeholder = st.empty()
        cols2 = st.columns((1, 1))
        with cols2[0]:
            interrupt_button_placeholder = st.empty()
        bots_reply_placeholder = st.empty()


        prompt = st.chat_input("Ask a question.")

        if prompt:
            if not_init("thread"):
                st.toast("new thread!!")
                st.session_state.thread = ChatThread()

            my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
            st.session_state.thread.messages.append( ChatMessage(role="user", content=prompt) )


            with bots_reply_placeholder.chat_message("assistant", avatar=ai_avatar):

                st.session_state.incomplete_stream = ""
                place_holder = st.empty()

                # we don't want to use write_stream because we need to keep track of the cost (and other things), as we go.
                # or... really for the ability to interrupt the stream and save the partially computed reply
                # reply = st.write_stream(get('construct').run(prompt))
                for chunk in get('construct').run(prompt):

                    st.session_state.incomplete_stream += chunk
                    place_holder.markdown(st.session_state.incomplete_stream)

                # reply = st.session_state.incomplete_stream
                st.session_state.thread.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))

            # TODO - save chat history

            # TODO - speak the result, if needed
