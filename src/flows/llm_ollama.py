import json
import enum

from pydantic import BaseModel

import streamlit as st

from streamlit_modal import Modal

import ollama

from src.flows import StreamingLLM
from src.persist import PREFERENCES_PATH
from src.common import get
from src.chat_history import serialize_messages



# https://github.com/ollama/ollama/blob/main/docs/api.md
# https://python.langchain.com/docs/integrations/llms/ollama
# https://github.com/ollama/ollama-python
# https://js.langchain.com/docs/use_cases/question_answering/local_retrieval_qa




# [c['name'] for c in ollama.list()['models']]
OLLAMA_MODELS = ["mistral", "llama2"]

# class OllamaModels:
#     MISTRAL = "mistral"
#     LLAMA2 = "llama2"


class LLM_SETTINGS_OLLAMA(BaseModel):
    model: str = ""
    temperature: float = 0.7


class LLM_OLLAMA(StreamingLLM):
    emoji = "🦙"
    name = "Ollama"
    avatar_filename = "ollama.png"
    preamble = "What does the LLaMA say? 🎤🦙"

    def __init__(self):
        super().__init__()

    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = LLM_SETTINGS_OLLAMA(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = LLM_SETTINGS_OLLAMA()



    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("run(): not setup yet! Run `setup()` first!")

        # ensure ollama model is downloaded
        # TODO put a loading bar here... it might take a long time!!!
        ollama.pull(self.settings.model)

        smsg = [serialize_messages(m) for m in st.session_state.appstate.chat.messages]
        client = ollama.chat(
                model=self.settings.model,
                messages=smsg,
                stream=True
            )

        for chunk in client:
            yield chunk['message']['content']



    
    def display_settings(self):
        st.caption(f"Loaded model: `{self.settings.model}`")
        def update(key):
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            # save to file
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))

        available_models = [c['name'] for c in ollama.list()['models']]
        if available_models == []:
            st.write("No models available - see https://ollama.com/library for more info.")
        else:
            try:
                selected_model_index = available_models.index(self.settings.model)
            except ValueError:
                selected_model_index = 0

            st.selectbox("Available Models", options=available_models, key="model", index=selected_model_index, on_change=update, args=("model",))
            st.slider("Temperature", min_value=0.0, max_value=1.0, key="temperature", value=self.settings.temperature, on_change=update, args=("temperature",))

        # st.write('---')
        with st.expander("Model management", expanded=False):
            st.text_input("Download model", key="model_to_download", value="")
            if st.button("Download"):
                if st.session_state.model_to_download is "":
                    st.warning("Enter a model name to download!")
                else:
                    status_placeholder = st.empty()
                    try:
                        generator = ollama.pull(st.session_state.model_to_download, stream=True)
                        for chunk in generator:
                            with status_placeholder.status(f"{chunk['status']}", expanded=True, state="running"):
                                st.write(chunk)

                        # status_placeholder.status(f"{chunk['status']}", state="complete")
                        st.rerun() # so that it shows the new model in the dropdown
                    except ollama.ResponseError:
                        status_placeholder.status(f"{chunk['status']}", state="error")
                        st.toast("Could not pull model!", icon='💥')


            st.write("Available models: https://ollama.com/library")


            modal = Modal("Demo Modal", key="demo-modal")
            open_modal = st.button(":green[model info card]", key="model_info")
            if open_modal:
                modal.open()

            if modal.is_open():
                with modal.container():
                    info = ollama.show(self.settings.model)

                    # format the info JSON
                    info = json.dumps(info, indent=4)
                    # st.markdown(info)
                    st.write(info)

            st.write("---")

            if st.button(":red[Delete loaded model]"):
                with st.spinner(f"Deleting model: {self.settings.model}..."):
                    ollama.delete(self.settings.model)
                    st.toast(f"Deleted model: {self.settings.model}!", icon='🗑️')
                    st.write(f"Deleted: {self.settings.model}")
                    # st.rerun()





"""


import streamlit as st
from streamlit_modal import Modal

import streamlit.components.v1 as components


modal = Modal( "Demo Modal", key="demo-modal")
open_modal = st.button("Open")
if open_modal:
    modal.open()

if modal.is_open():
    with modal.container():
        st.write("Text goes here")

        html_string = '''
        <h1>HTML string in RED</h1>

        <script language="javascript">
          document.querySelector("h1").style.color = "red";
        </script>
        '''
        components.html(html_string)

        st.write("Some fancy text")
        value = st.checkbox("Check me")
        st.write(f"Checkbox checked: {value}")


"""