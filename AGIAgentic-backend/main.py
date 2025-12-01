

from loguru import logger
from fastapi import FastAPI
from typing import List, Any, Dict
from contextlib import asynccontextmanager

from api import router
from tools import nitialize_tool_manager
from llms import initialize_model_manager
from common.logger import initialize_logger
from _mcp.manager import initialize_mcp_manager
from conf.config import config_manager, ConfigManager




def init_mcp(app: FastAPI) -> List[Any]:
    """Initialize MCP configuration."""
    mcp_tools: List[Any] = initialize_mcp_manager()
    logger.info("🔗 Fetching tools from MCP services...")
    logger.info(f"✅ Retrieved {len(mcp_tools)} tools from MCP services.")
    logger.debug("MCP Tools List:\n" + "\n".join([f"  - {tool}" for tool in mcp_tools]))
    logger.info("-" * 60)
    app.state.mcp_tools = mcp_tools
    return mcp_tools

def init_tools(app: FastAPI) -> List[Any]:
    """Initialize tools from the local tools package."""
    tools: List[Any] = nitialize_tool_manager()
    logger.info("🧰 Initializing tools from local tools package...")
    logger.info(f"✅ Total tools initialized: {len(tools)}")
    logger.debug("Local Tools List:\n" + "\n".join([f"  - {tool}" for tool in tools]))
    logger.info("=" * 60 + "\n")
    app.state.local_tools = tools
    return tools

def init_models(app: FastAPI) -> Dict[str, Any]:
    """Initialize model providers and LLMs."""
    llm_providers = initialize_model_manager()
    logger.info("🤖 Initializing model providers and LLMs...")
    log_message = f"\n{'=' * 100}\n"
    log_message += "✅  Model Initialization Successful\n"
    for provider_name, provider_instance in llm_providers.items():
      log_message += (
        f"Provider:  {provider_name}\n"
        f"Instance:  {repr(provider_instance)}\n"
    )
    log_message += f"{'=' * 100}\n"
    logger.debug(log_message)
    app.state.llm_providers = llm_providers
    return llm_providers


def initialize_config_manager(app: FastAPI) -> ConfigManager:
    """ Initialize the global configuration manager """
    app.state.config_manager = config_manager
    return config_manager


def init(app: FastAPI = None) -> None: # type: ignore
    """ Initialize the entire application."""

    # Initialize global configuration manager
    initialize_config_manager(app)
    
    # Initialize logging
    initialize_logger()

    # Initialize and load MCP configuration
    init_mcp(app)

    # Initialize tools from the local tools package
    init_tools(app)

    # Initialize the model providers and LLMs
    init_models(app)

def clear() -> None:
    """ Clear the application state and resources."""
    logger.info("🧹 Clearing application state and resources...")
    # Placeholder for actual clearing logic
    logger.info("✅ Application state cleared.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the application components
    init(app)
    yield
    # Clean up the ML models and release the resources
    clear()

def create_app() -> FastAPI:
    """Create and configure the main application."""

    app: FastAPI = FastAPI(title="AGIAgentic Backend",lifespan=lifespan, reload=True)

    # register router
    app.include_router(router, prefix="/api/v1")
    # Log application start
    logger.info("\n" + "=" * 60)
    logger.info("\n🚀  Starting AGIAgentic Backend")
    logger.info("\n" + "=" * 60 + "\n")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    server_config = config_manager.server_config
    uvicorn.run(
      app='main:app',
      host=server_config.HOST,
      port=server_config.PORT,
      reload=server_config.RELOAD
    )

