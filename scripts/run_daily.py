#!/usr/bin/env python3
"""매일 실행: 관심종목 데이터를 받아 시그널을 계산하고, 발생한 시그널이 있으면 알림을 보낸다."""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stockbot.config import load_notify_config, load_watchlist
from stockbot.data import kr as kr_data
from stockbot.data import us as us_data
from stockbot.notify.dispatcher import dispatch
from stockbot.signals.engine import Signal, generate_signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

FETCHERS = {"kr": kr_data.get_ohlcv, "us": us_data.get_ohlcv}


def collect_signals() -> list[Signal]:
    all_signals: list[Signal] = []
    for item in load_watchlist():
        fetch = FETCHERS[item.market]
        try:
            df = fetch(item.code)
        except Exception:
            logger.exception("데이터 조회 실패: %s(%s)", item.name, item.code)
            continue
        signals = generate_signals(df, item.code, item.name, item.market)
        for s in signals:
            logger.info("시그널 발생: %s", s.message)
        all_signals.extend(signals)
    return all_signals


def main() -> None:
    signals = collect_signals()
    if not signals:
        logger.info("오늘 발생한 시그널이 없습니다.")
        return

    message = "\n".join(s.message for s in signals)
    cfg = load_notify_config()
    if not cfg.enabled_channels:
        logger.info("NOTIFY_CHANNELS가 설정되지 않아 알림을 보내지 않습니다. 아래 내용을 로그로만 남깁니다:\n%s", message)
        return

    results = dispatch(cfg, f"[주식 시그널 알림]\n{message}")
    logger.info("알림 발송 결과: %s", results)


if __name__ == "__main__":
    main()
