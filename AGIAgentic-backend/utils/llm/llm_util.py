from typing import Any, Dict
import inspect


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
