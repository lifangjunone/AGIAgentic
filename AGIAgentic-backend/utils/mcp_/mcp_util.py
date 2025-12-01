

from typing import Any, Dict


def serialize_tool(tool: Any) -> Dict[str, Any]:
    """Convert a tool object to a JSON-serializable dict.
    Args:
        t (Any): The tool object to serialize.
    Returns:
        dict: A dictionary representation of the tool.
    """
    try:
        return {
            "type": tool.__class__.__name__, # type: ignore
            "name": getattr(tool, "name", None), # type: ignore
            "description": getattr(tool, "description", None), # type: ignore
            "args_schema": getattr(tool, "args_schema", None), # type: ignore
            "response_format": getattr(tool, "response_format", None), # type: ignore
        }
    except Exception:
        # Fallback: return a safe string representation
        return {"type": "unknown", "repr": repr(tool)}