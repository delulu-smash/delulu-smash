"""Heuristic, schema-aware live completion for SQL cells.

No SQL AST here, deliberately -- see the conversation for the full
tradeoff: unlike Python's parser (jedi's ``parso``, purpose-built to
tolerate incomplete/error input), general SQL grammars aren't built to
parse a statement mid-keystroke, which is the normal case while typing.
Instead: a small keyword-position heuristic decides *what kind* of thing
belongs at the cursor (table name vs. column name vs. keyword); the actual
candidates for "table" and "column" always come from
``sql.introspect_schema()``'s live read of the real database, never a
fabricated or static list -- the heuristic only decides *where to look* in
real schema data, not *what's true* about it.

Same ``(source, line, column, ...)`` shape as ``completion.complete``
(jedi's) on purpose -- a drop-in-shaped alternative completion source for
``CodeEditor``, not a parallel API to learn.
"""

from __future__ import annotations

import re

from .completion import Completion

MAX_COMPLETIONS = 50

# Coarse and not dialect-specific -- enough to be useful for a sample
# database's worth of queries. sql.scm (theme.py's syntax highlighting)
# has the exhaustive, dialect-aware keyword list if this needs to grow.
KEYWORDS = [
    "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT",
    "OFFSET", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "AS",
    "AND", "OR", "NOT", "IN", "IS", "NULL", "LIKE", "BETWEEN", "DISTINCT",
    "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM", "CREATE TABLE",
    "DROP TABLE", "ALTER TABLE", "PRIMARY KEY", "FOREIGN KEY", "REFERENCES",
    "COUNT", "SUM", "AVG", "MIN", "MAX", "CASE", "WHEN", "THEN", "ELSE",
    "END", "UNION", "ASC", "DESC",
]

# The single token that governs the cursor position -- found by scanning
# backward from the cursor for the nearest of these, ignoring everything
# else (identifiers, punctuation, other keywords). "table" is a deliberate
# imprecision: it's correct for ALTER/DROP TABLE (an existing table) but
# wrong for CREATE TABLE (a new one) -- accepted since this tool is mostly
# for querying an existing schema, not authoring one.
_TABLE_CONTEXT_KEYWORDS = {"from", "join", "into", "update", "table"}
_COLUMN_CONTEXT_KEYWORDS = {"select", "where", "on", "and", "or", "by", "set", "having", "values"}
# Of the table-context keywords, only these two get an auto-alias appended
# on accept -- "FROM"/"JOIN" table *references* read naturally with an
# alias ("FROM orders o"), but "UPDATE"/"INSERT INTO"/"ALTER TABLE" name a
# target table in a spot that doesn't take one the same way.
_ALIASABLE_KEYWORDS = {"from", "join"}

# Every other accepted completion gets a trailing space on insert, so
# typing the next token never needs its own leading space keystroke --
# except these: an aggregate is always immediately followed by its own
# "(", never a space (SQL tolerates "COUNT (x)", but nobody writes it that
# way, and the whole point here is fewer keystrokes, not an extra one to
# delete).
_NO_TRAILING_SPACE_KEYWORDS = {"COUNT", "SUM", "AVG", "MIN", "MAX"}

_WORD_RE = re.compile(r"\w+")
_QUALIFIED_PREFIX_RE = re.compile(r"(?:(\w+)\.)?(\w*)$")
# table + optional alias, e.g. "FROM orders o" or "JOIN order_items AS oi".
_TABLE_REF_RE = re.compile(r"\b(?:FROM|JOIN)\s+(\w+)(?:\s+(?:AS\s+)?(\w+))?", re.IGNORECASE)


def is_trigger_char(ch: str) -> bool:
    """Characters after which we proactively (re)show the popup.

    Includes space, unlike ``completion.is_trigger_char`` (jedi's) -- a
    space is meaningful in SQL (it follows a keyword like ``FROM``/``JOIN``/
    ``WHERE``), and showing the full candidate list right there, before
    anything's typed, is the whole point of a schema-aware completer: you
    shouldn't have to already half-remember a table's name to discover it.
    """
    return ch.isalnum() or ch in ("_", ".", " ")


def complete(source: str, line: int, column: int, schema: dict[str, list[str]]) -> list[Completion]:
    """Completions at (1-indexed line, 0-indexed column) in ``source``."""
    offset = _offset(source, line, column)
    before_cursor = source[:offset]

    qualifier, prefix = _qualifier_and_prefix(before_cursor)
    if qualifier is not None:
        table = _resolve_alias(source, qualifier, schema)
        entries = [(c, table) for c in schema.get(table, [])] if table else _column_entries(schema)
        return _column_matches(entries, prefix)

    keyword = _governing_keyword(before_cursor)
    candidates: list[Completion] = []

    if keyword in _TABLE_CONTEXT_KEYWORDS:
        if keyword in _ALIASABLE_KEYWORDS:
            candidates = _table_matches_with_alias(schema.keys(), prefix, source)
        else:
            candidates = _matches(schema.keys(), prefix, "table")
    elif keyword in _COLUMN_CONTEXT_KEYWORDS:
        tables = _tables_in_scope(source, schema)
        entries = _column_entries({t: schema[t] for t in tables}) if tables else _column_entries(schema)
        candidates = _column_matches(entries, prefix)

    if prefix or not candidates:
        # Merge in keyword matches whenever something's actually being
        # typed (not just when context resolution drew a total blank) --
        # a misjudged context shouldn't hide a valid keyword. E.g. typing
        # "F" right after "SELECT * " still has "select" as the nearest
        # governing keyword (this heuristic has no notion of "the column
        # list ended at the *"), which would otherwise offer only columns
        # and never suggest "FROM". Suppressed when prefix is empty *and*
        # we already have real candidates, so a fresh "FROM "/"JOIN "
        # trigger shows a clean table list, not that plus all 40 keywords.
        candidates = candidates + _matches(KEYWORDS, prefix, "keyword", upper=True)
    return candidates[:MAX_COMPLETIONS]


