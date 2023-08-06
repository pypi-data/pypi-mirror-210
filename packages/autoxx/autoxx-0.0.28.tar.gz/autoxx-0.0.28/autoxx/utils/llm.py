from typing import List, Dict
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
from autoxx.config.config import GlobalConfig
from autoxx.utils.base import Message

def create_message(prompt: str) -> List[Message]:
    """Create a message for the chat completion

    Args:
        chunk (str): The chunk of text to summarize
        question (str): The question to answer

    Returns:
        Dict[str, str]: The message to send to the chat completion
    """
    return [
        Message(role="system", content="You are an AI assistant."), 
        Message(role="user", content=prompt)
    ]

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
def get_embeddings(
    texts: List[str], 
    model:str = "text-embedding-ada-002",
    **kwargs,
) -> List[List[float]]:
    """
    Embed texts using OpenAI's ada model.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # Call the OpenAI API to get the embeddings
    config = GlobalConfig().get()
    embed_model_config = config.get_embedding_model_config(model)
    response = openai.Embedding.create(
        input=texts,
        model=embed_model_config.model,
        deployment_id=embed_model_config.api_deployment_id,
        api_key=embed_model_config.api_key,
        api_base=embed_model_config.api_base,
        api_type=embed_model_config.api_type,
        api_version=embed_model_config.api_version,
        request_timeout=10,
    )

    # Extract the embedding data from the response
    data = response["data"]  # type: ignore

    # Return the embeddings as a list of lists of floats
    return [result["embedding"] for result in data]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
def get_chat_completion(
    messages: List[Message],
    model="gpt-3.5-turbo",  # use "gpt-4" for better results
    **kwargs,
):
    """
    Generate a chat completion using OpenAI's chat completion API.

    Args:
        messages: The list of messages in the chat history.
        model: The name of the model to use for the completion. Default is gpt-3.5-turbo, which is a fast, cheap and versatile model. Use gpt-4 for higher quality but slower results.

    Returns:
        A string containing the chat completion.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # call the OpenAI chat completion API with the given messages
    config = GlobalConfig().get()
    llm_model_config = config.get_llm_model_config(model)
    response = openai.ChatCompletion.create(
        deployment_id=llm_model_config.api_deployment_id,
        model=llm_model_config.model,
        messages= [message.raw() for message in messages],
        api_key=llm_model_config.api_key,
        api_base=llm_model_config.api_base,
        api_type=llm_model_config.api_type,
        api_version=llm_model_config.api_version,
         request_timeout=30,
    )

    choices = response["choices"]  # type: ignore
    completion = choices[0].message.content.strip()
    return completion