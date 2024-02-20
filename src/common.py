import pathlib

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"



import streamlit as st


def is_init(var: str):
    return var in st.session_state

def not_init(var: str):
    return var not in st.session_state

def get(var: str):
    if not_init(var):
        raise ValueError(f"Variable {var} not initialized")
    return st.session_state.get(var, None)

def set(var: str, value):
    st.session_state[var] = value
