

import asyncio
import logging

from typing import Dict, Union, List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.sessions import Connection # type: ignore
from langchain_mcp_adapters.client import MultiServerMCPClient # type: ignore

from ..conf.config import config_manager


class MCPClientManager:
  """ MCP Client Manager
  Manages multiple MCP clients for different services.
  """

  def __init__(self, mcp_configs: Union[Dict[str, Connection], None] = None):
    """ Initialize the MCP Client Manager
    Args:
        mcp_configs (Dict[str, Dict[str, Any]]): A dictionary mapping service names to their MCP configurations.
    """
    self.mcp_configs = mcp_configs or {}
    self._client = None
    self._client_lock = asyncio.Lock()
  
  async def _validate_config(self, config: Connection) -> bool:
    """ Validate MCP configuration
    Args:
        config (Dict[str, Any]): The MCP configuration to validate.
    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    try:
      # Get transport type, default to 'stdio' if not specified
      transport = config.get("transport", "stdio")
      if transport not in ["websocket", "streamable_http", "http"]:
        return False
      if transport == "stdio":
        # The stdio transport requires 'command' parameter
        if "command" not in config:
          return False
      else:
        # Other transports require 'url' parameter
        if "url" not in config:
          return False
    except Exception as e:
      logging.error("Configuration validation error: %s", str(e))
      return False
    # If all checks pass, the configuration is valid
    return True

  async def get_or_create_client(self) -> Union[MultiServerMCPClient, None]:
    """ Get or create a multi-service MCP client
    Returns:
        MCPClient: An instance of the MCP client configured for multiple services or None if no configurations are provided.
    """
    if self._client is not None:
      return self._client
    async with self._client_lock:
      if not self.mcp_configs:
        logging.error("No MCP configurations provided.")
        return None
      try:
        logging.info("Creating MCP client for services: %s", list(self.mcp_configs.keys()))
        # filter out invalid configurations
        filtered_configs: Dict[str, Connection] = {}
        for service_name, config in self.mcp_configs.items():
          try:
            # Validate configuration 
            if await self._validate_config(config):
              filtered_configs[service_name] = config
          except Exception as e:
            logging.warning("Invalid MCP configuration for service '%s': %s", service_name, str(e))
            continue
        # Check if any valid configurations remain
        if not filtered_configs:
          logging.error("No valid MCP configurations available after filtering.")
          return None
        # Initialize the MCP client with the filtered configurations
        self._client = MultiServerMCPClient(filtered_configs)
        return self._client
      except Exception as e:
        logging.error("Error creating MCP client: %s", str(e))
        return None
      
  async def close_client(self) -> None:
    """ Close the MCP client and release resources"""

    if self._client is not None:
      async with self._client_lock:
        try:
          # langchain_mcp_adapters does not have a close method yet
          logging.info("Closing MCP client.")
        except Exception as e:
          logging.error("Error closing MCP client: %s", str(e))
        finally:
          self._client = None

  async def get_all_tools(self) -> List[BaseTool]:
    """ Get all available tools from the MCP services
    Returns:
        List: A list of tools available from all configured MCP services.
    """
    client = await self.get_or_create_client()
    if client is None:
      logging.error("MCP client is not available.")
      return []
    try:
      # Set a timeout for getting tools
      all_tools = await asyncio.wait_for(client.get_tools(), timeout=config_manager.mcp_config.MCP_GET_ALL_TOOLS_TIMEOUT)
      if not all_tools:
        logging.warning("No tools retrieved from MCP services.")
        return []
      else:
        logging.info("Retrieved %d tools from MCP services.", len(all_tools))
        return all_tools
    except asyncio.TimeoutError:
      logging.error("Timeout while retrieving tools from MCP Services.")
      return []
    except Exception as e:
      logging.error("Error retrieving tools from MCP Services: %s", str(e))
      return []
