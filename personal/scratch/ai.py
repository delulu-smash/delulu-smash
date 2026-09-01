# result = agent.run_sync("create an example python file that make typer cli app")
# print(result.output)
from __future__ import annotations

from ds.ai.agent import agent

agent.to_cli_sync()