def _offset(source: str, line: int, column: int) -> int:
    lines = source.split("\n")
    return sum(len(l) + 1 for l in lines[: line - 1]) + column


def _qualifier_and_prefix(before_cursor: str) -> tuple[str | None, str]:
    match = _QUALIFIED_PREFIX_RE.search(before_cursor)
    if not match:
        return None, ""
    return match.group(1), match.group(2)


def _governing_keyword(before_cursor: str) -> str | None:
    """The nearest of ``_TABLE_CONTEXT_KEYWORDS``/``_COLUMN_CONTEXT_KEYWORDS``
    before the cursor, scanning backward -- ``None`` if there isn't one yet
    (start of an empty/keyword-only statement). Deliberately just a reverse
    token scan, not a parse: cheap, and tolerant of an incomplete statement
    by construction (there's no grammar to satisfy).
    """
    for word in reversed(_WORD_RE.findall(before_cursor)):
        word = word.lower()
        if word in _TABLE_CONTEXT_KEYWORDS or word in _COLUMN_CONTEXT_KEYWORDS:
            return word
    return None


def _tables_in_scope(source: str, schema: dict[str, list[str]]) -> list[str]:
    """Tables named in *any* FROM/JOIN clause in the whole cell, not just
    before the cursor -- SELECT lists are commonly written before their own
    FROM clause, so "before the cursor" would miss it while it's still
    being typed top-to-bottom.
    """
    return [table for table, _alias in _TABLE_REF_RE.findall(source) if table in schema]


def _resolve_alias(source: str, qualifier: str, schema: dict[str, list[str]]) -> str | None:
    if qualifier in schema:
        return qualifier
    for table, alias in _TABLE_REF_RE.findall(source):
        if alias and alias.lower() == qualifier.lower() and table in schema:
            return table
    return None


def _column_entries(schema: dict[str, list[str]]) -> list[tuple[str, str]]:
    """``(column, table)`` pairs across ``schema`` -- kept un-deduplicated
    and per-table on purpose (unlike a flat column-name set) so a column
    that exists on more than one table in scope shows up once per table,
    each tagged with which one it's from (see ``_column_matches``).
    """
    return [(column, table) for table, columns in schema.items() for column in columns]


def _column_matches(entries: list[tuple[str, str]], prefix: str) -> list[Completion]:
    """Like ``_matches``, but ``type`` is the owning table's name instead
    of a generic ``"column"`` label -- so the popup itself answers "which
    table is this from", the same way it already shows a table/keyword's
    category.
    """
    prefix_lower = prefix.lower()
    results = []
    for column, table in entries:
        if not column.lower().startswith(prefix_lower):
            continue
        results.append(Completion(name=column, insert=column + " ", type=table))
        if len(results) >= MAX_COMPLETIONS:
            break
    return results


def suggest_alias(table: str, source: str) -> str:
    """A short alias for ``table``, avoiding collision with aliases already
    used elsewhere in ``source``.

    Default is the initials of each ``_``-separated word (``customers`` ->
    ``c``, ``order_items`` -> ``oi``) -- a plain first-letter isn't enough
    on its own for a schema with several similarly-named tables, and this
    still reduces to "first letter" for a single-word table name, matching
    the common case. On collision with an alias already in use *for a
    different table*, falls back to appending 2, 3, ... until one's free.
    """
    used = {alias.lower() for _table, alias in _TABLE_REF_RE.findall(source) if alias}

    base = "".join(word[0] for word in table.split("_") if word).lower() or table[:1].lower()
    if base not in used:
        return base
    suffix = 2
    while f"{base}{suffix}" in used:
        suffix += 1
    return f"{base}{suffix}"


def _table_matches_with_alias(tables, prefix: str, source: str) -> list[Completion]:
    prefix_lower = prefix.lower()
    results = []
    for table in tables:
        if not table.lower().startswith(prefix_lower):
            continue
        text = f"{table} {suggest_alias(table, source)}"
        results.append(Completion(name=text, insert=text + " ", type="table"))
        if len(results) >= MAX_COMPLETIONS:
            break
    return results


def _matches(candidates, prefix: str, type_: str, *, upper: bool = False) -> list[Completion]:
    prefix_lower = prefix.lower()
    results = []
    for name in candidates:
        if not name.lower().startswith(prefix_lower):
            continue
        display = name.upper() if upper else name
        insert = display if (upper and display in _NO_TRAILING_SPACE_KEYWORDS) else display + " "
        results.append(Completion(name=display, insert=insert, type=type_))
        if len(results) >= MAX_COMPLETIONS:
            break
    return results
