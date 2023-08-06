"""Text processing functions"""
from math import ceil
from typing import Optional

import spacy
import tiktoken

from autoxx.config.config import GlobalConfig
from autoxx.utils.token_counter import count_string_tokens
from autoxx.utils.openai_models import OPEN_AI_MODELS

def batch(iterable, max_batch_length: int, overlap: int = 0):
    """Batch data from iterable into slices of length N. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if max_batch_length < 1:
        raise ValueError("n must be at least one")
    for i in range(0, len(iterable), max_batch_length - overlap):
        yield iterable[i : i + max_batch_length]

def _max_chunk_length(model: str, max: Optional[int] = None) -> int:
    model_max_input_tokens = OPEN_AI_MODELS[model].max_tokens - 1
    if max is not None and max > 0:
        return min(max, model_max_input_tokens)
    return model_max_input_tokens


def must_chunk_content(
    text: str, for_model: str, max_chunk_length: Optional[int] = None
) -> bool:
    return count_string_tokens(text, for_model) > _max_chunk_length(
        for_model, max_chunk_length
    )


def chunk_content(
    content: str,
    for_model: str,
    max_chunk_length: Optional[int] = None,
    with_overlap=True,
):
    """Split content into chunks of approximately equal token length."""

    MAX_OVERLAP = 200  # limit overlap to save tokens

    if not must_chunk_content(content, for_model, max_chunk_length):
        yield content, count_string_tokens(content, for_model)
        return

    max_chunk_length = max_chunk_length or _max_chunk_length(for_model)

    tokenizer = tiktoken.encoding_for_model(for_model)

    tokenized_text = tokenizer.encode(content)
    total_length = len(tokenized_text)
    n_chunks = ceil(total_length / max_chunk_length)

    chunk_length = ceil(total_length / n_chunks)
    overlap = min(max_chunk_length - chunk_length, MAX_OVERLAP) if with_overlap else 0

    for token_batch in batch(tokenized_text, chunk_length + overlap, overlap):
        yield tokenizer.decode(token_batch), len(token_batch)

def split_text(
    text: str,
    for_model: str = "gpt-3.5-turbo",
    with_overlap=True,
    max_chunk_length: Optional[int] = None,
):
    """Split text into chunks of sentences, with each chunk not exceeding the maximum length

    Args:
        text (str): The text to split
        for_model (str): The model to chunk for; determines tokenizer and constraints
        max_length (int, optional): The maximum length of each chunk

    Yields:
        str: The next chunk of text

    Raises:
        ValueError: when a sentence is longer than the maximum length
    """
    max_length = _max_chunk_length(for_model, max_chunk_length)

    # flatten paragraphs to improve performance
    text = text.replace("\n", " ")
    text_length = count_string_tokens(text, for_model)

    if text_length < max_length:
        yield text, text_length
        return

    n_chunks = ceil(text_length / max_length)
    target_chunk_length = ceil(text_length / n_chunks)

    nlp: spacy.language.Language = spacy.load(GlobalConfig().get().browse_spacy_language_model)
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    sentences = [sentence.text.strip() for sentence in doc.sents]

    current_chunk: list[str] = []
    current_chunk_length = 0
    last_sentence = None
    last_sentence_length = 0

    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        sentence_length = count_string_tokens(sentence, for_model)
        expected_chunk_length = current_chunk_length + 1 + sentence_length

        if (
            expected_chunk_length < max_length
            # try to create chunks of approximately equal size
            and expected_chunk_length - (sentence_length / 2) < target_chunk_length
        ):
            current_chunk.append(sentence)
            current_chunk_length = expected_chunk_length

        elif sentence_length < max_length:
            if last_sentence:
                yield " ".join(current_chunk), current_chunk_length
                current_chunk = []
                current_chunk_length = 0

                if with_overlap:
                    overlap_max_length = max_length - sentence_length - 1
                    if last_sentence_length < overlap_max_length:
                        current_chunk += [last_sentence]
                        current_chunk_length += last_sentence_length + 1
                    elif overlap_max_length > 5:
                        # add as much from the end of the last sentence as fits
                        current_chunk += [
                            list(
                                chunk_content(
                                    last_sentence,
                                    for_model,
                                    overlap_max_length,
                                )
                            ).pop()[0],
                        ]
                        current_chunk_length += overlap_max_length + 1

            current_chunk += [sentence]
            current_chunk_length += sentence_length

        else:  # sentence longer than maximum length -> chop up and try again
            sentences[i : i + 1] = [
                chunk
                for chunk, _ in chunk_content(sentence, for_model, target_chunk_length)
            ]
            continue

        i += 1
        last_sentence = sentence
        last_sentence_length = sentence_length

    if current_chunk:
        yield " ".join(current_chunk), current_chunk_length