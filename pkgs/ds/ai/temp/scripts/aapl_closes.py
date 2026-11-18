"""Daily closing prices of a stock ticker over the past year, from Google Finance."""

import re
from datetime import date

from pydantic import BaseModel

from ds.ai.extract import page_data

MIN_ROWS = 15


class DailyClose(BaseModel, frozen=True):
    day: date  # trading day
    close: float  # closing price


def aapl_closes(ticker: str = "AAPL:NASDAQ") -> list[DailyClose]:
    """Daily closes for `ticker` (eg AAPL:NASDAQ) over the past year, oldest first."""
    body = page_data(_url(ticker), clicks=["1Y"], response="rpcids=c2u4wc")
    return _parse(body)


def _url(ticker: str) -> str:
    return f"https://www.google.com/finance/quote/{ticker}"


def _parse(body: str) -> list[DailyClose]:
    pat = re.compile(r"\[\[(\d{4}),(\d{1,2}),(\d{1,2}),[^\[\]]*\[-?\d+\]\],\[(-?[\d.]+(?:E-?\d+)?),")
    seen = {}
    for y, m, d, c in pat.findall(body):
        day = date(int(y), int(m), int(d)).isoformat()
        if day not in seen:
            seen[day] = float(c)
    return [DailyClose(day=date.fromisoformat(k), close=v) for k, v in sorted(seen.items())]


def _check(rows: list[DailyClose]) -> str:
    return "" if len(rows) >= MIN_ROWS else f"only {len(rows)} rows"
