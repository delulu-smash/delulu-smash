from __future__ import annotations

from pathlib import Path

REPO_DIR: Path = Path(__file__).parent.parent.parent.parent
ASSETS_DIR = REPO_DIR / "local" / "assets"
STAGING_ASSETS_DIR = ASSETS_DIR / "staging"
# delulu-smash's session log (git-ignored): written by services/ui/ui/debug_log.py, read by
# `ds ui debug` (ds.cli.ui_debug). Older parts sit next to it as ui.1.jsonl, ui.2.jsonl.
UI_LOG_FILE = REPO_DIR / "local" / "logs" / "ui" / "ui.jsonl"
# pydantic-ai model for ds.ai (agent + eval judge), via Pydantic AI Gateway (see ds.settings)
DEFAULT_AI_MODEL: str = "gateway/anthropic:claude-haiku-5-5"
