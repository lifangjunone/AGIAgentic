

from typing import Any, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from services.llm import LLMService
from services.tool import ToolService
from services.mcp import MCPService


class BaseGraph:
  """ Base graph"""

  def __init__(self, graph_name: str, provider_name: str="zhipu") -> None:
    """ init"""

    # graph name
    self.graph_name = graph_name

    # llm
    llm_service = LLMService(provider_name)
    self.simple_llm: ChatOpenAI = getattr(llm_service, "simple_llm")
    self.reason_llm: ChatOpenAI = getattr(llm_service, "reason_llm")
    self.code_llm: ChatOpenAI = getattr(llm_service, "code_llm")
    self.embedding_llm: OpenAIEmbeddings = getattr(llm_service, "embedding_llm")

    # tools
    tool_service = ToolService()
    self.local_tools: List[Any] = tool_service.local_tools
    mcp_service = MCPService()
    self.mcp_tools: List[Any] = mcp_service.mcp_tools


    # businese parameters
    self.user_id: str = ""
    self.provider_name: str = ""

