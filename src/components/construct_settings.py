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


def cmp_construct_settings():
    if not_init("construct"):
        return

    cols = st.columns((1, 1, 1, 2))

    with cols[0].popover(":orange[𝚯] Hyperparameters"):
        st.write("...go here")

    # with cols[1].popover("Construct Info"):
    #     st.write("yes")


    ### info card
    # with st.expander("Information about this AI workflow", expanded=False):
        # if construct:
        # get('construct').display_model_card()
