import pandas as pd

from pwb_alphaevolve.utils.regime import regime_signal


def test_regime_signal_basic():
    idx = pd.date_range("2020-01-01", periods=10)
    data = {
        ("close", "AAA"): [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
        ("close", "SPY"): [1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45],
    }
    df = pd.DataFrame(data, index=idx)
    sig = regime_signal(df, ticker="AAA", benchmark="SPY", lookback=3)
    assert sig.iloc[-1] == 1


def test_regime_signal_negative():
    idx = pd.date_range("2020-01-01", periods=10)
    data = {
        ("close", "AAA"): [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
        ("close", "SPY"): [1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45],
    }
    df = pd.DataFrame(data, index=idx)
    sig = regime_signal(df, ticker="AAA", benchmark="SPY", lookback=3)
    assert sig.iloc[-1] == -1
