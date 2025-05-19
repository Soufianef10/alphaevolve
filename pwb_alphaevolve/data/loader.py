"""
Efficient data-loading helpers using `yfinance`.

Usage
-----
symbols = ["SPY", "EFA", "IEF", "VNQ", "GSG"]
price_df = load_ohlc(symbols, start="1990-01-01")
cerebro    = bt.Cerebro()
add_feeds_to_cerebro(price_df, cerebro)
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd
import yfinance as yf
import backtrader as bt
from tqdm import tqdm

CACHE_DIR = Path.home() / ".alpha_trader_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=32)
def load_ohlc(
    symbols: tuple[str, ...],
    start: str | None = None,
    end: str | None = None,
    dataset: str = "yfinance",
) -> pd.DataFrame:
    """Return OHLC dataframe indexed by date with a 2-level column (field, symbol)."""
    tickers = " ".join(symbols)
    df = yf.download(tickers, start=start, end=end, group_by="column", progress=False)

    # yfinance returns single-index columns for one ticker; unify to MultiIndex
    if not isinstance(df.columns, pd.MultiIndex):
        df.columns = pd.MultiIndex.from_product([df.columns, symbols])

    df = df.rename(columns={"Adj Close": "Close"})
    df.columns = pd.MultiIndex.from_tuples(
        (str(field).lower(), sym) for field, sym in df.columns
    )
    df.index.name = "date"

    pivot_df = df.sort_index()

    # fill weekends / holidays → NaNs; forward-fill to trading days later
    full_range = pd.date_range(pivot_df.index.min(), pivot_df.index.max(), freq="D")
    pivot_df = pivot_df.reindex(full_range)

    # persistent feather cache for faster reloads
    cache_key = (
        f"{dataset}_{'_'.join(symbols)}_ohlc_{pivot_df.index.min().date()}_"
        f"{pivot_df.index.max().date()}.feather"
    )
    cache_file = CACHE_DIR / cache_key
    if not cache_file.exists():
        pivot_df.reset_index().rename(columns={"index": "date"}).to_feather(cache_file)
    return pivot_df


def _trading_days(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    return pd.bdate_range(idx.min(), idx.max())


def add_feeds_to_cerebro(df: pd.DataFrame, cerebro: bt.Cerebro) -> None:
    """Convert DataFrame produced by `load_ohlc` into individual Backtrader feeds."""
    trading_idx = _trading_days(df.index)
    tqdm_bar = tqdm(df.columns.levels[1], desc="Adding feeds")
    for symbol in tqdm_bar:
        tqdm_bar.set_postfix_str(symbol)
        sym_df = (
            df.xs(symbol, axis=1, level=1, drop_level=False).copy().droplevel(1, axis=1)
        )
        sym_df.index.name = "date"
        sym_df = sym_df.ffill().bfill()
        sym_df = sym_df.loc[trading_idx]

        data_feed = bt.feeds.PandasData(dataname=sym_df)
        cerebro.adddata(data_feed, name=symbol)
