import openai
import os
from autogpt.config import Config
from typing import Optional

def setup_config(
        azure_config_file:Optional[str] = "",
        debug:bool = False,
) -> Config:
    CFG = Config()
    if azure_config_file != "":
        CFG.set_openai_api_key(os.getenv("AZURE_OPENAI_API_KEY", ""))
        CFG.use_azure=True
        CFG.load_azure_config(config_file=azure_config_file)

    CFG.set_debug_mode(debug)
    if CFG.google_api_key is None:
        CFG.set_google_api_key(os.getenv("GOOGLE_API_KEY", ""))
        CFG.set_custom_search_engine_id(os.getenv("CUSTOM_SEARCH_ENGINE_ID", ""))

    openai.api_type = CFG.openai_api_type
    openai.api_base = CFG.openai_api_base
    openai.api_version = CFG.openai_api_version
    openai.api_key = CFG.openai_api_key
    return CFG
