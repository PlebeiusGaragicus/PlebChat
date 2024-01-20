import time
import streamlit as st

from mistralai.models.chat_completion import ChatMessage

from src.chat_history import serialize_messages



class AbstractModel:
    def __init__(self, name):
        self.name = name

        self.client = None
        self.options = {}

    def get_client(self):
        raise NotImplementedError("Must implement get_client() this in child class!")


class Content:
    def __init__(self, word_chunk):
        self.content = word_chunk

class Delta:
    def __init__(self, word_chunk):
        self.delta = Content(word_chunk)

class DeltaContentChunk:
    def __init__(self, word_chunk):
        self.choices = [ Delta(word_chunk) ]




class Echobot(AbstractModel):
    def __init__(self):
        super().__init__("Echobot")
        # super("Echobot")

    def get_client(self):
        time.sleep(0.5)
        echo = st.session_state.appstate.chat.messages[-1].content

        # split the message into words
        echo = echo.split(" ")
        for e in echo:
            time.sleep(0.15)
            # yield DeltaContentChunk(f" {e}")
            yield e

    @classmethod
    def get_streamed_tokens(cls, chunk):
        for c in chunk:
            # yield c.choices[0].delta.content
            yield c

    def get_description(self):
        content = st.session_state.appstate.chat.messages[0].content
        # return first 3 words, at most
        return " ".join(content.split(" ")[:4])



class UppercaseBot(AbstractModel):
    def __init__(self):
        super().__init__("UppercaseBot")

    def get_client(self):
        time.sleep(0.8)
        echo = st.session_state.appstate.chat.messages[-1].content

        # split the message into words
        echo = echo.split(" ")
        for e in echo:
            time.sleep(0.3)
            yield DeltaContentChunk(f" {e.upper()}!")

    @classmethod
    def get_streamed_tokens(cls, chunk):
        for c in chunk:
            yield c.choices[0].delta.content

    def get_description(self):
        content = st.session_state.appstate.chat.messages[0].content
        # return first 3 words, at most
        return " ".join(content.split(" ")[:4]).upper()



class MistralAPI(AbstractModel):
    MISTRAL_MODELS = ['mistral-medium', 'mistral-small', 'mistral-tiny']

    def __init__(self):
        super().__init__("Mistral API")
        from mistralai.client import MistralClient

        if st.session_state.user_preferences["mistral_api_key"] in [None, ""]:
            raise Exception("Mistral API key not set.")

        # TODO add error handling here
        self.client = MistralClient(api_key=st.session_state.user_preferences["mistral_api_key"])


    def get_client(self):
        return self.client.chat_stream(
            model=st.session_state.user_preferences['mistral_model'],
            messages=st.session_state.appstate.chat.messages,
            safe_mode=st.session_state.user_preferences['mistral_safemode']
        )

    @classmethod
    def get_streamed_tokens(cls, chunk):
        for c in chunk:
            yield c.choices[0].delta.content

    def get_description(self):
        messages = [
            ChatMessage(
                role="user",
                content=f"Reduce the following user query into 3 to 4 key words: `{st.session_state.appstate.chat.messages[0].content}`\nDo not answer questions. Your reply MUST be no more than 4 words!"
            )
        ]

        chat_response = self.client.chat(
            model="mistral-small", #TODO use medium?  The smaller ones seem to SUCK at following directions.
            messages=messages,
        )
        return chat_response.choices[0].message.content
    


class MistralLocal(AbstractModel):
    def __init__(self):
        super().__init__("Mistral Local")
        self.client = None

    def get_client(self):
        import ollama
        smsg = [serialize_messages(m) for m in st.session_state.appstate.chat.messages]
        return ollama.chat(
                model='mistral',
                messages=smsg,
                stream=True
            )

    @classmethod
    def get_streamed_tokens(cls, chunk):
        for c in chunk:
            yield c['message']['content']

    def get_description(self):
        content = st.session_state.appstate.chat.messages[0].content
        return " ".join(content.split(" ")[:4])



class Llama2Local(AbstractModel):
    def __init__(self):
        super().__init__("Llama2 Local")
        self.client = None

    def get_client(self):
        import ollama
        smsg = [serialize_messages(m) for m in st.session_state.appstate.chat.messages]
        return ollama.chat(
                model='llama2',
                messages=smsg,
                stream=True
            )

    @classmethod
    def get_streamed_tokens(cls, chunk):
        for c in chunk:
            yield c['message']['content']

    def get_description(self):
        content = st.session_state.appstate.chat.messages[0].content
        return " ".join(content.split(" ")[:4])





class OpenAIAPI(AbstractModel):
    def __init__(self):
        super().__init__("OpenAI API")

        if st.session_state.user_preferences["openai_api_key"] in [None, ""]:
            raise Exception("OpenAI API key not set.")

        from openai import OpenAI

        # TODO add error handling here
        self.client = OpenAI(api_key=st.session_state.user_preferences["openai_api_key"])


    def get_client(self):
        return self.client.chat.completions.create(
            model="gpt-4",
            messages=st.session_state.appstate.chat.messages,
            stream=True,
        )


    @classmethod
    def get_streamed_tokens(cls, chunk):
        for c in chunk:
            yield c.choices[0].delta.content


    def get_description(self):
        content = st.session_state.appstate.chat.messages[0].content
        # return first 3 words, at most
        return " ".join(content.split(" ")[:4])
