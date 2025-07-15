from dataclasses import dataclass
from enum import Enum

class ModelProvider(str, Enum):
    OLLAMA = "ollama"
  

@dataclass
class ModelConfig:
    name: str
    temperature: float
    provider: ModelProvider
 
devstral_24B = ModelConfig("devstral:24b", temperature=0.01, provider=ModelProvider.OLLAMA)
 
class Config:
    SEED = 42
    MODEL = devstral_24B
    OLLAMA_CONTEXT_WINDOW = 4096  
    OLLAMA_BASE_URL= "https://inference.jhingaai.com" 
    SERPER_API_TOKEN="79ed7737508eaf88b020d39e133f17ed69b829b8"

    class Agent:
        MAX_ITERATIONS=10     
 