from pydantic import Field
from pydantic_settings import BaseSettings

class MCPSettings(BaseSettings):
    """ Settings for MCP integration """
    GET_ALL_TOOLS_TIMEOUT: float = Field(10.0, description="Timeout in seconds for getting all tools from MCP services")

    class Config:
        env_prefix = "MCP_"
        case_sensitive = True
        extra = "ignore"


class AgentSettings(BaseSettings):
    """ Settings for Agent integration """
    TIMEOUT: float = Field(10.0, description="Timeout in seconds for agent services")

    class Config:
        env_prefix = "AGENT_"
        case_sensitive = True
        extra = "ignore"


class ToolsSettings(BaseSettings):
    """ Settings for tools """
    RETRY_LIMIT: float = Field(10.0, description="Retry limit for tools")

    class Config:
        env_prefix = "TOOLS_"
        case_sensitive = True
        extra = "ignore"


class ServerSettings(BaseSettings):
    """ Server configuration settings """
    DEBUG: bool = Field(False, description="Enable debug mode")
    NAME: str = Field("AGIAgentic", description="Name of the server")
    HOST: str = Field("0.0.0.0", description="Host address for the server")
    PORT: int = Field(8000, description="Port number for the server")
    RELOAD: bool = Field(True, description="Enable auto-reload for the server")

    class Config:
        env_prefix = "SERVER_"
        case_sensitive = True
        extra = "ignore"


class ModelSettings(BaseSettings):
    """ Settings for model configurations """
    ZHIPU_API_KEY: str = Field("", description="API key for Zhipu models")
    ZHIPU_BASE_URL: str = Field("https://open.bigmodel.cn/api/paas/v4", description="Base URL for Zhipu API")
    SIMPLE_LLM: str = Field("glm-4-plus", description="Default simple LLM model name")
    REASON_LLM: str = Field("glm-4-plus", description="Default reasoning-capable LLM model name")
    CODE_LLM: str = Field("glm-4-plus", description="Default code generation LLM model name")
    EMBEDDING_MODEL: str = Field("embedding-3", description="Default embedding model name")

    

    class Config:
        env_prefix = "MODEL_"
        case_sensitive = True
        extra = "ignore"
