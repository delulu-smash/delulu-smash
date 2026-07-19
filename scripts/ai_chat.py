from __future__ import annotations

import os
from pathlib import Path

from litellm import completion
from pydantic import BaseModel


def _load_openai_key_from_file(path: str | Path = "local/openai.secret") -> str | None:
    """Load OpenAI API key from a gitignored local file (if present).

    The file may contain a raw key, or a KEY=VALUE pair (for example
    OPENAI_API_KEY=sk-...). If the environment variable OPENAI_API_KEY is
    already set, this function will not overwrite it.
    """
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]

    p = Path(path)
    if not p.exists():
        return None

    raw = p.read_text(encoding="utf-8").strip()
    # Support KEY=VALUE lines
    if "=" in raw:
        for line in raw.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                if k.strip().upper() in ("OPENAI_API_KEY", "OPENAI_KEY", "API_KEY"):
                    val = v.strip().strip("'\"")
                    os.environ["OPENAI_API_KEY"] = val
                    return val
    # Otherwise treat whole file as the key
    val = raw.strip().strip("'\"")
    if val:
        os.environ["OPENAI_API_KEY"] = val
        return val
    return None


# Ensure we have a key available via env or local secret file
_load_openai_key_from_file()


messages = [{"role": "user", "content": "John is 35 years old"}]


class User(BaseModel):
    name: str
    age: int


resp = completion(model="gpt-5.4-mini", messages=messages, response_format=User)
user = User.model_validate_json(resp.choices[0].message.content)
print(user)
