

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from common.logger import logger
from utils.tool.tool_util import serialize_tool


router = APIRouter(prefix="/local_tools", tags=["local_tools"])


@router.get("/")
def get_tools(request: Request):
  """ Get local tools
  Args:
      request (Request): The FastAPI request object.
  Returns:
      dict: A dictionary containing the list of local tools.
  """
  local_tools = getattr(request.app.state, "local_tools", [])
  serialized_tools = [serialize_tool(tool) for tool in local_tools]
  logger.debug(f"Fetching local tools, local_tools: {serialized_tools}")
  return JSONResponse({
      "local_tools": serialized_tools
  })



