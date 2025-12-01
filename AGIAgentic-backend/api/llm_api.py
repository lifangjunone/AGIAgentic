



from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Union
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from common.logger import logger
from services.llm import LLMService
from utils.llm.llm_util import serialize_provider, serializable_llm_result



router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/providers")
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

@router.get("/{provider_name}/{model_type}")
def get_model(request: Request, provider_name: str, model_type: str):
    """ Get model information for a specific provider and model type.
    Args:
        request (Request): The FastAPI request object.
        provider_name (str): The name of the LLM provider.
        model_type (str): The type of the model (e.g., "chat", "embedding").
    Returns:
        dict: A dictionary containing the model information.
    """

    llm_service = LLMService(provider_name)
    model_type = f"{model_type}_llm"
    model_instance = getattr(llm_service, model_type, None)
    if model_instance is None:
        logger.error(f"Model type '{model_type}' not found for provider '{provider_name}'.")
        return JSONResponse({
            "error": f"Model type '{model_type}' not found for provider '{provider_name}'."
        })
    return JSONResponse({
        "provider": provider_name,
        "model_type": model_type,
        "model_name": serialize_provider(model_instance)
    })

@router.post("/{provider_name}/{model_type}/debug")
def debug_model(
      request: Request, 
      provider_name: str, 
      model_type: str,
      query: str
    ):
    """ Debug model information for a specific provider and model type.
    Args:
        request (Request): The FastAPI request object.
        provider_name (str): The name of the LLM provider.
        model_type (str): The type of the model (e.g., "chat", "embedding").
        query (str): The input query for debugging the model.
    Returns:
        dict: A dictionary containing the debug information of the model.
    """

    logger.info(f"Debugging model '{model_type}' from provider '{provider_name}' with query: {query}")
    llm_service = LLMService(provider_name)
    llm = f"{model_type}_llm"
    model_instance: Union[ChatOpenAI, OpenAIEmbeddings, None] = getattr(llm_service, llm, None)
    if model_instance is None:
        logger.error(f"Model type '{model_type}' not found for provider '{provider_name}'.")
        return JSONResponse({
            "error": f"Model type '{model_type}' not found for provider '{provider_name}'."
        })
    match model_type:
        case "embedding":
            res = model_instance.embed_query(query) # type: ignore
        case _: 
            res = model_instance.invoke(query) # type: ignore
    logger.debug(f"Debugging model '{llm}' from provider '{provider_name}' with query '{query}': {res}")
    return JSONResponse({
        "provider": provider_name,
        "model_type": model_type,
        "model": llm,
        "model_debug_info": serializable_llm_result(res)
    })

