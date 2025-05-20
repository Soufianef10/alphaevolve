"""Market regime detection utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def regime_signal(
    df: pd.DataFrame,
    *,
    ticker: str,
    benchmark: str = "SPY",
    lookback: int = 63,
    corr_threshold: float = 0.0,
) -> pd.Series:
    """Return +1 (buy) or -1 (sell) regime signal for ``ticker``.

    Parameters
    ----------
    df : DataFrame
        OHLC dataframe produced by :func:`load_ohlc` with multi-index columns
        of the form ``(field, symbol)``.
    ticker : str
        Symbol for which to compute the regime signal.
    benchmark : str, default 'SPY'
        Benchmark symbol used for correlation.
    lookback : int, default 63
        Window length in trading days used for rolling correlation.
    corr_threshold : float, default 0.0
        Minimum correlation with the benchmark required to be considered
        risk-on.  Values below this produce a -1 signal.
    """
    close = df["close"]
    if ticker not in close or benchmark not in close:
        raise KeyError("Symbols not found in DataFrame")

    ret_ticker = close[ticker].pct_change()
    ret_bench = close[benchmark].pct_change()

    rolling_corr = ret_ticker.rolling(lookback).corr(ret_bench)
    bench_trend = ret_bench.rolling(lookback).mean()

    regime = (rolling_corr > corr_threshold) & (bench_trend > 0)
    signal = np.where(regime, 1, -1)
    return pd.Series(signal, index=df.index, name="signal")
