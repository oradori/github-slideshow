"""시그널(1=매수, -1=매도, 0=유지) 기반 단순 벡터화 백테스터.

공매도는 다루지 않는다: 매수 시그널 이후 매도 시그널이 나오기 전까지는
계속 보유(포지션=1), 그 외에는 미보유(포지션=0) 로 취급한다.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Trade:
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    return_pct: float


@dataclass
class BacktestResult:
    total_return: float
    max_drawdown: float
    win_rate: float
    num_trades: int
    trades: list[Trade]
    equity_curve: pd.Series


def _signal_to_position(signal: pd.Series) -> pd.Series:
    position = signal.replace(0, np.nan)
    position = position.ffill().fillna(0)
    return position.clip(lower=0)  # -1(매도)은 미보유(0)로 취급


def _extract_trades(df: pd.DataFrame, position: pd.Series) -> list[Trade]:
    trades = []
    entry_idx = None
    prev = 0
    for idx, pos in position.items():
        if prev == 0 and pos == 1:
            entry_idx = idx
        elif prev == 1 and pos == 0 and entry_idx is not None:
            entry_price = df.loc[entry_idx, "Close"]
            exit_price = df.loc[idx, "Close"]
            trades.append(Trade(
                entry_date=str(entry_idx.date()) if hasattr(entry_idx, "date") else str(entry_idx),
                exit_date=str(idx.date()) if hasattr(idx, "date") else str(idx),
                entry_price=float(entry_price),
                exit_price=float(exit_price),
                return_pct=float(exit_price / entry_price - 1),
            ))
            entry_idx = None
        prev = pos
    return trades


def run_backtest(df: pd.DataFrame, signal: pd.Series) -> BacktestResult:
    position = _signal_to_position(signal)
    daily_returns = df["Close"].pct_change().fillna(0)
    strategy_returns = position.shift(1).fillna(0) * daily_returns
    equity_curve = (1 + strategy_returns).cumprod()

    total_return = float(equity_curve.iloc[-1] - 1) if len(equity_curve) else 0.0
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1
    max_drawdown = float(drawdown.min()) if len(drawdown) else 0.0

    trades = _extract_trades(df, position)
    win_rate = (
        sum(1 for t in trades if t.return_pct > 0) / len(trades) if trades else 0.0
    )

    return BacktestResult(
        total_return=total_return,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        num_trades=len(trades),
        trades=trades,
        equity_curve=equity_curve,
    )
