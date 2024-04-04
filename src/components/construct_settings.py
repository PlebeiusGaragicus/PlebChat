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


# https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line
def cmp_construct_settings():
    if not_init("construct"):
        return

    construct = get('construct')

    cols = st.columns((1, 1, 1, 2))

    with cols[0].popover(":orange[𝚯] Hyperparameters"):
    # with cols[0].popover(":orange[𝚯]", use_container_width=True):
        construct.display_settings()

    # with cols[1].popover(":green[✔️] Model"):
    # with cols[1].expander("🧠 :blue[Model]"):
    with st.sidebar:
        st.markdown(f"# :orange[{construct.name}]")
        construct.display_model_card()
