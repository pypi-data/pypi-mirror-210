import openai
from autoxx.config.config import Config, GlobalConfig

def setup_config(
        debug:bool = False,
) -> Config:
    CFG = Config()
    GlobalConfig().set(CFG)
    openai.api_key = CFG.openai_api_key
    return CFG
