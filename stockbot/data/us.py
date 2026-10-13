"""미국 주식 OHLCV 데이터 수집 (yfinance 기반)."""
import pandas as pd
import yfinance as yf


def get_ohlcv(ticker: str, lookback_days: int = 200) -> pd.DataFrame:
    """티커의 최근 OHLCV를 가져온다. 컬럼: Open, High, Low, Close, Volume."""
    df = yf.Ticker(ticker).history(period=f"{lookback_days}d")
    return df.dropna()
