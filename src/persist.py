import json
import yaml
import pathlib
import streamlit as st


PREFERENCES_PATH = pathlib.Path(__file__).parent.parent / "preferences"

from src.common import (
    is_init,
    not_init,
    get,
    set,
)


def load_persistance():
    if is_init("persistance"):
        # st.write(f"persistance already loaded... {get('persistance')}")
        print("persistance already loaded... returning")
        return
        # set("persistance", {})

    persistance_file = PREFERENCES_PATH / f"{get('username')}.json"
    try:
        with open(persistance_file, "r") as f:  # Change "w" to "r"
            set("persistance", json.loads(f.read()))

    except (FileNotFoundError, json.JSONDecodeError):
        set("persistance", default_persistance)
        update_persistance()

    print(get('persistance'))


def update_persistance(key, value):
    print(f"update_persistance()")

    st.session_state["persistance"][key] = value
    # st.write(f"updating {key} to {value}...")

    persistance_file = PREFERENCES_PATH / f"{get('username')}.json"
    with open(persistance_file, "w") as f:
        f.write(json.dumps(get("persistance")))

    import time
    time.sleep(0.1)

### DEFAULT PERSISTANCE
default_persistance = {
    "chosen_pill": "echobot"
}
