"""설정된 모든 채널로 메시지를 동시에 발송한다."""
import logging

from stockbot.config import NotifyConfig
from stockbot.notify.base import Notifier
from stockbot.notify.kakao import KakaoNotifier
from stockbot.notify.slack import SlackNotifier
from stockbot.notify.telegram import TelegramNotifier

logger = logging.getLogger(__name__)

BUILDERS = {
    "slack": lambda cfg: SlackNotifier(cfg.slack_webhook_url) if cfg.slack_webhook_url else None,
    "telegram": lambda cfg: (
        TelegramNotifier(cfg.telegram_bot_token, cfg.telegram_chat_id)
        if cfg.telegram_bot_token and cfg.telegram_chat_id
        else None
    ),
    "kakao": lambda cfg: (
        KakaoNotifier(cfg.kakao_rest_api_key, cfg.kakao_token_path) if cfg.kakao_rest_api_key else None
    ),
}


def build_notifiers(cfg: NotifyConfig) -> list[Notifier]:
    notifiers = []
    for channel in cfg.enabled_channels:
        builder = BUILDERS.get(channel)
        if builder is None:
            logger.warning("알 수 없는 알림 채널: %s", channel)
            continue
        notifier = builder(cfg)
        if notifier is None:
            logger.warning("%s 채널이 활성화되어 있지만 필요한 설정값이 없습니다", channel)
            continue
        notifiers.append(notifier)
    return notifiers


def dispatch(cfg: NotifyConfig, message: str) -> dict[str, bool]:
    results = {}
    for notifier in build_notifiers(cfg):
        results[notifier.name] = notifier.send(message)
    return results
