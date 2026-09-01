from __future__ import annotations

import os

import keyring
from pydantic import BaseModel, SecretStr

__all__ = ["get_settings"]

KEYRING_SERVICE_NAME: str = "delulu-smash"


class OpenApiKey(SecretStr):
    """OpenAI API key (more user friendly printed secret)"""

    def _display(self) -> str:
        # print with first 15 characters rest * (no longer than 30 characters)
        secret_value = self.get_secret_value()
        if len(secret_value) > 30:
            return f"{secret_value[:15]}{'*' * 15}"
        return f"{secret_value[:15]}{'*' * (len(secret_value) - 15)}"


# TODO: look at use of https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
class Settings(BaseModel):
    """Application settings."""

    # OpenAI API key stored in keyring
    openai_api_key: OpenApiKey | None = None


def set_settings(openai_api_key: str | None = None) -> None:
    """Set application settings. Secrets (eg api keys) stored in keyring"""
    global SETTINGS
    if openai_api_key is not None:
        keyring.set_password(KEYRING_SERVICE_NAME, "OPENAI_API_KEY", openai_api_key)
    # ensures global setting variable has updates
    SETTINGS = init_settings()


def init_settings() -> Settings:
    """Getting & Initializing settings  (eg setting ones to proper cli env variables)"""
    openai_api_key = keyring.get_password(KEYRING_SERVICE_NAME, "OPENAI_API_KEY")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    return Settings(openai_api_key=openai_api_key)


def get_settings() -> Settings:
    """Return the current global settings (always up to date after set_settings())"""
    return SETTINGS


SETTINGS: Settings = init_settings()
