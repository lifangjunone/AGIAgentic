

from pydantic import SecretStr
from langchain_openai import ChatOpenAI

from common.logger import logger
from llms.providers import LLMProvider
from conf.config import config_manager


class ZhipuProvider(LLMProvider):
    """ Zhipu LLM provider implementation.
    """

    def get_llm(self, model_name: str) -> ChatOpenAI:
        """Retrieve a Zhipu LLM instance by model name.
        """
        # Placeholder for actual Zhipu LLM retrieval logic
        logger.info(f"Zhipu LLM instance for model: {model_name}")
        model_config = config_manager.model_config
        logger.debug(f"Using configuration: {model_config}")
        llm = ChatOpenAI(
            model=model_name,
            api_key=SecretStr(model_config.ZHIPU_API_KEY),
            base_url=model_config.ZHIPU_BASE_URL
        )
        return llm
    

if __name__ == "__main__":
    provider = ZhipuProvider()
    llm_instance = provider.get_llm("glm-4-plus")
    print(llm_instance)