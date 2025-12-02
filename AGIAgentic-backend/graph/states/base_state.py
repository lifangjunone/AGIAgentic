

from typing import List, Dict, Any, TypedDict

from langchain_core.messages import BaseMessage

class BaseState(TypedDict):
    """ A base structure to represent generic graph states. """
    # base attributes can be defined here if needed

    # messages to store conversation history
    messages: List[BaseMessage]
    # streaming chunks for real-time updates
    streaming_chunks: List[Dict[str, Any]]

    # state metadata
    status: str
    error: str

    # context information
    request_id: str
    user_id: str
    session_id: str

    # additional data
    timing_info: Dict[str, Any]