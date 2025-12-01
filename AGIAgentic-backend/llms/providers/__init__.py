
from abc import ABC, abstractmethod


class LLMProvider(ABC):
  """ Abstract base class for LLM providers.
  """

  @abstractmethod
  def get_llm(self, model_name: str) -> object:
    """Retrieve an LLM instance by model name.
    """
    pass



    
