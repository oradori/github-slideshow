"""Slack Incoming Webhook 알림.

설정 방법: https://api.slack.com/messaging/webhooks 에서 워크스페이스에
Incoming Webhook 앱을 추가하고 발급받은 URL을 SLACK_WEBHOOK_URL 환경변수에 넣는다.
"""
import logging

import requests

from stockbot.notify.base import Notifier

logger = logging.getLogger(__name__)


class SlackNotifier(Notifier):
    name = "slack"

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, message: str) -> bool:
        try:
            resp = requests.post(self.webhook_url, json={"text": message}, timeout=10)
            resp.raise_for_status()
            return True
        except requests.RequestException:
            logger.exception("Slack 전송 실패")
            return False
