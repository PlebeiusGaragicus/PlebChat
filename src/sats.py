# import redis

import streamlit as st

from src.common import get, PREFERENCES_PATH

def load_sats_balance():
    return int(st.session_state.redis_conn.get(st.session_state.username) or 0)

    # get("username")

    # # read file
    # # PREFERENCES_PATH.mkdir(parents=True, exist_ok=True)

    # filename = PREFERENCES_PATH / f"{get('username')}.sats"
    # try:
    #     with open(filename, "r") as f:  # Change "w" to "r"
    #         sats = f.read()
    #         # st.write(f"loaded {sats} sats from {filename}")
    #         return int(sats)
    # except FileNotFoundError:
    #     st.write(f"no sats file found... creating {filename}")
    #     with open(filename, "w") as f:
    #         f.write("0")
    #         return 0

    # assert False, "should not reach here"



def add_sats(amount: int):
    current_sats = int(st.session_state.redis_conn.get(st.session_state.username) or 0)
    new_sats = current_sats + amount  # 'amount' is the number of satoshis to add
    st.session_state.redis_conn.set(st.session_state.username, new_sats)

    # filename = PREFERENCES_PATH / f"{get('username')}.sats"
    # with open(filename, "r") as f:
    #     current_sats = int(f.read())
    # with open(filename, "w") as f:
    #     f.write(str(current_sats + sats))
    
    # st.toast(f"Added {sats} sats to your balance!", icon="⚡️")


def save_sats_balance():
    raise ("save_sats_balance() DEPRECATED")
    st.session_state.redis_conn.set(st.session_state.username, st.session_state.sats)

    # filename = PREFERENCES_PATH / f"{get('username')}.sats"
    # with open(filename, "w") as f:
    #     f.write(str(get("sats")))
