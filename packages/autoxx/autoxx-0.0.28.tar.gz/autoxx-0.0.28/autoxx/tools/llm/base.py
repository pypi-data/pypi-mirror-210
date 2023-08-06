from autoxx.utils.llm import get_chat_completion, create_message

class llm_uils:

    model: str

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model

    def text_completion(self, prompt: str) -> str:
        messages = create_message(prompt)
        response = get_chat_completion(
            messages=messages,
            model=self.model
        )

        return response
