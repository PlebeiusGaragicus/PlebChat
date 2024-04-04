import time
import json
import streamlit as st
from streamlit_javascript import st_javascript

import uuid

def get_from_local_storage(k):
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('{k}'));"
    )
    return v or {}


def set_to_local_storage(k, v):
    jdata = json.dumps(v)
    st_javascript(
        f"localStorage.setItem('{k}', JSON.stringify({jdata}));"
    )

def find_in_local_storage():
    # all = {}
    # length = st_javascript("localStorage.length", key=str(uuid.uuid4()))
    # st.write(length)
    # for i in range(0, length):
    #     key = st_javascript(f"localStorage.key('{i}');", key=str(uuid.uuid4()))
    #     value = st_javascript(f"localStorage.getItem('{key}');", key=str(uuid.uuid4()))
    #     all[key] = value

    all = st_javascript("""let ever = {};
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            let value = localStorage.getItem(key);
            ever[key] = value;
        }
        return ever;""")
    st.write(all)



TOOL_PREFIX = 'name_of_tool'
INPUT_FIELDS = ['first_input', 'second_input']

if st.session_state.get(TOOL_PREFIX):
    saved_result = st.session_state[TOOL_PREFIX]
else:
    with st.spinner():
        saved_result = get_from_local_storage(TOOL_PREFIX)
        # without sleep doesn't always load on time
        time.sleep(0.5)

# this for solving field problem 
# https://discuss.streamlit.io/t/form-submit-works-only-on-odd-tries/29804
for field in INPUT_FIELDS:
    if field not in st.session_state:
        st.session_state[field] = saved_result.get(field, '')


def save_update_state(st_data: dict):
    st.session_state[TOOL_PREFIX] = st_data
    set_to_local_storage(TOOL_PREFIX, st_data)


with st.form(key='test_form'):
    inp = st.text_input(label='Enter some data',
                        key='first_input')
    btn = st.form_submit_button('Go on!')
    if inp and btn:
        saved_result['first_input'] = inp
        st.success('Its ok')
        save_update_state(saved_result)
    elif btn:
        st.warning('Put something in text area')

with st.form(key='test_form_2'):
    inp = st.text_input(label='Enter some data',
                        key='second_input')
    btn = st.form_submit_button('Go on!')
    if inp and btn:
        saved_result['second_input'] = inp
        st.success('Its ok')
        save_update_state(saved_result)
    elif btn:
        st.warning('Put something in text area')

st.write(st.session_state)

find_in_local_storage()
