#!/usr/bin/env python3
"""단일 종목에 대해 SMA 교차 전략을 백테스트하고 결과를 출력한다.

사용 예:
  python scripts/run_backtest.py --market kr --code 005930 --lookback-days 365
  python scripts/run_backtest.py --market us --code AAPL --lookback-days 365
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stockbot.backtest.engine import run_backtest
from stockbot.data import kr as kr_data
from stockbot.data import us as us_data
from stockbot.signals.engine import compute_cross_signal

FETCHERS = {"kr": kr_data.get_ohlcv, "us": us_data.get_ohlcv}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=["kr", "us"], required=True)
    parser.add_argument("--code", required=True, help="국내 종목코드 또는 미국 티커")
    parser.add_argument("--lookback-days", type=int, default=365)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = FETCHERS[args.market](args.code, lookback_days=args.lookback_days)
    signal = compute_cross_signal(df)
    result = run_backtest(df, signal)

    print(f"종목: {args.code} ({args.market}) / 기간: {df.index[0].date()} ~ {df.index[-1].date()}")
    print(f"누적수익률   : {result.total_return:.2%}")
    print(f"최대낙폭(MDD): {result.max_drawdown:.2%}")
    print(f"거래횟수     : {result.num_trades}")
    print(f"승률         : {result.win_rate:.2%}")
    print()
    print("거래 내역:")
    for t in result.trades:
        print(f"  {t.entry_date} 매수({t.entry_price:.2f}) -> {t.exit_date} 매도({t.exit_price:.2f})"
              f"  수익률 {t.return_pct:.2%}")


if __name__ == "__main__":
    main()
