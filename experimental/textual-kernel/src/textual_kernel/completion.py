"""Jupyter-style live completion using jedi against the kernel's namespace.

``jedi.Interpreter`` (rather than ``jedi.Script``) is what IPython/Jupyter
use for tab completion -- it combines static analysis of the cell's source
with the *live* runtime namespace, so completions include variables actually
defined by earlier cell runs, not just what's visible from static analysis
of the current cell alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jedi

MAX_COMPLETIONS = 50


@dataclass(frozen=True)
class Completion:
    name: str
    insert: str
    """Full text that replaces the already-typed prefix on accept (see
    ``CodeEditor._accept_completion``) -- not a suffix to append."""
    type: str


def complete(source: str, line: int, column: int, namespace: dict[str, Any]) -> list[Completion]:
    """Completions at (1-indexed line, 0-indexed column) in ``source``."""
    try:
        interpreter = jedi.Interpreter(source, [namespace])
        raw = interpreter.complete(line=line, column=column)
    except Exception:
        return []
    return [Completion(name=c.name, insert=c.name, type=c.type) for c in raw[:MAX_COMPLETIONS]]


def is_trigger_char(ch: str) -> bool:
    """Characters after which we proactively (re)show the popup."""
    return ch.isalnum() or ch in ("_", ".")
