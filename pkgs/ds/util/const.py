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
# Why gpt-6-luna (2026-11-20, of what the work laptop's seat offers): the app's AI does
# simple tool calls (look up frame data, fill a form) and reports them, which the light tier
# handles; it is the cheapest, at half the token price of gpt-5.6-luna with the same facts in
# our test. The others are built for more than that:
#   Terra  general mid tier, harder multi-step work    10x the price
#   Sol    hard reasoning, long tool chains            20-40x
#   Codex  coding agents (writing and editing code)    about 20x
# Prices and the test: personal/ai/findings/github_copilot_api.md
DEFAULT_AI_MODEL: str = "github-copilot:gpt-6-luna"
