

from langchain.tools import BaseTool


class ToolService:
    
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._local_tools = None

    @property
    def local_tools(self) -> list[BaseTool]:
        """ Get local tools"""
        from main import app  # delayed import to avoid circular import at module load
        if self._local_tools is None:
            self._local_tools = getattr(app.state, "local_tools", [])
        return self._local_tools