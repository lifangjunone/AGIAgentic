from pydantic import Field
from pydantic_settings import BaseSettings

class MCPSettings(BaseSettings):
    """ Settings for MCP integration """
    MCP_GET_ALL_TOOLS_TIMEOUT: float = Field(10.0, description="Timeout in seconds for getting all tools from MCP services")

    class Config:
        env_prefix = "MCP_"
        case_sensitive = True


class AgentSettings(BaseSettings):
    """ Settings for Agent integration """
    AGENT_TIMEOUT: float = Field(10.0, description="Timeout in seconds for agent services")

    class Config:
        env_prefix = "AGENT_"
        case_sensitive = True


class ToolsSettings(BaseSettings):
    """ Settings for tools """
    TOOLS_RETRY_LIMIT: float = Field(10.0, description="Retry limit for tools")

    class Config:
        env_prefix = "TOOLS_"
        case_sensitive = True
