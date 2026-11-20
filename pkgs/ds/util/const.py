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
# Why a Luna (2026-11-20, of what the work laptop's seat offers): the app's AI does simple
# tool calls (look up frame data, fill a form) and reports them, which the light tier
# handles at the lowest price. The others are built for more than that:
#   Terra  general mid tier, harder multi-step work    10x the price of gpt-6-luna
#   Sol    hard reasoning, long tool chains            20-40x
#   Codex  coding agents (writing and editing code)    about 20x
# Prices and the test: personal/ai/findings/github_copilot_api.md
# TODO: switch to "github-copilot:gpt-6-luna" (half the token price of gpt-5.6-luna, same
#   facts in our test) once pydantic-ai knows its context window: on 2.71.0 / genai-prices
#   0.2.5 it has none for Copilot, so the title bar's context meter loses its percent and its
#   hover (tests/ds/ai/test_model.py fails then). Also retest: it made more tool calls
DEFAULT_AI_MODEL: str = "github-copilot:gpt-5.6-luna"
