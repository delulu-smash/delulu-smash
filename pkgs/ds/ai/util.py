from __future__ import annotations

from litellm import completion
from pydantic import BaseModel

__all__ = ["chat"]


def chat(
    messages: list[dict], model: str = "gpt-5.4-mini", response_format: type[BaseModel] | None = None
) -> BaseModel | dict:
    """
    Send a chat message to the specified model and return the response.

    Args:
        messages (list[dict]): A list of messages in the format [{"role": "user", "content": "Hello"}].
        model (str): The model to use for the chat. Default is "gpt-5.4-mini".
        response_format (type[BaseModel] | None): If provided, the response will be validated against this Pydantic model.

    Returns
    -------
        BaseModel | dict: The response from the model, either as a Pydantic model or a raw dictionary.
    """
    resp = completion(model=model, messages=messages, response_format=response_format)
    if response_format:
        return response_format.model_validate_json(resp.choices[0].message.content)
    return resp.choices[0].message.content
