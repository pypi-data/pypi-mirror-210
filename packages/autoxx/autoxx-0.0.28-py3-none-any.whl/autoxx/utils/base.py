from dataclasses import dataclass
from typing import Literal, TypedDict

MessageRole = Literal["system", "user", "assistant"]

class MessageDict(TypedDict):
    role: MessageRole
    content: str

@dataclass
class Message:
    """OpenAI Message object containing a role and the message content"""

    role: MessageRole
    content: str

    def raw(self) -> MessageDict:
        return {"role": self.role, "content": self.content}

@dataclass
class ModelInfo:
    """Struct for model information.

    Would be lovely to eventually get this directly from APIs, but needs to be scraped from
    websites for now.

    """

    name: str
    prompt_token_cost: float
    completion_token_cost: float
    max_tokens: int


@dataclass
class ChatModelInfo(ModelInfo):
    """Struct for chat model information."""

    pass


@dataclass
class TextModelInfo(ModelInfo):
    """Struct for text completion model information."""

    pass


@dataclass
class EmbeddingModelInfo(ModelInfo):
    """Struct for embedding model information."""

    embedding_dimensions: int