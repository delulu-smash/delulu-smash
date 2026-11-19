from __future__ import annotations

from pathlib import Path

REPO_DIR: Path = Path(__file__).parent.parent.parent.parent
ASSETS_DIR = REPO_DIR / "local" / "assets"
STAGING_ASSETS_DIR = ASSETS_DIR / "staging"
# The model of every AI agent in the repo (ds.ai, the app's inline chats, the eval judge): the
# one line to change. ds.ai.model.ai_model() turns it into what an Agent gets:
#   "github-copilot:<id>"         a GitHub Copilot seat (token: `ds settings sync`); ids:
#                                 `models` in experimental/copilot_agent/copilot_agent.py
#   "gateway/<provider>:<model>"  the Pydantic AI Gateway (key: `ds settings sync`), eg
#                                 "gateway/anthropic:claude-haiku-5-5", the default on `main`
DEFAULT_AI_MODEL: str = "github-copilot:gpt-5.6-luna"
