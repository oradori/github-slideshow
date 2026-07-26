"""카카오톡 '나에게 보내기' 알림.

카카오는 Slack/Telegram과 달리 access_token이 짧게 만료되는 OAuth 토큰이 필요하다.
최초 1회는 scripts/kakao_auth.py 를 실행해 authorize code -> access/refresh token
발급을 받아 kakao_token.json 에 저장해야 하며, 이후 만료 시 refresh_token으로
자동 갱신한다. 앱 등록 및 카카오 로그인 활성화는 https://developers.kakao.com 에서
진행하고 KAKAO_REST_API_KEY 환경변수에 REST API 키를 넣는다.
"""
import json
import logging
import time
from pathlib import Path

import requests

from stockbot.notify.base import Notifier

logger = logging.getLogger(__name__)

TOKEN_URL = "https://kauth.kakao.com/oauth/token"
SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


class KakaoNotifier(Notifier):
    name = "kakao"

    def __init__(self, rest_api_key: str, token_path: str):
        self.rest_api_key = rest_api_key
        self.token_path = Path(token_path)

    def _load_tokens(self) -> dict:
        if not self.token_path.exists():
            raise FileNotFoundError(
                f"{self.token_path} 가 없습니다. 먼저 scripts/kakao_auth.py 로 최초 인증을 진행하세요."
            )
        return json.loads(self.token_path.read_text(encoding="utf-8"))

    def _save_tokens(self, tokens: dict) -> None:
        self.token_path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")

    def _refresh_access_token(self, tokens: dict) -> dict:
        resp = requests.post(TOKEN_URL, data={
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": tokens["refresh_token"],
        }, timeout=10)
        resp.raise_for_status()
        refreshed = resp.json()
        tokens["access_token"] = refreshed["access_token"]
        tokens["obtained_at"] = time.time()
        tokens["expires_in"] = refreshed.get("expires_in", 21599)
        if "refresh_token" in refreshed:
            tokens["refresh_token"] = refreshed["refresh_token"]
        self._save_tokens(tokens)
        return tokens

    def _get_valid_access_token(self) -> str:
        tokens = self._load_tokens()
        obtained_at = tokens.get("obtained_at", 0)
        expires_in = tokens.get("expires_in", 0)
        if time.time() >= obtained_at + expires_in - 60:
            tokens = self._refresh_access_token(tokens)
        return tokens["access_token"]

    def send(self, message: str) -> bool:
        try:
            access_token = self._get_valid_access_token()
        except (FileNotFoundError, requests.RequestException, KeyError):
            logger.exception("Kakao 토큰 준비 실패")
            return False

        template_object = {
            "object_type": "text",
            "text": message,
            "link": {"web_url": "https://developers.kakao.com", "mobile_web_url": "https://developers.kakao.com"},
        }
        try:
            resp = requests.post(
                SEND_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                data={"template_object": json.dumps(template_object, ensure_ascii=False)},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except requests.RequestException:
            logger.exception("Kakao 전송 실패")
            return False
