import os

import streamlit as st
from streamlit_pills import pills


from src.interface import (
    column_fix,
    center_text,
)

from src.flows.constructs import ALL_CONSTRUCTS


from src.common import (
    ASSETS_PATH,
    AVATAR_PATH,
    is_init,
    not_init,
    get,
    set,
)





def cmp_intro():
    if is_init("construct"):
        return

    st.markdown("## Welcome to :rainbow[PlebChat!]")
    # with centered_button_trick():
        # st.image(f"{ASSETS_PATH}/" + "assistant2sm.png")




def cmp_header():
    st.set_page_config(
        # page_title="DEBUG!" if os.getenv("DEBUG", False) else "NOS4A2",
        page_title="PlebChat!",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="wide",
        initial_sidebar_state="auto",
    )

    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever




def cmp_pills():
    construct_names = [c.name for c in ALL_CONSTRUCTS]
    # construct_icons = [c.emoji for c in ALL_CONSTRUCTS]

    if not_init("selected_construct"):
        set("selected_construct", None)

    # selected_index = construct_names.index(get("selected_construct")) if get("selected_construct") in construct_names else None

    # selected = pills(label="Choose an AI workflow:",
    #                 options=construct_names,
    #                 icons=construct_icons,
    #                 clearable=True,
    #                 index=None,
    #             )

    # with st.popover("🧠 :blue[AI Workflows]"):
    selected = st.radio("Choose an AI workflow:", construct_names, index=0, horizontal=True, label_visibility="collapsed")

    st.header("", divider="rainbow")


    if selected is None:
        st.toast("Select a construct workflow to continue")

        set("selected_construct", None)
        if is_init("construct"):
            st.toast("Deleting existing construct...")
            del st.session_state.construct
        
        return


    # selected pill is same as last run... return
    if selected == get("selected_construct"):
        return


    ### We are switching to a new construct
    st.session_state.selected_construct = selected
    st.toast("New selected construct!")

    if is_init("thread"):
        st.toast("New chat thread!!")
        del st.session_state.thread

    for Construct in ALL_CONSTRUCTS:
        if Construct.name == selected:
            st.session_state["construct"] = Construct()
            # st.rerun() # we need this to reload the page with the new construct

    if get("construct") is None:
        raise Exception(f"Unknown construct: {selected} - fix this!")
