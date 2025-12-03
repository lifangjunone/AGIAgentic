
import json
import inspect


from typing import Any, Dict



def serialize_provider(provider: Any) -> Dict[str, Any]:
    """Convert provider object to JSON-serializable dict."""
    try:
        methods = [
            name
            for name, _ in inspect.getmembers(provider, predicate=inspect.isroutine)
            if not name.startswith("_")
        ]
        description = getattr(provider, "description", None)
        if not description:
            doc = getattr(provider, "__doc__", None)
            description = doc.strip() if isinstance(doc, str) else None

        return {
            "type": provider.__class__.__name__ if hasattr(provider, "__class__") else type(provider).__name__,
            "repr": repr(provider),
            "has_get_llm": callable(getattr(provider, "get_llm", None)),
            "methods": methods,
            "description": description,
        }
    except Exception as e:
        # return minimal serializable info on error
        return {"type": "unknown", "repr": repr(provider), "error": str(e)}
    
def serializable_llm_result(obj: Any) -> Any:
      """Recursively convert various LLM response objects to JSON-serializable structures."""
      # primitives
      if obj is None or isinstance(obj, (str, int, float, bool)):
          return obj
      # dict / list / tuple
      if isinstance(obj, dict):
          return json.dumps({k: serializable_llm_result(v) for k, v in obj.items()}, ensure_ascii=False) # type: ignore
      if isinstance(obj, (list, tuple, set)):
          return json.dumps([serializable_llm_result(v) for v in obj], ensure_ascii=False) # type: ignore
  
      # common attributes returned by langchain/langchain_core LLM outputs
      for attr in ("content", "text", "message", "data", "value"):
          if hasattr(obj, attr):
              try:
                  return serializable_llm_result(getattr(obj, attr))
              except Exception:
                  pass
  
      # generations / generation lists
      if hasattr(obj, "generations"):
          try:
              gens = getattr(obj, "generations")
              return serializable_llm_result(gens)
          except Exception:
              pass
      if hasattr(obj, "generation"):
          try:
              return serializable_llm_result(getattr(obj, "generation"))
          except Exception:
              pass
  
      # pydantic models
      if hasattr(obj, "model_dump"):
          try:
              return serializable_llm_result(obj.model_dump())
          except Exception:
              pass
      if hasattr(obj, "dict"):
          try:
              return serializable_llm_result(obj.dict())
          except Exception:
              pass
      if hasattr(obj, "to_dict"):
          try:
              return serializable_llm_result(obj.to_dict())
          except Exception:
              pass
  
      # try JSON round-trip
      try:
          return json.dumps(obj)
      except Exception:
          return repr(obj)
  
