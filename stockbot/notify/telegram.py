"""Telegram Bot API 알림.

설정 방법:
  1. @BotFather 에게 /newbot 으로 봇을 생성하고 토큰을 발급받는다 (TELEGRAM_BOT_TOKEN).
  2. 봇과 대화를 시작한 뒤 https://api.telegram.org/bot<TOKEN>/getUpdates 로
     채팅에서 chat.id 값을 확인한다 (TELEGRAM_CHAT_ID).
"""
import logging

import requests

from stockbot.notify.base import Notifier

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org"


class TelegramNotifier(Notifier):
    name = "telegram"

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, message: str) -> bool:
        url = f"{API_BASE}/bot{self.bot_token}/sendMessage"
        try:
            resp = requests.post(url, json={"chat_id": self.chat_id, "text": message}, timeout=10)
            resp.raise_for_status()
            return True
        except requests.RequestException:
            logger.exception("Telegram 전송 실패")
            return False
