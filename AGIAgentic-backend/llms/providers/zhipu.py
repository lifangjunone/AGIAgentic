

from pydantic import SecretStr
from typing import Union
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from common.logger import logger
from llms.providers import LLMProvider
from conf.config import config_manager


class ZhipuProvider(LLMProvider):
    """ Zhipu LLM provider implementation.
    """

    def get_llm(self, model_name: str, model_type: str = "chat") -> Union[ChatOpenAI, OpenAIEmbeddings]:
        """Retrieve a Zhipu LLM instance by model name.
        """
        # Placeholder for actual Zhipu LLM retrieval logic
        logger.info(f"Zhipu LLM instance for model: {model_name}")
        model_config = config_manager.model_config
        logger.debug(f"Using configuration: {model_config}")
        match model_type:
            case "embedding":
                logger.debug(f"Creating OpenAIEmbeddings with model: {model_name}")
                llm = OpenAIEmbeddings(
                    model=model_name,
                    api_key=SecretStr(model_config.ZHIPU_API_KEY),
                    base_url=model_config.ZHIPU_BASE_URL,
                )
            case "chat":
                logger.debug(f"Creating ChatOpenAI with model: {model_name}, base_url: {model_config.ZHIPU_BASE_URL}")
                llm = ChatOpenAI(
                    model=model_name,
                    api_key=SecretStr(model_config.ZHIPU_API_KEY),
                    base_url=model_config.ZHIPU_BASE_URL,
                    temperature=0.7
                )
            case _:
                logger.warning(f"Unknown model type '{model_type}', defaulting to 'chat'.")
                llm = ChatOpenAI(
                    model=model_name,
                    api_key=SecretStr(model_config.ZHIPU_API_KEY),
                    base_url=model_config.ZHIPU_BASE_URL,
                    temperature=0.7
                )
                
        logger.info(f"Successfully created {model_type} LLM instance: {model_name}")
        return llm
    

if __name__ == "__main__":
    provider = ZhipuProvider()
    llm_instance = provider.get_llm("glm-4-plus")
    print(llm_instance)