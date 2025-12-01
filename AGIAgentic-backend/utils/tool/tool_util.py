
from typing import Any, Dict
import inspect

try:
    from pydantic import BaseModel as PydanticBaseModel  # pydantic v1/v2
except Exception:
    PydanticBaseModel = None


def _serialize_args_schema(schema: Any) -> Any:
    """Convert args_schema (possibly a Pydantic model class) to a JSON-serializable form."""
    if schema is None:
        return None

    # If it's already a dict (schema), return as-is
    if isinstance(schema, dict):
        return schema # type: ignore

    # If it's a pydantic BaseModel class, convert to JSON schema
    if PydanticBaseModel and isinstance(schema, type) and issubclass(schema, PydanticBaseModel):
        # pydantic v2: model_json_schema, v1: schema
        if hasattr(schema, "model_json_schema"):
            try:
                return schema.model_json_schema()
            except Exception:
                pass
        if hasattr(schema, "schema"):
            try:
                return schema.schema() # type: ignore
            except Exception:
                pass
        # fallback to str
        return {"schema": str(schema)}

    # If it's an instance of a Pydantic model, dump to dict
    if PydanticBaseModel and isinstance(schema, PydanticBaseModel):
        try:
            # v2: model_dump, v1: dict()
            if hasattr(schema, "model_dump"):
                return schema.model_dump()
            return dict(schema)
        except Exception:
            return {"schema": str(schema)}

    # If it's a typing / other class, try to get its __name__ or str
    if inspect.isclass(schema): # type: ignore
        return {"schema_type": getattr(schema, "__name__", str(schema))} # type: ignore

    # Fallback: try to serialize primitive or repr
    try:
        import json

        json.dumps(schema)
        return schema
    except Exception:
        return {"schema": str(schema)}


def serialize_tool(tool: Any) -> Dict[str, Any]:
    """Convert a tool object (StructuredTool/BaseTool) to a JSON-serializable dict."""
    name = getattr(tool, "name", None) or getattr(tool, "__name__", None)
    description = getattr(tool, "description", None)
    response_format = getattr(tool, "response_format", None)
    args_schema = getattr(tool, "args_schema", None)

    serialized_schema = _serialize_args_schema(args_schema)

    return {
        "type": tool.__class__.__name__,
        "name": name,
        "description": description,
        "args_schema": serialized_schema,
        "response_format": response_format,
    }