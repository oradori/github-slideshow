import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stockbot.backtest.engine import run_backtest
from stockbot.signals.engine import compute_cross_signal


def _make_df(prices: list[float]) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=len(prices), freq="D")
    return pd.DataFrame({"Close": prices}, index=dates)


def test_compute_cross_signal_detects_golden_and_dead_cross():
    # 하락 후 급반등(골든크로스) 후 다시 하락(데드크로스)하는 인위적 시계열
    prices = [100 - i for i in range(25)] + [75 + i * 3 for i in range(25)] + [150 - i * 3 for i in range(25)]
    df = _make_df(prices)
    signal = compute_cross_signal(df)
    assert (signal == 1).any(), "골든크로스가 감지되어야 한다"
    assert (signal == -1).any(), "데드크로스가 감지되어야 한다"


def test_run_backtest_on_uptrend_is_profitable():
    prices = [100 - i for i in range(25)] + [75 + i * 3 for i in range(50)]
    df = _make_df(prices)
    signal = compute_cross_signal(df)
    result = run_backtest(df, signal)
    assert result.total_return > 0
    assert -1 <= result.max_drawdown <= 0
    assert 0 <= result.win_rate <= 1


def test_run_backtest_flat_market_has_no_trades():
    df = _make_df([100.0] * 30)
    signal = compute_cross_signal(df)
    result = run_backtest(df, signal)
    assert result.num_trades == 0
    assert result.total_return == 0
