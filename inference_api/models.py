from langchain_core.language_models.chat_models import BaseChatModel
# from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from  agent_config import Config, ModelConfig, ModelProvider

def create_llm(model_config: ModelConfig) -> BaseChatModel:
    if model_config.provider == ModelProvider.OLLAMA:
        return ChatOllama(
            model=model_config.name,
            temperature=model_config.temperature,
            num_ctx=Config.OLLAMA_CONTEXT_WINDOW,
            base_url=Config.OLLAMA_BASE_URL,
            verbose=False,
            keep_alive=-1,
        )
 