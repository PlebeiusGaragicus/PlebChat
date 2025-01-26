from pydantic import BaseModel, Field
from enum import Enum


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



class Llama(Agent):
    class Config(BaseModel):
        pass

    @property
    def endpoint(self):
        return "llama"
    @property
    def display_name(self):
        return "🦙 :green[Llama 3]"

    @property
    def placeholder(self):
        return "How can this little Llama help you?"


class Researcher(Agent):
    @property
    def endpoint(self):
        return "researcher"
    @property
    def display_name(self):
        return "🌐 :violet[Researcher]"
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



AGENTS = [Phi, Llama, Researcher]

# AGENTS = {
#     "phi": Phi,
#     "llama": Llama,
#     "researcher": Researcher
# }


def get_agent_by_endpoint(endpoint: str) -> Agent:
    for agent_class in AGENTS:
        if agent_class().endpoint == endpoint:
            return agent_class()
    raise ValueError(f"No agent found for endpoint: {endpoint}")
