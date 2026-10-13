import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stockbot.signals.indicators import macd, rsi, sma


def test_sma_basic():
    close = pd.Series([1, 2, 3, 4, 5])
    result = sma(close, window=2)
    assert result.iloc[1] == 1.5
    assert result.iloc[-1] == 4.5


def test_rsi_all_gains_is_100():
    close = pd.Series(range(1, 30))  # 계속 상승만 하는 시계열
    result = rsi(close, window=14)
    assert result.iloc[-1] == 100


def test_rsi_all_losses_is_0():
    close = pd.Series(range(30, 1, -1))  # 계속 하락만 하는 시계열
    result = rsi(close, window=14)
    assert result.iloc[-1] == 0


def test_macd_columns():
    close = pd.Series(range(1, 60)).astype(float)
    result = macd(close)
    assert list(result.columns) == ["macd", "signal", "hist"]
    assert len(result) == len(close)
