

from typing_extensions import Self
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from typing import Optional, Type, TypeVar, cast, Dict, Any

from common.logger import logger
from llms.providers import LLMProvider
from conf.config import config_manager


T = TypeVar("T", bound=object)


# Global provider storage

_PROVIDERS: Dict[str, LLMProvider] = {}


class LLMService:
    """Service class for managing LLM interactions."""

    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, llm_provider_name: str = "zhipu"):
        """ Initialize the LLM service with a specific provider.
        Args:
            llm_provider (LLMProvider): The name of the LLM provider to use.
        """
        self.llm_provider_name = llm_provider_name
        self._simple_llm: Optional[ChatOpenAI] = None
        self._reason_llm: Optional[ChatOpenAI] = None
        self._code_llm: Optional[ChatOpenAI] = None
        self._embedding_model: Optional[OpenAIEmbeddings] = None
        self.model_config = config_manager.model_config

    def _ensure_provider(self) -> LLMProvider:
        if _PROVIDERS.get(self.llm_provider_name) is None:
            from main import app  # delayed import to avoid circular import at module load
            providers = getattr(app.state, "llm_providers", {})
            _provider = providers.get(self.llm_provider_name)
            if not _provider:
                logger.error(f"LLM provider '{self.llm_provider_name}' not found.")
                raise ValueError(f"LLM provider '{self.llm_provider_name}' not found.")
            _PROVIDERS[self.llm_provider_name] = _provider
        return _PROVIDERS[self.llm_provider_name]

    def _get_and_validate(self, config_attr: str, expected_type: Type[T], model_type: str = "chat") -> T:
        """Generic helper to fetch a model name from model_config, request the provider and validate type."""
        provider = self._ensure_provider()
        model_name = getattr(self.model_config, config_attr)
        logger.debug(f"Requesting model '{model_name}' (type={model_type}) from provider '{self.llm_provider_name}'")
        inst = provider.get_llm(model_name, model_type=model_type)
        # Validate the type of the returned instance
        if not isinstance(inst, expected_type):
            logger.error(f"{config_attr} must be an instance of {expected_type.__name__}, got {type(inst).__name__}")
            raise TypeError(f"{config_attr} must be an instance of {expected_type.__name__}, got {type(inst).__name__}")
        # cast(T, inst) 用于显式地将T对象转换为inst的类型
        return cast(T, inst)
    
    @property
    def simple_llm(self) -> ChatOpenAI:
        """Get a simple chat LLM (ChatOpenAI)."""
        if self._simple_llm is None:
            self._simple_llm = self._get_and_validate("SIMPLE_LLM", ChatOpenAI, model_type="chat")
        return self._simple_llm

    @property
    def reason_llm(self) -> ChatOpenAI:
        """Get a reasoning-capable ChatOpenAI instance."""
        if self._reason_llm is None:
            self._reason_llm = self._get_and_validate("REASON_LLM", ChatOpenAI, model_type="chat")
        return self._reason_llm

    @property
    def code_llm(self) -> ChatOpenAI:
        """Get a code-generation ChatOpenAI instance."""
        if self._code_llm is None:
            self._code_llm = self._get_and_validate("CODE_LLM", ChatOpenAI, model_type="chat")
        return self._code_llm

    @property
    def embedding_llm(self) -> OpenAIEmbeddings:
        """Get an embedding model (OpenAIEmbeddings)."""
        if self._embedding_model is None:
            self._embedding_model = self._get_and_validate("EMBEDDING_MODEL", OpenAIEmbeddings, model_type="embedding")
        return self._embedding_model


    