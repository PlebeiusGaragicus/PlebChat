from src.flows.echobots import echobot
from src.flows.llm_openai import LLM_OPENAI_GPT
from src.flows.llm_ollama import LLM_OLLAMA
from src.flows.graph_tavily import TavilyBot
from src.flows.chain_reflection import ChainReflectionBot


ALL_CONSTRUCTS = [LLM_OPENAI_GPT, LLM_OLLAMA, ChainReflectionBot, TavilyBot, echobot]
