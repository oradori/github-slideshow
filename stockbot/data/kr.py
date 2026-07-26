"""국내 주식 OHLCV 데이터 수집 (FinanceDataReader 기반)."""
from datetime import date, timedelta

import FinanceDataReader as fdr
import pandas as pd


def get_ohlcv(code: str, lookback_days: int = 200) -> pd.DataFrame:
    """종목코드의 최근 OHLCV를 가져온다. 컬럼: Open, High, Low, Close, Volume."""
    start = date.today() - timedelta(days=lookback_days)
    df = fdr.DataReader(code, start)
    return df.dropna()
