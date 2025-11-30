import os

from typing import Optional, Type, TypeVar
from pydantic_settings import BaseSettings

from .setting import MCPSettings, AgentSettings, ToolsSettings


T = TypeVar("T", bound=BaseSettings)

class ConfigManager:
    """ Configuration manager for all settings """

    def __init__(self, env_file: Optional[str] = None):
        self._env_file = env_file or os.getenv("ENV_FILE_PATH", ".env")  # 默认 .env 文件路径
        self._mcp_config: Optional[MCPSettings] = None
        self._agent_config: Optional[AgentSettings] = None
        self._tools_config: Optional[ToolsSettings] = None

    def _load_config(self, config_class: Type[T]) -> T:
        """ 动态加载配置类 
        Args:
            config_class (Type[BaseSettings]): 需要加载的配置类
        Returns:
            BaseSettings: 加载后的配置实例
        """
        return config_class(_env_file=self._env_file)  # 通过传递 env_file 加载配置

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
    

# 初始化配置管理器时，可以传递自定义的 .env 文件路径
run_env = os.getenv("RUN_ENV", "development")
env_file_path = f"env/{run_env}.env"
config_manager = ConfigManager(env_file=env_file_path)
