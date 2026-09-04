"""SQL execution against a DBAPI2 (PEP 249) connection.

Deliberately written against the DBAPI2 interface (``cursor()``,
``execute()``, ``description``, ``fetchall()``, ``rowcount``, ``commit()``)
rather than anything sqlite3-specific, even though the only connection this
app builds today is an in-process ``sqlite3`` one. Every mainstream Python
SQL driver (``psycopg2``, ``mysql-connector-python``, ``duckdb``, ...)
implements that same interface, so ``run_sql`` and ``seed_sample_database``'s
caller (``Kernel``) are the only places that would need to change to point
this at a real database later -- swap ``Kernel.sql_connection`` for a
different driver's connection object, nothing else.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

import polars as pl


@dataclass
class SqlExecution:
    """The raw outcome of one SQL statement -- deliberately its own type
    rather than ``kernel.CellResult`` (which would make this module import
    ``kernel``, and ``kernel`` already needs to import this module to call
    it -- a plain result type here keeps this module a leaf, same as how
    ``display.py`` returns its own ``DataFrameView`` tuple rather than
    reaching into ``kernel``). ``Kernel.run_sql`` copies these fields onto a
    ``CellResult`` itself.
    """

    stdout: str = ""
    value: Any = None
    result_repr: str | None = None
    error: str | None = None


@dataclass
class _Table:
    name: str
    ddl: str
    rows: list[tuple]


# A small, self-contained sample schema: a handful of SQLite's native
# storage classes (INTEGER, TEXT, REAL), a boolean-as-INTEGER convention, a
# date-as-TEXT (ISO 8601) convention -- both common since SQLite has no
# dedicated BOOLEAN/DATE type -- a couple of NULLs to show nullable columns,
# and a two-level foreign key chain (orders -> customers, order_items ->
# orders/products) to give SQL mode something worth joining.
_TABLES: list[_Table] = [
    _Table(
        "customers",
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            balance REAL NOT NULL
        )
        """,
        [
            (1, "Ava Chen", "ava@example.com", "2023-01-14", 1, 128.50),
            (2, "Marcus Webb", "marcus@example.com", "2023-03-02", 1, 0.0),
            (3, "Priya Nair", "priya@example.com", "2023-05-19", 1, 42.75),
            (4, "Leo Fischer", "leo@example.com", "2024-01-08", 0, 0.0),
            (5, "Ines Duarte", "ines@example.com", "2024-06-23", 1, 310.0),
            (6, "Sam O'Neal", "sam@example.com", "2024-11-30", 1, -12.25),
        ],
    ),
    _Table(
        "products",
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            in_stock INTEGER NOT NULL
        )
        """,
        [
            (1, "Mechanical Keyboard", "Electronics", 89.99, 1),
            (2, "Standing Desk", "Furniture", 349.00, 1),
            (3, "Ceramic Mug", "Kitchen", 14.50, 1),
            (4, "Wireless Mouse", "Electronics", 29.99, 0),
            (5, "Notebook (Dot Grid)", "Stationery", 9.25, 1),
            (6, "Mystery Grab Bag", None, 5.00, 1),
            (7, "Desk Lamp", "Furniture", 42.00, 1),
            (8, "USB-C Hub", "Electronics", 24.99, 0),
        ],
    ),
    _Table(
        "orders",
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            order_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """,
        [
            (1, 1, "2024-02-01", "delivered"),
            (2, 1, "2024-04-11", "delivered"),
            (3, 2, "2024-03-22", "cancelled"),
            (4, 3, "2024-06-05", "delivered"),
            (5, 5, "2024-07-19", "shipped"),
            (6, 5, "2024-08-02", "delivered"),
            (7, 6, "2024-12-01", "pending"),
            (8, 3, "2025-01-15", "delivered"),
            (9, 1, "2025-02-20", "shipped"),
            (10, 4, "2025-03-03", "pending"),
        ],
    ),
    _Table(
        "order_items",
        """
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL
        )
        """,
        [
            (1, 1, 1, 1, 89.99),
            (2, 1, 3, 2, 14.50),
            (3, 2, 5, 3, 9.25),
            (4, 3, 4, 1, 29.99),
            (5, 4, 2, 1, 349.00),
            (6, 5, 7, 1, 42.00),
            (7, 5, 3, 4, 14.50),
            (8, 6, 1, 1, 89.99),
            (9, 7, 6, 2, 5.00),
            (10, 8, 8, 1, 24.99),
            (11, 8, 3, 1, 14.50),
            (12, 9, 2, 1, 349.00),
            (13, 9, 7, 1, 42.00),
            (14, 10, 5, 5, 9.25),
        ],
    ),
]


