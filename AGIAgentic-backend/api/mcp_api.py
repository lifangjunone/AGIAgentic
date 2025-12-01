

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from common.logger import logger
from utils.mcp_.mcp_util import serialize_tool


router = APIRouter(prefix="/mcp_tools", tags=["mcp_tools"])


@router.get("/")
def get_tools(request: Request):
  """ Get MCP tools
  Args:
      request (Request): The FastAPI request object.
  Returns:
      dict: A dictionary containing the list of MCP tools.
  """
  mcp_tools = getattr(request.app.state, "mcp_tools", [])
  serialized_tools = [serialize_tool(tool) for tool in mcp_tools]
  logger.debug(f"Fetching MCP tools, mcp_tools: {serialized_tools}")
  return JSONResponse({
      "mcp_tools": serialized_tools
  })



