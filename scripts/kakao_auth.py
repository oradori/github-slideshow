#!/usr/bin/env python3
"""카카오톡 '나에게 보내기' 최초 1회 OAuth 인증 스크립트.

사전 준비:
  1. https://developers.kakao.com 에서 앱을 만들고 REST API 키를 KAKAO_REST_API_KEY 로 설정한다.
  2. 앱 설정 > 카카오 로그인 > Redirect URI 에 임의의 URI(예: https://localhost.com)를 등록한다.
  3. 앱 설정 > 카카오 로그인 > 동의항목에서 '카카오톡 메시지 전송'을 활성화한다.

실행하면 인증 URL을 보여주고, 브라우저에서 로그인 후 리다이렉트된 주소의
'code' 파라미터 값을 입력받아 access/refresh token을 발급받아 저장한다.
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stockbot.config import load_notify_config

TOKEN_URL = "https://kauth.kakao.com/oauth/token"
AUTH_URL = "https://kauth.kakao.com/oauth/authorize"


def main() -> None:
    cfg = load_notify_config()
    if not cfg.kakao_rest_api_key:
        print("KAKAO_REST_API_KEY 환경변수를 먼저 설정하세요.")
        return

    redirect_uri = input("Kakao 앱에 등록한 Redirect URI를 입력하세요 (예: https://localhost.com): ").strip()

    query = urlencode({
        "client_id": cfg.kakao_rest_api_key,
        "redirect_uri": redirect_uri,
        "response_type": "code",
    })
    print("\n아래 URL을 브라우저에서 열어 로그인/동의 후,")
    print("리다이렉트된 주소창의 'code=' 뒤 값을 복사하세요.\n")
    print(f"{AUTH_URL}?{query}\n")

    code = input("전달받은 code 값을 입력하세요: ").strip()

    resp = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "client_id": cfg.kakao_rest_api_key,
        "redirect_uri": redirect_uri,
        "code": code,
    }, timeout=10)
    resp.raise_for_status()
    tokens = resp.json()
    tokens["obtained_at"] = time.time()

    token_path = Path(cfg.kakao_token_path)
    token_path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n토큰을 저장했습니다: {token_path}")
    print("이 파일은 절대 커밋하지 마세요 (.gitignore에 포함되어 있습니다).")


if __name__ == "__main__":
    main()
