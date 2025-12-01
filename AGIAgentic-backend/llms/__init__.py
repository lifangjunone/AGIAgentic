

import pkgutil
import inspect

from typing import Any, Dict

from common.logger import logger
from llms.providers import LLMProvider


def initialize_model_manager() -> Dict[str, Any]:
  """ Auto collect and initialize all available models
  Returns:
      List[Any]: A list of initialized model instances.
  """

  provider_models: Dict[str, Any] = dict()

  _package = f"{__package__}.providers" or "llms.providers"
  _path = f"{__path__[0]}/providers"  # type: ignore
  logger.info(f"Collecting model providers from package: {_package}, path: {_path}")
  for _, module_name, _ in pkgutil.iter_modules([_path]):
      logger.debug(f"Importing module: {_package}.{module_name}")
      module = __import__(f"{_package}.{module_name}", fromlist=[''])
      for _, obj in inspect.getmembers(module):
          if inspect.isclass(obj) and issubclass(obj, LLMProvider) and obj is not LLMProvider:
              provider_instance = obj()
              provider_models[module_name] = provider_instance
              logger.info(f"Collected model provider: {module_name} with instance: {provider_instance}")
  return provider_models