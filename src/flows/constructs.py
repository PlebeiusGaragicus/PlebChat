import os

from src.flows.echobots import echobot
from src.flows.llm_openai import LLM_OPENAI_GPT
from src.flows.llm_gemini import LLM_GOOGLE_GEMINI
from src.flows.llm_mistral import LLM_MISTRAL
from src.flows.llm_ollama import LLM_OLLAMA
from src.flows.chain_tavily import TavilyBot
from src.flows.chain_reflection import ChainReflectionBot
from src.flows.custom_langflow import CustomLangFlow


if os.getenv("DEBUG", False):
    ALL_CONSTRUCTS = [echobot, LLM_GOOGLE_GEMINI, LLM_OPENAI_GPT, LLM_MISTRAL, LLM_OLLAMA, ChainReflectionBot, TavilyBot, CustomLangFlow]
else:
    # NOTE: only include the bots that are ready for production!
    # ALL_CONSTRUCTS = [LLM_OPENAI_GPT, TavilyBot]
    ALL_CONSTRUCTS = [LLM_OPENAI_GPT, LLM_GOOGLE_GEMINI, LLM_MISTRAL]
