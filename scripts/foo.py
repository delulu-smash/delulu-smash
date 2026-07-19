from __future__ import annotations

from ds.ai import chat
from pydantic import BaseModel

messages = [{"role": "user", "content": "John is 35 years old"}]


class User(BaseModel):
    name: str
    age: int


user = chat(messages=messages, response_format=User)
print(user)
