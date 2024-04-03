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
    construct_icons = [c.emoji for c in ALL_CONSTRUCTS]
    # pill_index = get("persistance")['chosen_pill']
    # if we play around in debug and switch to production, we need to make sure we don't go out of bounds

    if not_init("selected_construct"):
        set("selected_construct", None)

    selected = pills(label="Choose an AI workflow:",
                    options=construct_names,
                    icons=construct_icons,
                    clearable=True,
                    index=None,
                    # key="pill_key"
                )

    if selected is None:
        st.toast("Select a construct workflow to continue")

        set("selected_construct", None)
        if is_init("construct"):
            st.toast("Deleting existing construct...")
            del st.session_state.construct
        
        return



    if selected != get("selected_construct"):
        st.session_state.selected_construct = selected
        st.toast("New selected construct!")
        
        st.session_state.construct = selected
