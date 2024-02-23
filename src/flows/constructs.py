# from src.flows.echobots import echobot, tommybot, dummybot
from src.flows.echobots import echobot
from src.flows.llm_openai import LLM_OPENAI_GPT
from src.flows.llm_ollama import LLM_OLLAMA
from src.flows.graph_tavily import TavilyBot


# ALL_CONSTRUCTS = [echobot, LLM_OPENAI_GPT, LLM_OLLAMA, TavilyBot, tommybot, dummybot]
ALL_CONSTRUCTS = [LLM_OPENAI_GPT, LLM_OLLAMA, TavilyBot, echobot]
