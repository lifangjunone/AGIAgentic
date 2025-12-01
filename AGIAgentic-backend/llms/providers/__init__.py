

from typing import Union
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class LLMProvider(ABC):
  """ Abstract base class for LLM providers.
  """

  @abstractmethod
  def get_llm(self, model_name: str, model_type: str = "chat") -> Union[ChatOpenAI, OpenAIEmbeddings]:
    """Retrieve an LLM instance by model name.
    """
    match model_type:
        case "embedding":
            return OpenAIEmbeddings()
        case "chat":
            return ChatOpenAI()
        case _:
            return ChatOpenAI()



    
