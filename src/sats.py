# import redis

import streamlit as st

from src.common import get


def charge_user(amount: int = None):
    if amount is None:
        amount = st.session_state.token_cost_accumulator

    sats_left = st.session_state.redis_conn.decrby(get('username'), amount)
    st.session_state.token_cost_accumulator = 0
    return sats_left



def load_sats_balance():
    return int(st.session_state.redis_conn.get(st.session_state.username) or 0)


def add_sats(amount: int):
    current_sats = int(st.session_state.redis_conn.get(st.session_state.username) or 0)
    new_sats = current_sats + amount
    st.session_state.redis_conn.set(st.session_state.username, new_sats)

