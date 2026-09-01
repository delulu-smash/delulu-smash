from __future__ import annotations

import os
import random

import polars as pl
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai_harness import Coder

# agent = Agent("openai:gpt-5.6-sol", capabilities=[Coder()])
agent = Agent("openai:gpt-5.6-sol")


class Person(BaseModel):
    name: str
    age: int
    city: str


@agent.tool_plain
def get_data(name: str) -> list[Person]:
    """Returns the data for the given name"""
    df = pl.DataFrame(
        {
            "name": [name, "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["New York", "Los Angeles", "Chicago"],
        }
    )
    return [Person(**r) for r in df.to_dicts()]
