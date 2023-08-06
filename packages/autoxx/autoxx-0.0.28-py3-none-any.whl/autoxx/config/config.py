import os
import logging
import abc
from colorama import Fore
from typing import Optional
from dataclasses import dataclass
    
@dataclass
class OpenAIConfig:
    model: str
    api_key: str
    temperature: float = 0
    api_deployment_id: Optional[str] = None
    api_type: str = "open_ai"
    api_base: str = "https://api.openai.com/v1"
    api_version: Optional[str] = None

@dataclass
class GPTLLMModelConfig(OpenAIConfig):
    temperature: float = 0

@dataclass
class GPTEmbeddingModelConfig(OpenAIConfig):
    embedding_tokenizer: str = "cl100k_base"

def check_openai_api_key(api_key: str) -> None:
    """Check if the OpenAI API key is set in config.py or as an environment variable."""
    if not api_key or api_key == "":
        logging.error(
            Fore.RED
            + "Please set your OpenAI API key in .env or as an environment variable."
        )
        exit(1)

class Config():
    """
    Configuration class to store the state of bools for different scripts access.
    """

    def __init__(self) -> None:
        """Initialize the Config class"""
        self.debug_mode = False

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_models =   os.getenv("LLM_MODELS", "gpt-3.5-turbo,gpt-4").split(",")
        self.embedding_models = os.getenv("EMBEDDING_MODELS", "text-embedding-ada-002").split(",")
        self.model_config = {}
        for model in self.llm_models:
            self.set_llm_model_config(model)
        for model in self.embedding_models:
            self.set_embedding_model_config(model)

        self.browse_spacy_language_model = os.getenv(
            "BROWSE_SPACY_LANGUAGE_MODEL", "en_core_web_sm"
        )

        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.custom_search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_region = os.getenv("PINECONE_ENVIRONMENT")

        self.mongodb_host = os.getenv("MONGODB_HOST")
        self.mongodb_password = os.getenv("MONGODB_PASSWORD")
        self.mongodb_user = os.getenv("MONGODB_USER")

        # Selenium browser settings
        self.selenium_web_browser = os.getenv("USE_WEB_BROWSER", "chrome")
        self.selenium_headless = os.getenv("HEADLESS_BROWSER", "True") == "True"

        # User agent header to use when making HTTP requests
        # Some websites might just completely deny request with an error code if
        # no user agent was found.
        self.user_agent = os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        )
    
    def set_llm_model_config(self, model_name: str):
        model_uppercase = model_name.upper()

        model = os.getenv(f"{model_uppercase}_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv(f"{model_uppercase}_MODEL_API_KEY", self.openai_api_key)
        api_type = os.getenv(f"{model_uppercase}_MODEL_API_TYPE", "open_ai")
        api_base = os.getenv(f"{model_uppercase}_MODEL_API_BASE", "https://api.openai.com/v1")
        api_version = os.getenv(f"{model_uppercase}_MODEL_API_VERSION", None)
        api_deployment_id = os.getenv(f"{model_uppercase}_MODEL_API_DEPLOYMENT_ID", None)
        temperature = float(os.getenv(f"{model_uppercase}_MODEL_TEMPERATURE", 0))
        
        self.model_config[model_name] = GPTLLMModelConfig(
            model=model,
            api_key=api_key,
            api_type=api_type,
            api_base=api_base,
            api_version=api_version,
            api_deployment_id=api_deployment_id,
            temperature=temperature,
        )
        check_openai_api_key(api_type)

    def set_embedding_model_config(self, model_name:str):
        model_uppercase = model_name.upper()
        model = os.getenv(f"{model_uppercase}_MODEL",  model_name)
        api_key = os.getenv(f"{model_uppercase}_MODEL_API_KEY", self.openai_api_key)
        api_type = os.getenv(f"{model_uppercase}_MODEL_API_TYPE", "open_ai")
        api_base = os.getenv(f"{model_uppercase}_MODEL_API_BASE", "https://api.openai.com/v1")
        api_version = os.getenv(f"{model_uppercase}_MODEL_API_VERSION", None)
        api_deployment_id = os.getenv(f"{model_uppercase}_MODEL_API_DEPLOYMENT_ID", None)
        self.embedding_tokenizer = os.getenv(f"{model_uppercase}_EMBEDDING_TOKENIZER", "cl100k_base")
        
        self.model_config[model_name] = GPTEmbeddingModelConfig(
            model=model,
            api_key=api_key,
            api_type=api_type,
            api_base=api_base,
            api_version=api_version,
            api_deployment_id=api_deployment_id,
            embedding_tokenizer=self.embedding_tokenizer,
        )
        check_openai_api_key(api_key)

    def get_llm_model_config(self, model_name: str) -> GPTLLMModelConfig:
        if model_name not in self.model_config:
            raise ValueError(f"LLM Model {model_name} not found in config")
        return self.model_config[model_name]
    
    def get_embedding_model_config(self, model_name: str) -> GPTEmbeddingModelConfig:
        if model_name not in self.model_config:
            raise ValueError(f"Embedding Model {model_name} not found in config")
        return self.model_config[model_name]
    

class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class GlobalConfig(metaclass=Singleton):
    def __init__(self, cfg: Optional[Config] = None) -> None:
        if cfg is None:
            cfg = Config()
        self.config = cfg

    def set(self, cfg: Config) -> None:
        self.config = cfg

    def get(self) -> Config:
        return self.config