move to sqllite, adding we could enforce contraints like FK constraints (but one problem is any addition we need to update the create table/etc scirpt, parquet just dump)

# Data Storage

## Format: SQLite

Persisted data is stored in SQLite database files (`.sqlite`/`.db`), not per-library formats (eg Parquet
directories, pickles, DuckDB-native `.duckdb` files).

### Why

- **Library-agnostic access**: one file readable from the whole Python data stack with no conversion step:
  - stdlib `sqlite3` (zero dependencies)
  - DuckDB, by attaching the file (`ATTACH 'file.db' (TYPE sqlite)`) and querying it directly
  - Polars (`pl.read_database(query, sqlite3_connection)`) and pandas (`pd.read_sql`)
- **Schema metadata lookup**: tables, columns and types can be discovered from the file itself
  (`sqlite_master`, `PRAGMA table_info(<table>)`), so consumers (scripts, agents, UIs) don't need a separate
  schema description to know what's stored.
- **Built-in SQL**: filtering, joins, aggregation and indexing are available without loading a dataframe
  library, and the same queries work across all the tools above.
- **Single portable file**: easy to copy between machines, inspect with any SQLite viewer, and back up.

## Requirements

- Writers must declare explicit column types when creating tables (no untyped columns), so schema lookup
  returns meaningful types to every reader.
- Stay within SQL that SQLite supports natively; don't depend on DuckDB- or Polars-only features for data that
  is persisted.
- Heavy analytics may load into DuckDB/Polars in memory, but the SQLite file remains the source of truth.