import time
from typing import Type, Union
from pydantic import BaseModel

from mistralai.models.chat_completion import ChatMessage


class AgenticChatThread(ChatMessage):
    step: list[Union[str, str]]



class ChatThread:
    def __init__(self):
        self.session_start_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.description = None
        self.messages: list[ChatMessage] = []




class AIWorkflowAbsctractConstruct:
    # name: str = "unnamed"
    # emoji: str = "🤖"
    avatar_filename: str = "assistant.png"
    # preamble: str = "I'm a bot!"

    def __init__(self):
        self._is_setup = False

        self.setup()

    
    def setup(self):
        raise NotImplementedError("Must implement setup() this in child class!")


    def run(self, prompt, **kwargs):
        raise NotImplementedError("Must implement run() this in child class!")


    def display_settings(self):
        raise NotImplementedError("Must implement display_settings() this in child class!")


    # it's OK not to have a model card for every bot
    def display_model_card(self):
        pass


class StreamingLLM(AIWorkflowAbsctractConstruct):
    agentic = False

class LangChainConstruct(AIWorkflowAbsctractConstruct):
    agentic = True
