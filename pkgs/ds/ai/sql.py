from __future__ import annotations

from ds.ai.util import chat
from polars import DataFrame
from pydantic import BaseModel, Field

__all__ = ["sql"]


class DataframeQuery(BaseModel):
    explanation: str = Field(description="A brief explanation of what filtering logic is being applied.")
    sql: str = Field(description="A valid polars df.sql() string. Example: 'SELECT * FROM self WHERE age > 30'")


def sql(df: DataFrame, prompt: str) -> DataFrame:
    """
    Convert a natural language request into a valid polars `df.sql()` string based on the provided DataFrame schema.

    Args:
        df (polars.DataFrame): The DataFrame to query.
        prompt (str): The natural language request for the query.

    Returns
    -------
        DataframeQuery: A Pydantic model containing the SQL query and an explanation of the filtering logic.
    """
    schema_info = str(df.schema)

    system_instruction = (
        "You are an expert data analysis assistant. Your job is to convert a user's natural language "
        "request into a valid polars `df.sql()` string based strictly on the provided schema.\n\n"
        f"Here is the polars DataFrame schema (Columns and Data Types):\n{schema_info}\n\n"
        "Rules:\n"
        "1. Return ONLY a valid query string that can be passed directly into `df.sql()`.\n"
        "2. Do not include 'df.sql()' or backticks in the sql field.\n"
        "3. String values inside the query must be properly enclosed in matching quotes."
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Query requested: {prompt}"},
    ]

    df_query = chat(messages=messages, response_format=DataframeQuery)
    _df = df.sql(df_query.sql)
    _df.ai = df_query
    return _df
