from __future__ import annotations

import polars as pl
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai_harness import Coder  # noqa: F401  # used by the commented-out Coder agent below

from ds.ai.knowledge import knowledge_capability
from ds.ai.little_mac import little_mac_capability
from ds.ai.mechanics import mechanics_capability
from ds.ai.smashdb import smashdb_capability
from ds.ai.supermajor import supermajor_capability

__all__ = ["agent"]
# agent = Agent("openai:gpt-5.6-sol", capabilities=[Coder()])  # noqa: ERA001  # alt config
# TODO: transfer specific smash ultimate engine items to docs/smashDb (eg 1v1 base multiplier)
# always-on (capabilities are deferred), so match assumptions apply to every answer
# ds::docs-source: none yet (no 1v1 multiplier docs page; 1.2 also in ds.calc.modifiers)
_INSTRUCTIONS = """\
Assume a competitive Super Smash Bros. Ultimate 1v1 (singles) match unless the user says otherwise (eg doubles,
FFA, 3+ players). In 1v1 the game multiplies all damage by 1.2x:
- Frame-data damage (SmashDb basedamage, ultimateframedata) is listed WITHOUT this multiplier, so multiply by 1.2
  for any 1v1 damage number or damage calc (combo damage, KO percents, armor thresholds, etc).
- Show the 1v1 value first and the listed base value alongside it, eg "Jab 1: 1.8% in 1v1 (1.5% base)", so the
  user can check it against the source.
- The multiplier stacks with other modifiers (eg stale moves): 1v1 damage = base x 1.2 x staleness factor.
- If the user mentions doubles, FFA or 3+ players, drop the 1.2x and say so."""

agent = Agent(
    "openai:gpt-5.6-sol",
    instructions=_INSTRUCTIONS,
    capabilities=[
        knowledge_capability,
        smashdb_capability,
        mechanics_capability,
        little_mac_capability,
        supermajor_capability,
    ],
)


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
