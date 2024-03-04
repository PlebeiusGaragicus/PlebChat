import requests
import json

from pydantic import BaseModel

import streamlit as st

from src.flows import StreamingLLM
from src.persist import PREFERENCES_PATH
from src.common import get


# https://docs.mistral.ai/platform/client/
# https://docs.mistral.ai/guides/model-selection/



# TODO - too many choices... also, should I provide pricing/info for each model...? model info card?
MISTRAL_MODELS = [
    #     "mistral-large-latest",
    #     "mistral-medium",
    #     "mistral-small",
    #     "mistral-tiny",
    # ]

    'open-mixtral-8x7b',
    'open-mistral-7b',
    'mistral-large-latest',
    'mistral-medium',
    'mistral-small',
    'mistral-tiny',
    # 'mistral-large-2402',
    # 'mistral-medium-latest',
    # 'mistral-medium-2312',
    # 'mistral-small-latest',
    # 'mistral-small-2402',
    # 'mistral-small-2312',
    # 'mistral-tiny-2312',
    # 'mistral-embed'
]



class LLM_SETTINGS_MISTRAL(BaseModel):
    model: str = MISTRAL_MODELS[0]
    # temperature: float = 0.7
    api_key: str = ""


class LLM_MISTRAL(StreamingLLM):
    emoji = "🇫🇷"
    name = "Mistral"
    avatar_filename = "mistral0.png"
    preamble = "Jui un modèle de langage de génération de texte développé par ... uhhh... je ne sais pas.  Mais je suis très bon!"

    def __init__(self):
        super().__init__()

    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = LLM_SETTINGS_MISTRAL(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = LLM_SETTINGS_MISTRAL()

        # self.get_availble_models()



    # def get_availble_models(self):
    #     st.toast("Loading Mistral models...", icon="⏳")
    #     """
    #     curl --location "https://api.mistral.ai/v1/models" \
    #     --header 'Content-Type: application/json' \
    #     --header 'Accept: application/json' \
    #     --header "Authorization: Bearer ecdOj2CwLfDgXUhdgy71eaeT08lenlYj"
    #     """
    #     response = requests.get(
    #         "https://api.mistral.ai/v1/models",
    #         headers={
    #             "Content-Type": "application/json",
    #             "Accept": "application/json",
    #             "Authorization": f"Bearer {self.settings.api_key}"
    #         }
    #     )
    #     if response.status_code != 200:
    #         raise Exception(f"Mistral API error: {response.status_code} - {response.text}")
        
    #     models = response.json()
    #     self.model_list = [m["id"] for m in models['data']]

    #     print(self.model_list)



    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("StreamingLLM.run(): not setup yet! Run `setup()` first!")

        # import openai
        # from openai import OpenAI
        # client = openai.OpenAI(api_key=self.settings.api_key)

        # try:
        #     generator = client.chat.completions.create(
        #         model=self.settings.model,
        #         messages=st.session_state.appstate.chat.messages,
        #         stream=True,
        #     )
        # # except openai._exceptions.OpenAIError:
        # # except E
        # except openai._exceptions.APIConnectionError:
        #     # yield "Connection failed - double check your API key?"
        #     yield "🥺 Oops... my connection failed.  Ensure I have my API key and try again?"
        #     return

        # for chunk in generator:
        #     # print(chunk)
        #     yield chunk.choices[0].delta.content

        # if self.settings.api_key in [None, ""]:
            # raise Exception("Mistral API key not set.")

        from mistralai.client import MistralClient
        self.client = MistralClient(api_key=self.settings.api_key)


        try:
            for chunk in self.client.chat_stream(
                model=self.settings.model,
                messages=st.session_state.appstate.chat.messages,
                # safe_mode=st.session_state.user_preferences['mistral_safemode']
                safe_mode=False
            ):
                yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"🥺 Oops... my connection failed.  Ensure I have my API key and try again? ({e})"



    
    def display_settings(self):
        def save_settings():
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "w") as f:
                f.write(json.dumps(self.settings.model_dump()))


        def update(key):
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            save_settings()

        try:
            st.selectbox("Model", options=MISTRAL_MODELS, key="model", index=MISTRAL_MODELS.index(self.settings.model), on_change=update, args=("model",))
            # st.selectbox("Model", options=self.model_list, key="model", index=self.model_list.index(self.settings.model), on_change=update, args=("model",))
            # st.slider("Temperature", min_value=0.0, max_value=1.0, key="temperature", value=self.settings.temperature, on_change=update, args=("temperature",))

            if get("username") == "satoshi": # TODO - don't hardcode... also, this is just a temp workaround
                with st.expander(":blue[API KEYS]", expanded=False):
                    st.text_input(":blue[MISTRAL_API_KEY]", key="api_key", value=self.settings.api_key, on_change=update, args=("api_key",))
        except ValueError:
            self.settings = LLM_SETTINGS_MISTRAL()
            save_settings() # might this cause endless recursion?
            self.display_settings()
