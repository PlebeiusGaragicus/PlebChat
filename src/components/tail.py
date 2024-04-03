import os
import streamlit as st

from src.VERSION import VERSION

def cmp_tail():
    with st.sidebar:
        caption = f"Version :green[{VERSION}] | "
        if os.getenv("DEBUG", False):
            caption += ":orange[DEBUG] | "
        caption += "by PlebbyG 🧑🏻‍💻"
        st.caption(caption)
