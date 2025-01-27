from pydantic import BaseModel, Field
from enum import Enum

import streamlit as st


class Agent():
    @property
    def endpoint(self):
        raise NotImplementedError("You must implement this.")
    @property
    def display_name(self):
        raise NotImplementedError("You must implement this.")
    @property
    def placeholder(self):
        raise NotImplementedError("You must implement this.")

    class Config(BaseModel):
        pass




@st.cache_resource(ttl=3600)
def ollama_models():
    from ollama import Client
    # from ollama._types import ListResponse

    models = Client("http://host.docker.internal:11434").list()

    # print(type(models))
    # print(models.__dict__['models'])

    for m in models['models']:
        print(m.model)

    # Create enum dynamically
    model_dict = {model.upper().replace(":", "_").replace(".", "_"): model for model in [m.model for m in models['models']]}

    return Enum('OllamaModels', model_dict)

OllamaModels = ollama_models()






class Ollama(Agent):
    @property
    def endpoint(self):
        return "ollama"
    @property
    def display_name(self):
        return "🦙 :orange[Ollama]"
    @property
    def placeholder(self):
        return "🗣️🤖💬 Let's chat!"

    class Config(BaseModel):
        ollama_model: OllamaModels = Field(
            default=next(iter(OllamaModels)),  # Get first enum value as default
            # description="The LLM model to use for Ollama.",
        )


class Phi(Agent):
    @property
    def endpoint(self):
        return "phi"
    @property
    def display_name(self):
        return "✨ :red[Phi-4]"
    @property
    def placeholder(self):
        return "What's on your mind?"

    class Config(BaseModel):
        class VoiceType(str, Enum):
            HUMAN = "👤 Human"
            AI = "🤖 AI"

        voice: VoiceType = Field(
            default=VoiceType.HUMAN,
            title=":blue[Choose your Voice]"
        )
        example: str = Field(
            default="Pleb",
            title=":blue[examples examples]",
            max_length=100
        )


# class Llama(Agent):
#     class Config(BaseModel):
#         pass

#     @property
#     def endpoint(self):
#         return "llama"
#     @property
#     def display_name(self):
#         return "🦙 :green[Llama 3]"

#     @property
#     def placeholder(self):
#         return "How can this little Llama help you?"


class Researcher(Agent):
    @property
    def endpoint(self):
        return "research"
    @property
    def display_name(self):
        return "🌐 :violet[Research 'Precis']"
    @property
    def placeholder(self):
        return "What do you want to learn?"

    class Config(BaseModel):
        iterations: int = Field(
            20,
            ge=10,
            le=30,
            multiple_of=2,
            description="Number property with a limited range.",
        )


AGENTS = [Ollama, Researcher, Phi]


def get_agent_by_endpoint(endpoint: str) -> Agent:
    for agent_class in AGENTS:
        if agent_class().endpoint == endpoint:
            return agent_class()
    raise ValueError(f"No agent found for endpoint: {endpoint}")
