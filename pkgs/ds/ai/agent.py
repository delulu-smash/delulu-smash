from __future__ import annotations

import polars as pl
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai_harness import Coder  # noqa: F401  # used by the commented-out Coder agent below

from ds.ai.smashdb import smashdb_capability

__all__ = ["agent"]
# agent = Agent("openai:gpt-5.6-sol", capabilities=[Coder()])  # noqa: ERA001  # alt config
agent = Agent("openai:gpt-5.6-sol", capabilities=[smashdb_capability])


class Person(BaseModel):
    name: str
    age: int
    city: str


# NOTE: below serves as example
# @agent.tool_plain
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
