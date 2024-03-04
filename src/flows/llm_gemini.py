import json

from pydantic import BaseModel

import streamlit as st

from src.flows import StreamingLLM
from src.persist import PREFERENCES_PATH
from src.common import get


# https://aistudio.google.com/app/prompts/new_chat



class GoogleSafetySettings():
    """
    Content is blocked based on the probability that it is harmful.
        --Google
    """

    BLOCK_FEW = "BLOCK_ONLY_HIGH"
    BLOCK_SOME = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_MOST = "BLOCK_LOW_AND_ABOVE"




# TODO - too many choices... also, should I provide pricing/info for each model...? model info card?
GEMINI_MODELS = [
        "gemini-1.0-pro",
    ]



class LLM_SETTINGS_GOOGLE_GEMINI(BaseModel):
    model: str = GEMINI_MODELS[0]
    # temperature: float = 0.7
    api_key: str = ""


class LLM_GOOGLE_GEMINI(StreamingLLM):
    emoji = "🔮"
    name = "Google Gemini"
    avatar_filename = "gemini0.png"
    preamble = "Closed source and ready to take your money!"


    def __init__(self):
        super().__init__()


    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            settings_filename = PREFERENCES_PATH / f"{get('username')}_botsettings_{self.name}.json"
            with open(settings_filename, "r") as f:
                settings = json.loads(f.read())
                self.settings = LLM_SETTINGS_GOOGLE_GEMINI(**settings)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = LLM_SETTINGS_GOOGLE_GEMINI()


        # Set up the model
        self.generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
        ]



    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("StreamingLLM.run(): not setup yet! Run `setup()` first!")


        import google.generativeai as genai

        genai.configure(api_key=self.settings.api_key)

        model = genai.GenerativeModel(model_name=self.settings.model,
                                    generation_config=self.generation_config,
                                    safety_settings=self.safety_settings)

        # prompt_parts = [
        #     "input: ",
        #     "output: ",
        # ]


        convo = model.start_chat(history=[])

        for chunk in convo.send_message(prompt, stream=True):
            yield chunk.text

        # for chunk in model.generate_content(prompt_parts, stream=True):
        #     print(chunk.text)
        #     yield chunk.text

        # response = model.generate_content(prompt_parts, stream=True)
        # print(response.text)



    
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
            st.selectbox("Model", options=GEMINI_MODELS, key="model", index=GEMINI_MODELS.index(self.settings.model), on_change=update, args=("model",))
            # st.slider("Temperature", min_value=0.0, max_value=1.0, key="temperature", value=self.settings.temperature, on_change=update, args=("temperature",))

            if get("username") == "satoshi": # TODO - don't hardcode... also, this is just a temp workaround
                with st.expander(":blue[API KEYS]", expanded=False):
                    st.text_input(":blue[GEMINI_API_KEY]", key="api_key", value=self.settings.api_key, on_change=update, args=("api_key",))
        except ValueError:
            self.settings = LLM_SETTINGS_GOOGLE_GEMINI()
            save_settings() # might this cause endless recursion?
            self.display_settings()

