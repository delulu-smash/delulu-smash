from __future__ import annotations

import ds.ai
import polars as pl

df = pl.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie", "David", "Ben", "John"],
        "age": [25, 30, 35, 40, 28, 32],
        "city": ["New York", "Los Angeles", "Chicago", "Houston", "Chicago", "Chicago"],
    }
)

print(ds.ai.sql(df, "Get all people older than 30 who live in Chicago."))
_df = ds.ai.sql(df, "Get average & standard deviation of age")
print(_df.ai)
print(_df)
