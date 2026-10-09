from __future__ import annotations

import os
from pathlib import Path

import keyring
from pydantic import BaseModel, SecretStr

__all__ = ["get_settings"]

KEYRING_SERVICE_NAME: str = "delulu-smash"
# Local, git-ignored KEY=value file for non-keyring settings (eg SUPERMAJOR_ANON_KEY)
ENV_FILE: Path = Path(__file__).parent / ".env"


def _read_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    """Parse a simple KEY=value file (blank lines and # comments skipped); {} if missing"""
    if not path.is_file():
        return {}
    values = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("'\"")
    return values


_MAX_DISPLAY_LEN = 30


class OpenApiKey(SecretStr):
    """OpenAI API key (more user friendly printed secret)"""

    def _display(self) -> str:
        # Show the first 15 and last 4 characters (no longer than 30 characters),
        # which show up on the openai dashbaord
        secret_value = self.get_secret_value()
        if len(secret_value) > _MAX_DISPLAY_LEN:
            return f"{secret_value[:15]}{'*' * 11}{secret_value[-4:]}"
        suffix_start = max(15, len(secret_value) - 4)
        return f"{secret_value[:15]}{'*' * max(0, len(secret_value) - 19)}{secret_value[suffix_start:]}"


# TODO: look at use of https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
class Settings(BaseModel):
    """Application settings."""

    # OpenAI API key stored in keyring
    openai_api_key: OpenApiKey | None = None
    # supermajor.gg's public Supabase "anon" key (from the site's JS), for player tag search.
    # Read from $SUPERMAJOR_ANON_KEY or ENV_FILE (pkgs/ds/settings/.env, git-ignored)
    supermajor_anon_key: SecretStr | None = None


def set_settings(openai_api_key: str | None = None) -> None:
    """Set application settings. Secrets (eg api keys) stored in keyring"""
    global SETTINGS  # noqa: PLW0603  # module-level settings by design, read through get_settings()
    if openai_api_key is not None:
        keyring.set_password(KEYRING_SERVICE_NAME, "OPENAI_API_KEY", openai_api_key)
    # ensures global setting variable has updates
    SETTINGS = init_settings()


def init_settings() -> Settings:
    """Getting & Initializing settings  (eg setting ones to proper cli env variables)"""
    openai_api_key = keyring.get_password(KEYRING_SERVICE_NAME, "OPENAI_API_KEY")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    supermajor_anon_key = os.environ.get("SUPERMAJOR_ANON_KEY") or _read_env_file().get("SUPERMAJOR_ANON_KEY")
    return Settings(openai_api_key=openai_api_key, supermajor_anon_key=supermajor_anon_key)


def get_settings() -> Settings:
    """Return the current global settings (always up to date after set_settings())"""
    return SETTINGS


SETTINGS: Settings = init_settings()
