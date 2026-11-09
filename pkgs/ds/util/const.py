from __future__ import annotations

from pathlib import Path

REPO_DIR: Path = Path(__file__).parent.parent.parent.parent
ASSETS_DIR = REPO_DIR / "local" / "assets"
STAGING_ASSETS_DIR = ASSETS_DIR / "staging"
# pydantic-ai model for ds.ai (agent + eval judge), via Pydantic AI Gateway (see ds.settings)
DEFAULT_AI_MODEL: str = "gateway/anthropic:claude-haiku-5-5"
