

import asyncio
import traceback

from typing import Dict, Union, List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.sessions import Connection # type: ignore
from langchain_mcp_adapters.client import MultiServerMCPClient # type: ignore

from conf.config import config_manager
from common.logger import logger


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
      logger.debug(f"Validating MCP configuration: {config}")
      # Get transport type, default to 'stdio' if not specified
      transport = config.get("transport")
      if not transport:
        return False
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
      logger.error(f"Configuration validation error: {str(e)}")
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
        logger.error("No MCP configurations provided.")
        return None
      try:
        logger.debug(f"mcp_configs: {self.mcp_configs}") 
        logger.info(f"Creating MCP client for services: {list(self.mcp_configs.keys())}")
        # filter out invalid configurations
        filtered_configs: Dict[str, Connection] = {}
        for service_name, config in self.mcp_configs.items():
          logger.debug(f"Validating MCP configuration for service {service_name}: {config}")
          try:
            # Validate configuration 
            is_valid = await self._validate_config(config)
            logger.debug(f"Validation result for service {service_name}: {is_valid}")
            if is_valid:
              filtered_configs[service_name] = config
          except Exception as e:
            logger.warning(f"Invalid MCP configuration for service {service_name}: {str(e)}")
            continue
        # Check if any valid configurations remain
        if not filtered_configs:
          logger.error("No valid MCP configurations available after filtering.")
          return None
        # Initialize the MCP client with the filtered configurations
        self._client = MultiServerMCPClient(filtered_configs)
        return self._client
      except Exception as e:
        logger.error(f"Error creating MCP client: {str(e)}")
        return None
      
  async def close_client(self) -> None:
    """ Close the MCP client and release resources"""

    if self._client is not None:
      async with self._client_lock:
        try:
          # langchain_mcp_adapters does not have a close method yet
          logger.info("Closing MCP client.")
        except Exception as e:
          logger.error(f"Error closing MCP client: {str(e)}")
        finally:
          self._client = None

  async def get_all_tools(self) -> List[BaseTool]:
    """ Get all available tools from the MCP services
    Returns:
        List: A list of tools available from all configured MCP services.
    """
    client = await self.get_or_create_client()
    if client is None:
      logger.error("MCP client is not available.")
      return []
    try:
      # Set a timeout for getting tools
      all_tools = await asyncio.wait_for(client.get_tools(), timeout=config_manager.mcp_config.GET_ALL_TOOLS_TIMEOUT)
      if not all_tools:
        logger.warning("No tools retrieved from MCP services.")
        return []
      else:
        logger.info(f"Retrieved {len(all_tools)} tools from MCP services.")
        logger.debug(f"Tools: {all_tools}")
        return all_tools
    except asyncio.TimeoutError:
      logger.error("Timeout while retrieving tools from MCP Services.")
      return []
    except Exception as e:
      traceback.print_exc()
      logger.error(f"Error retrieving tools from MCP Services: {str(e)}")
      return []

  def get_mcp_tools(self) -> List[BaseTool]:
    """ Get all available tools from the MCP services (synchronous wrapper)
    Returns:
        List: A list of tools available from all configured MCP services.
    """
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
      tools = new_loop.run_until_complete(self.get_all_tools())
      return tools
    finally:
      new_loop.close()