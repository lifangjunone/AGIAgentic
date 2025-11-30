
from typing import List, Any
from _mcp.manager import initialize_mcp_manager

from common.logger import initialize_logger


def main():
    # Initialize logging
    logger = initialize_logger()
    # Initialize and load MCP configuration
    mcp_tools: List[Any] = initialize_mcp_manager()
    # Fetch all available tools from MCP services
    logger.info("Fetching tools from MCP services...")
    logger.info("--------------------------------------------------")
    logger.info(f"Retrieved {len(mcp_tools)} tools from MCP services.")
    logger.info("Tools:", mcp_tools)
    logger.info("--------------------------------------------------")



if __name__ == "__main__":
    main()
