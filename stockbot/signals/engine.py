"""지표를 조합해 매매 시그널을 만드는 룰 엔진.

지금은 두 가지 단순한 룰만 구현한다:
  - SMA5/SMA20 골든크로스(매수) / 데드크로스(매도)
  - RSI14 과매수(>=70) / 과매도(<=30) 알림
필요에 따라 새로운 룰을 이 파일에 추가해 나가면 된다.
"""
from dataclasses import dataclass

import pandas as pd

from stockbot.signals.indicators import rsi, sma

SMA_SHORT_WINDOW = 5
SMA_LONG_WINDOW = 20
RSI_WINDOW = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


@dataclass
class Signal:
    code: str
    name: str
    market: str
    date: str
    type: str  # "BUY", "SELL", "RSI_OVERBOUGHT", "RSI_OVERSOLD"
    message: str


def compute_cross_signal(df: pd.DataFrame) -> pd.Series:
    """SMA5/SMA20 교차를 1(골든크로스)/-1(데드크로스)/0(교차 없음)으로 반환한다."""
    short = sma(df["Close"], SMA_SHORT_WINDOW)
    long = sma(df["Close"], SMA_LONG_WINDOW)
    above = short > long
    crossed_up = above & ~above.shift(1, fill_value=False)
    crossed_down = ~above & above.shift(1, fill_value=False)
    signal = pd.Series(0, index=df.index)
    signal[crossed_up] = 1
    signal[crossed_down] = -1
    return signal


def generate_signals(df: pd.DataFrame, code: str, name: str, market: str) -> list[Signal]:
    """가장 최근 거래일 기준으로 발생한 시그널 목록을 반환한다."""
    if len(df) < SMA_LONG_WINDOW + 1:
        return []

    cross = compute_cross_signal(df)
    rsi_series = rsi(df["Close"], RSI_WINDOW)

    last_date = df.index[-1].strftime("%Y-%m-%d")
    signals: list[Signal] = []

    last_cross = cross.iloc[-1]
    if last_cross == 1:
        signals.append(Signal(code, name, market, last_date, "BUY",
                               f"[{name}] SMA{SMA_SHORT_WINDOW}/{SMA_LONG_WINDOW} 골든크로스 발생"))
    elif last_cross == -1:
        signals.append(Signal(code, name, market, last_date, "SELL",
                               f"[{name}] SMA{SMA_SHORT_WINDOW}/{SMA_LONG_WINDOW} 데드크로스 발생"))

    last_rsi = rsi_series.iloc[-1]
    if pd.notna(last_rsi):
        if last_rsi >= RSI_OVERBOUGHT:
            signals.append(Signal(code, name, market, last_date, "RSI_OVERBOUGHT",
                                   f"[{name}] RSI({RSI_WINDOW}) {last_rsi:.1f} 과매수 구간"))
        elif last_rsi <= RSI_OVERSOLD:
            signals.append(Signal(code, name, market, last_date, "RSI_OVERSOLD",
                                   f"[{name}] RSI({RSI_WINDOW}) {last_rsi:.1f} 과매도 구간"))

    return signals
