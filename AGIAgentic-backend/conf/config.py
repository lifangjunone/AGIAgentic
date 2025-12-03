
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional, Type, TypeVar, Any

from .setting import (
    MCPSettings, AgentSettings, ToolsSettings, ServerSettings, ModelSettings
)


T = TypeVar("T", bound=BaseSettings)

class ConfigManager:
    """ Configuration manager for all settings """

    _instance: Optional["ConfigManager"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, env_file: Optional[str] = None):
        self._env_file = env_file or os.getenv("ENV_FILE_PATH", ".env")  # 默认 .env 文件路径
        self._server_config: Optional[ServerSettings] = None
        self._mcp_config: Optional[MCPSettings] = None
        self._agent_config: Optional[AgentSettings] = None
        self._tools_config: Optional[ToolsSettings] = None
        self._model_config: Optional[ModelSettings] = None

    def _load_config(self, config_class: Type[T]) -> T:
        """ 动态加载配置类 
        Args:
            config_class (Type[BaseSettings]): 需要加载的配置类
        Returns:
            BaseSettings: 加载后的配置实例
        """
        return config_class(env_file=self._env_file)  # 通过传递 env_file 加载配置
    
    @property
    def server_config(self) -> ServerSettings:
        if self._server_config is None:
            self._server_config = self._load_config(ServerSettings)
        return self._server_config

    @property
    def mcp_config(self) -> MCPSettings:
        if self._mcp_config is None:
            self._mcp_config = self._load_config(MCPSettings)
        return self._mcp_config

    @property
    def agent_config(self) -> AgentSettings:
        if self._agent_config is None:
            self._agent_config = self._load_config(AgentSettings)
        return self._agent_config

    @property
    def tools_config(self) -> ToolsSettings:
        if self._tools_config is None:
            self._tools_config = self._load_config(ToolsSettings)
        return self._tools_config
    
    @property
    def model_config(self) -> ModelSettings:
        if self._model_config is None:
            self._model_config = self._load_config(ModelSettings)
        return self._model_config
    

def initialize_config_manager(env_file: Optional[str] = None) -> ConfigManager:
    """ Initialize the global configuration manager """
    run_env = os.getenv("RUN_ENV", "")
    env_file_path = f"{run_env}.env"
    if os.path.exists(env_file_path):
        print("🔄 Loading environment variables from:", env_file_path)
        load_dotenv(env_file_path)
    config_manager = ConfigManager(env_file=env_file_path)
    config_manager.server_config  # 预加载服务器配置
    config_manager.mcp_config     # 预加载MCP配置
    config_manager.agent_config   # 预加载Agent配置
    config_manager.tools_config   # 预加载工具配置
    config_manager.model_config   # 预加载模型配置
    return config_manager


# Global configuration manager instance
config_manager = initialize_config_manager()





