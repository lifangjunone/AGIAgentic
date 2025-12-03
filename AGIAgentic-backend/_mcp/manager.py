
import os
import json
import concurrent.futures

from typing import Any, List
from typing_extensions import Self
from .client import MCPClientManager
from common.logger import logger


class MCPConfigManager:
  """ MCP Configuration Manager"""

  _instance: Self | None = None
  _mcp_config: dict[str, Any] = {}

  def __new__(cls, *args: Any, **kwargs: Any) -> Self:
    """ Singleton implementation to ensure only one instance exists."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  

  def __init__(self, config_file: str = "mcp_config.json") -> None:
    """ Initialize the MCP Configuration Manager 
    Args:
        config_file (str): Path to the MCP configuration file.
    """
    self.config_file = config_file

  def load_config(self) -> dict[str, Any]:
    """ Load MCP configuration from a JSON file.
    Returns:
        dict: The MCP configuration.
    """
    if not os.path.exists(self.config_file):
      logger.warning(f"MCP configuration file does not exist: {self.config_file}")
      return {}
    try:
      with open(self.config_file, 'r', encoding='utf-8') as f:
        self._mcp_config = json.load(f).get("mcp_services", {})
      logger.info(f"MCP configuration loaded successfully from {self.config_file}, mcp_services: {self._mcp_config}")
    except Exception as e:
      logger.error(f"Error loading MCP configuration: {str(e)}")
      self._mcp_config = {}
    logger.debug(f"Loaded MCP configuration: {self._mcp_config}")
    return self._mcp_config
  

class MCPManager:
  """ MCP Manager to handle MCP configurations and clients """

  def __init__(self, client: type[MCPClientManager], config: MCPConfigManager) -> None:
    """ Initialize the MCP Manager """
    self.config_manager = config
    self.client_manager = client(self.config_manager.load_config())


def initialize_mcp_manager() -> List[Any]:
  """ Initialize the MCP Manager singleton """
  mcp_tools: List[Any] = []
  mcp_manager = MCPManager(MCPClientManager, MCPConfigManager(config_file="mcp_config.json"))
  try: 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mcp_manager.client_manager.get_mcp_tools)
        tools = future.result()
        mcp_tools.extend(tools)
        logger.info(f"Retrieved {len(tools)} tools from MCP services.")
  except Exception as e:
    logger.error(f"Error initializing MCP Manager or retrieving tools: {str(e)}")
  return mcp_tools
    



