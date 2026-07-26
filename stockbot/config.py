"""환경변수 및 관심종목 설정 로딩."""
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
WATCHLIST_PATH = BASE_DIR / "watchlist.yaml"


@dataclass
class WatchlistItem:
    code: str
    name: str
    market: str  # "kr" or "us"


def load_watchlist() -> list[WatchlistItem]:
    with open(WATCHLIST_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    items = []
    for market in ("kr", "us"):
        for entry in raw.get(market, []):
            items.append(WatchlistItem(code=entry["code"], name=entry["name"], market=market))
    return items


@dataclass
class NotifyConfig:
    enabled_channels: list[str] = field(default_factory=list)
    slack_webhook_url: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    kakao_rest_api_key: str | None = None
    kakao_token_path: str = str(BASE_DIR.parent / "kakao_token.json")


def load_notify_config() -> NotifyConfig:
    channels_raw = os.environ.get("NOTIFY_CHANNELS", "")
    channels = [c.strip() for c in channels_raw.split(",") if c.strip()]
    return NotifyConfig(
        enabled_channels=channels,
        slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL"),
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID"),
        kakao_rest_api_key=os.environ.get("KAKAO_REST_API_KEY"),
    )
