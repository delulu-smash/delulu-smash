from __future__ import annotations

from pathlib import Path

import polars as pl

__all__ = ["init_db"]

DATA_DIR = Path(__file__).parent


# this class allows to load the all parquet files as tables
# named by their file name
# this then allows to query like smash_db.sql("select * from framedata")
class SmashDb:
    def __init__(self):
        self.data_dir = DATA_DIR
        # one table per *.parquet file, named by its filename stem (eg char.parquet -> "char")
        self._tables = {p.stem: pl.scan_parquet(p) for p in sorted(DATA_DIR.glob("*.parquet"))}
        self._ctx = pl.SQLContext(**self._tables)

    def sql(self, sql: str) -> pl.DataFrame:
        return self._ctx.execute(sql, eager=True)


def init_db() -> SmashDb:
    return SmashDb()