def seed_sample_database(connection: Any) -> None:
    """Create and populate the sample schema on a fresh DBAPI2 connection."""
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    for table in _TABLES:
        cursor.execute(table.ddl)
        placeholders = ", ".join("?" for _ in table.rows[0])
        cursor.executemany(f"INSERT INTO {table.name} VALUES ({placeholders})", table.rows)
    connection.commit()


def introspect_schema(connection: Any) -> dict[str, list[str]]:
    """Live ``{table: [column, ...]}`` straight off the connection's own
    catalog -- the real source of truth ``sql_completion.py``'s heuristic
    completer draws candidates from, so a completion is never a fabricated
    or stale name, only ever "which real name applies here".

    Needs a per-driver case the same way ``describe_connection``'s
    ``target`` does -- there's no DBAPI2-wide standard for "what tables
    exist". SQLite's is its own ``sqlite_master`` table plus ``PRAGMA
    table_info`` per table; a future driver would read its own catalog
    (Postgres/MySQL: the ANSI-standard ``information_schema`` views) and
    return the same shape.
    """
    if not isinstance(connection, sqlite3.Connection):
        return {}

    cursor = connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        " ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]

    schema: dict[str, list[str]] = {}
    for table in tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        schema[table] = [row[1] for row in cursor.fetchall()]
    return schema


def execute(connection: Any, query: str) -> SqlExecution:
    """Execute ``query`` against a DBAPI2 connection.

    A ``SELECT`` (or anything else that produces a result set) comes back as
    a ``polars.DataFrame`` in ``.value``/``.result_repr`` -- the same fields
    ``Kernel.run`` uses for a Python cell's trailing expression -- so it
    renders through the exact same ``dataframe_view`` -> ``DataTable`` path
    as a Python cell's dataframe output, no SQL-specific display code
    needed. Anything without a result set (``INSERT``/``CREATE``/...) just
    reports the row count as stdout, mirroring a shell command's output.
    """
    cursor = connection.cursor()

    try:
        cursor.execute(query)
    except Exception as exc:
        return SqlExecution(error=str(exc))

    if cursor.description is None:
        connection.commit()
        stdout = f"{cursor.rowcount} row(s) affected" if cursor.rowcount >= 0 else "OK"
        return SqlExecution(stdout=stdout)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    data = {name: [row[i] for row in rows] for i, name in enumerate(columns)}
    df = pl.DataFrame(data)

    return SqlExecution(value=df, result_repr=repr(df))


def describe_connection(connection: Any) -> tuple[str, str]:
    """Best-effort ``(engine, target)`` straight off the live connection
    object -- no separate hand-maintained label to drift out of sync if
    ``Kernel.sql_connection`` ever points somewhere else.

    ``engine`` comes from the connection class's own module -- works for
    any DBAPI2 driver without special-casing (``sqlite3`` -> ``"sqlite3"``,
    ``psycopg2`` -> ``"psycopg2"``, ``duckdb`` -> ``"duckdb"``, ...).

    ``target`` (what database it's actually pointed at) has no DBAPI2-wide
    standard to read, so it needs a per-driver case -- ``sqlite3`` is
    special-cased via ``PRAGMA database_list`` (its ``file`` column is the
    on-disk path, or ``""`` for an in-memory connection) since that's the
    only driver this app uses today; a future driver either gets its own
    case here (e.g. psycopg2's ``get_dsn_parameters()``) or falls back to
    the connection's own ``repr()``.
    """
    engine = type(connection).__module__.split(".")[0]

    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute("PRAGMA database_list")
        _, _, file = cursor.fetchone()
        return engine, (file or ":memory:")

    return engine, repr(connection)
