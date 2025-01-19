import json
import requests
from typing_extensions import TypedDict

from typing import List, Union, Generator, Iterator
try:
    from pydantic.v1 import BaseModel
except Exception:
    from pydantic import BaseModel



PORT = 8513
PIPELINE_ENDPOINT = "/template"
CONSTRUCT_NAME = "LangGraph Template"
LANGSERVE_ENDPOINT = f"http://host.docker.internal"


class PostRequest(TypedDict):
    user_message: str
    messages: List[dict]
    body: dict



class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.name = CONSTRUCT_NAME

    async def on_startup(self):
        print(f">>> PIPELINE {self.name.upper()} IS STARTING!!! <<<")


    async def on_shutdown(self):
        print(f">>> PIPELINE {self.name.upper()} IS SHUTTING DOWN!!! <<<")


    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict
             ) -> Union[str, Generator, Iterator]:

        if body.get("task") == "Title Generation":
            print("######################################")
            print("Title Generation")
            print("######################################")
            yield "Test Pipeline"
        else:

            print(f">>> PIPELINE '{self.name.upper()}' RUNNING <<<")
            print("######################################")
            print("user_message: str")
            print(f"{user_message}")
            print("model_id: str")
            print(f"{model_id}")
            # print("messages: List[dict]")
            # print(f"{messages}")
            print("body: dict")
            print(f"{json.dumps(body, indent=4)}")
            print("######################################")

            #TODO: title generation?

            url = f"{LANGSERVE_ENDPOINT}:{PORT}{PIPELINE_ENDPOINT}"
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

            req = PostRequest(user_message=user_message, messages=messages, body=body)
            response = requests.post(url, json=req, headers=headers, stream=True)
            for line in response.iter_lines():
                if line:
                    yield line.decode() + '\n'
