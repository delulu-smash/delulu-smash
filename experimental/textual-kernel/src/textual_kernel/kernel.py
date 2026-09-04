"""A persistent, in-process, Jupyter-like execution namespace.

Each ``run()`` call compiles and executes a chunk of code against a
namespace that persists across calls, mirroring how a Jupyter kernel keeps
variables alive between cells. If the last statement is a bare expression,
its repr is captured as "Out[n]" instead of being discarded, matching
IPython/Jupyter's interactive behavior.
"""

from __future__ import annotations

import ast
import contextlib
import io
import sqlite3
import subprocess
import traceback
from dataclasses import dataclass
from typing import Any

from . import sql

SHELL_TIMEOUT_SECONDS = 60


@dataclass
class CellResult:
    execution_count: int
    stdout: str = ""
    stderr: str = ""
    value: Any = None
    result_repr: str | None = None
    error: str | None = None


class Kernel:
    def __init__(self) -> None:
        self.namespace: dict[str, object] = {"__name__": "__console__"}
        self.execution_count = 0
        # In-memory, reseeded on every app start -- disposable, matching
        # this project's own "PoC, not production" stance. Held as a plain
        # DBAPI2 connection (see sql.py) so pointing this at a real database
        # later is a one-line swap, not a rewrite.
        self.sql_connection = sqlite3.connect(":memory:")
        sql.seed_sample_database(self.sql_connection)

    def sql_connection_info(self) -> tuple[str, str]:
        """``(engine, target)`` read straight off ``sql_connection`` itself
        (see ``sql.describe_connection``) -- surfaced by the UI (Cell's
        SQL-mode connection badge) so it's visible what a query is actually
        about to run against. Nothing to keep in sync by hand: swap
        ``sql_connection`` for a different driver later and this reflects
        it automatically.
        """
        return sql.describe_connection(self.sql_connection)

    def sql_schema(self) -> dict[str, list[str]]:
        """``{table: [column, ...]}`` read straight off ``sql_connection``
        (see ``sql.introspect_schema``) -- the candidate pool for SQL-mode
        completion (``sql_completion.py``). Re-queried on every call rather
        than cached: cheap against an in-memory sample database, and always
        reflects any DDL a cell has actually run.
        """
        return sql.introspect_schema(self.sql_connection)

    def run(self, code: str) -> CellResult:
        self.execution_count += 1
        result = CellResult(execution_count=self.execution_count)

        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError:
            result.error = traceback.format_exc()
            return result

        trailing_expr: ast.Expr | None = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            trailing_expr = tree.body.pop()

        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                if tree.body:
                    exec(compile(tree, "<cell>", "exec"), self.namespace)
                if trailing_expr is not None:
                    value = eval(
                        compile(ast.Expression(trailing_expr.value), "<cell>", "eval"),
                        self.namespace,
                    )
                    if value is not None:
                        self.namespace["_"] = value
                        result.value = value
                        result.result_repr = repr(value)
        except Exception:
            result.error = traceback.format_exc()

        result.stdout = stdout.getvalue()
        result.stderr = stderr.getvalue()
        return result

    def run_shell(self, command: str) -> CellResult:
        """Run ``command`` in a subshell (IPython-style ``!`` escape).

        Not a persistent shell -- each call gets a fresh subprocess, so
        ``cd``/env var changes don't carry over between cells.
        """
        self.execution_count += 1
        result = CellResult(execution_count=self.execution_count)

        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=SHELL_TIMEOUT_SECONDS,
            )
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            if proc.returncode != 0:
                result.error = f"[exit code {proc.returncode}]"
        except subprocess.TimeoutExpired:
            result.error = f"[timed out after {SHELL_TIMEOUT_SECONDS}s]"
        except OSError as exc:
            result.error = str(exc)

        return result

    def run_sql(self, query: str) -> CellResult:
        self.execution_count += 1
        result = CellResult(execution_count=self.execution_count)
        outcome = sql.execute(self.sql_connection, query)
        result.stdout = outcome.stdout
        result.value = outcome.value
        result.result_repr = outcome.result_repr
        result.error = outcome.error
        return result
