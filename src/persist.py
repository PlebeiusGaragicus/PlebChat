import json
import yaml
import pathlib
import streamlit as st



from src.common import (
    PREFERENCES_PATH,
    is_init,
    not_init,
    get,
    set,
)


def load_persistance():
    if is_init("persistance"):
        # st.write(f"persistance already loaded... {get('persistance')}")
        # print("persistance already loaded... returning")
        return
        # set("persistance", {})

    persistance_file = PREFERENCES_PATH / f"{get('username')}.json"
    try:
        with open(persistance_file, "r") as f:  # Change "w" to "r"
            set("persistance", json.loads(f.read()))

    except (FileNotFoundError, json.JSONDecodeError):
        set("persistance", default_persistance)
        update_persistance()

    # print(get('persistance'))


# TODO seems hacky... but whatevs.... there could be a better way to have consistent naming and "scoop" all persistance keys... nevermind.
# def update_persistance(key, value):
def update_persistance(key = None, value = None):
    # print(f"update_persistance()")

    if key is not None and value is not None:
        st.session_state["persistance"][key] = value
    # st.write(f"updating {key} to {value}...")
        
    # ensure persistance directory exists
    if not PREFERENCES_PATH.exists():
        PREFERENCES_PATH.mkdir()

    persistance_file = PREFERENCES_PATH / f"{get('username')}.json"
    with open(persistance_file, "w") as f:
        f.write(json.dumps(get("persistance")))

    import time
    # time.sleep(0.1) # TODO NEEDED



### DEFAULT PERSISTANCE
default_persistance = {
    "chosen_pill": 0 # INDEX OF THE PILL USED TO CHOOSE THE AI CONSTRUCT WORKFLOW
}
