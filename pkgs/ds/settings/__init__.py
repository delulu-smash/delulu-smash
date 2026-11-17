from __future__ import annotations

import os

import keyring
from pydantic import BaseModel, SecretStr

__all__ = ["get_settings"]

KEYRING_SERVICE_NAME: str = "delulu-smash"
# Pydantic AI Gateway, US region like the Logfire project (`gateway/...` models read env vars)
GATEWAY_BASE_URL: str = "https://gateway-us.pydantic.dev/proxy"

_MAX_DISPLAY_LEN = 30


class ApiKey(SecretStr):
    """API key secret, printed partially masked (friendlier than SecretStr's '**********')"""

    def _display(self) -> str:
        # Show the first 15 and last 4 characters (no longer than 30 characters),
        # enough to match the key against its provider dashboard
        secret_value = self.get_secret_value()
        if len(secret_value) > _MAX_DISPLAY_LEN:
            return f"{secret_value[:15]}{'*' * 11}{secret_value[-4:]}"
        suffix_start = max(15, len(secret_value) - 4)
        return f"{secret_value[:15]}{'*' * max(0, len(secret_value) - 19)}{secret_value[suffix_start:]}"


# TODO: look at use of https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
class Settings(BaseModel):
    """Application settings."""

    # Two Pydantic (Logfire) keys in keyring:
    # project key: all ds.ai model calls (the Gateway, as PYDANTIC_AI_GATEWAY_API_KEY) and
    # ds.data.raw.logfire (AI spend queries over the project's traces)
    pydantic_project_api_key: ApiKey | None = None
    # organization key: ds.data.raw.gateway only (spending limits; the Gateway refuses it)
    pydantic_org_api_key: ApiKey | None = None
    # start.gg personal API token in keyring; used by ds.data.raw.startgg (create one at
    # https://start.gg/admin/profile/developer)
    startgg_api_token: ApiKey | None = None


def set_settings(
    pydantic_org_api_key: str | None = None,
    pydantic_project_api_key: str | None = None,
    startgg_api_token: str | None = None,
) -> None:
    """Set application settings. Secrets (eg api keys) go in keyring; None keeps a value"""
    global SETTINGS  # noqa: PLW0603  # module-level settings by design, read through get_settings()
    if startgg_api_token is not None:
        keyring.set_password(KEYRING_SERVICE_NAME, "STARTGG_API_TOKEN", startgg_api_token)
    if pydantic_project_api_key is not None:
        keyring.set_password(KEYRING_SERVICE_NAME, "PYDANTIC_PROJECT_API_KEY", pydantic_project_api_key)
    if pydantic_org_api_key is not None:
        keyring.set_password(KEYRING_SERVICE_NAME, "PYDANTIC_ORG_API_KEY", pydantic_org_api_key)
    # ensures global setting variable has updates
    SETTINGS = init_settings()


def init_settings() -> Settings:
    """Getting & Initializing settings  (eg setting ones to proper cli env variables)"""
    pydantic_project_api_key = keyring.get_password(KEYRING_SERVICE_NAME, "PYDANTIC_PROJECT_API_KEY")
    if pydantic_project_api_key:
        # pydantic-ai's `gateway/...` models read the key from this variable
        os.environ["PYDANTIC_AI_GATEWAY_API_KEY"] = pydantic_project_api_key
    # setdefault so an explicitly exported URL (eg another region) still wins
    os.environ.setdefault("PYDANTIC_AI_GATEWAY_BASE_URL", GATEWAY_BASE_URL)
    # an exported STARTGG_API_TOKEN wins over the keyring (eg CI, a one-off shell)
    startgg_api_token = os.environ.get("STARTGG_API_TOKEN") or keyring.get_password(
        KEYRING_SERVICE_NAME, "STARTGG_API_TOKEN"
    )
    return Settings(
        pydantic_project_api_key=pydantic_project_api_key or None,
        pydantic_org_api_key=keyring.get_password(KEYRING_SERVICE_NAME, "PYDANTIC_ORG_API_KEY") or None,
        startgg_api_token=startgg_api_token or None,
    )


def get_settings() -> Settings:
    """Return the current global settings (always up to date after set_settings())"""
    return SETTINGS


SETTINGS: Settings = init_settings()
