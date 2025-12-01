



from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

from common.logger import logger
from utils.llm.llm_util import serialize_provider


router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/")
def get_llm(request: Request):
  """ Get LLM providers and implementations
  Args:
      request (Request): The FastAPI request object.
  Returns:
      dict: A dictionary containing the list of LLM providers and implementations.
  """
  llm_providers: Dict[str, Any] = getattr(request.app.state, "llm_providers", {})
  serializable = {k: serialize_provider(v) for k, v in llm_providers.items()}
  logger.debug(f"Fetching LLM providers, llm_providers: {serializable}")
  return JSONResponse({
      "llm_providers": serializable
  })



