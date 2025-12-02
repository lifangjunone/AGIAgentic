

from services.llm import LLMService


class BaseGraph:
  """ Base graph"""

  def __init__(self, graph_name: str, provider_name: str="zhipu") -> None:
    """ init"""

    # graph name
    self.graph_name = graph_name

    # llm
    llm_service = LLMService(provider_name)
    self.simple_llm = getattr(llm_service, "simple_llm", None)
    self.reason_llm = getattr(llm_service, "reason_llm", None)
    self.code_llm = getattr(llm_service, "code_llm", None)
    self.embedding_llm = getattr(llm_service, "embedding_llm", None)

    # businese parameters
    self.user_id: str = ""
    self.provider_name: str = ""

