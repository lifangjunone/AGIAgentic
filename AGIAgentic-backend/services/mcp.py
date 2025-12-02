

from typing import Any


class MCPService:
  """ MCP Service class to interact with MCP tools. """

  _instance = None

  def __new__(cls):
      if not cls._instance:
          cls._instance = super().__new__(cls)
      return cls._instance


  def __init__(self):
    """ Initialize MCPService """
    self._mcp_tools = None

  @property
  def mcp_tools(self) -> list[Any]:
    """ Get MCP tools """
    if self._mcp_tools is None:
      from main import app  # delayed import to avoid circular import at module load
      self._mcp_tools = getattr(app.state, "mcp_tools", [])
    return self._mcp_tools