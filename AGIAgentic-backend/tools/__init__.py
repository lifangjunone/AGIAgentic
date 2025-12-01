
import pkgutil
import inspect
import importlib


from .time_tool import *
from typing import Any, List
from common.logger import logger
from langchain.tools import BaseTool


def nitialize_tool_manager() -> List[Any]:
    """ Auto collect and initialize all available tools 
    Returns:
        List[Any]: A list of initialized tool instances.
    """
    tools: List[Any] = []

    _package = __package__ or "tools"
    _path = __path__  # type: ignore
    logger.info(f"Collecting tools from package: {_package}, path: {_path}")
    for _, module_name, _ in pkgutil.iter_modules([_path[0]]):
        module = importlib.import_module(f"{_package}.{module_name}")
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, BaseTool):
                tools.append(obj)
                logger.info(f"Collected tool: {obj.name} from module: {module_name}")
    logger.info(f"Total tools collected: {len(tools)}")
    return tools