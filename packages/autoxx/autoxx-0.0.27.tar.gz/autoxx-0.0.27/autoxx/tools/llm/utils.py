from typing import Dict, List, Dict
from autogpt.llm_utils import create_chat_completion

def create_message(prompt: str) -> List[Dict]:
    """Create a message for the chat completion

    Args:
        chunk (str): The chunk of text to summarize
        question (str): The question to answer

    Returns:
        Dict[str, str]: The message to send to the chat completion
    """
    return [
        {
            "role": "system",
            "content": "You are an AI assistant."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

class llm_uils:

    model: str

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model

    def text_completion(self, prompt: str) -> str:
        messages = create_message(prompt)
        response = create_chat_completion(
            model=self.model,
            messages=messages,
        )

        return response