
from loguru import logger
from conf.config import config_manager


def initialize_logger():
  server_cfg = config_manager.server_config
  # 配置日志格式和级别
  logger.add(
      "logs/agiaagentic.log",
      rotation="10 MB",  # 每个日志文件最大10MB
      retention="10 days",  # 保留最近10天的日志
      compression="zip",  # 压缩旧日志文件
      format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
      level="DEBUG" if server_cfg.SERVER_DEBUG else "INFO",  # 日志级别
  ) 
  logger.bind(app=server_cfg.SERVER_NAME)
  return logger





