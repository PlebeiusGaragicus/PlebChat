import streamlit as st

# from src.common import (
#     ChatMessage,
# )

from src.chat_history import (
    save_chat_history,
)

from src.flows import ChatMessage


def column_fix():
    st.write("""<style>
[data-testid="column"] {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>""", unsafe_allow_html=True)



def center_text(type, text, size=None):
    if size == None:
        st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)
    else:
        st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)


def centered_button_trick():
    """ Use this in a `with` statement to center a button.
    
    Example:
    ```python
    with centered_button_trick():
        st.button(
            "👈 back",
            on_click=go_to_main_page,
            use_container_width=True)
    ```
    """
    columns = st.columns((1, 2, 1))
    with columns[0]:
        st.empty()
    # with columns[1]:
        # normally the button logic would go here
    with columns[2]:
        st.empty()

    return columns[1]


# def interrupt():
#     """ callback for the interrupt button """
#     st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
#     st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))

#     if save_chat_history():
#         st.session_state.appstate.load_chat_history()

    # st.rerun() # not allowed in on_click handlers (callbacks)
