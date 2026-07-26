# stockbot

한국/미국 주식 관심종목을 매일 점검해 매매 시그널을 계산하고, Slack/Telegram/KakaoTalk 중
설정된 채널로 알림을 보내는 자동화 도구. 백테스트로 전략을 검증하는 스크립트도 포함한다.

**주의**: 이 프로젝트는 실제 주문을 실행하지 않는다. 시그널 계산과 알림, 리서치용
백테스트까지만 다룬다. 실거래 자동매매(키움 OpenAPI+ 등)는 별도 단계로 확장 가능하다.

## 구성

```
stockbot/
  config.py          환경변수 및 watchlist.yaml 로딩
  watchlist.yaml      관심종목 목록 (국내/미국)
  data/                시세 수집 (FinanceDataReader, yfinance)
  signals/             지표 계산 및 매매 시그널 룰 엔진
  notify/              Slack / Telegram / Kakao 알림 채널
  backtest/            시그널 기반 벡터화 백테스트 엔진
scripts/
  run_daily.py         매일 실행할 시그널 계산 + 알림 파이프라인
  run_backtest.py      단일 종목 백테스트 실행
  kakao_auth.py        Kakao 최초 1회 OAuth 인증
.github/workflows/
  daily-signals.yml    평일 스케줄 실행 (GitHub Actions)
```

## 로컬 설치

```bash
pip install -r requirements.txt
cp .env.example .env   # 값 채우기
```

## 알림 채널 설정

`.env`의 `NOTIFY_CHANNELS`에 콤마로 원하는 채널을 나열한다 (예: `slack,telegram,kakao`).
현재는 셋 다 동시에 켜서 비교해보고, 추후 하나로 좁히면 된다.

- **Slack**: Incoming Webhook URL 발급 후 `SLACK_WEBHOOK_URL`에 설정.
- **Telegram**: `@BotFather`로 봇 생성 → `TELEGRAM_BOT_TOKEN`, 봇과 대화 시작 후
  `getUpdates`로 `chat.id` 확인 → `TELEGRAM_CHAT_ID`.
- **Kakao**: [Kakao Developers](https://developers.kakao.com)에서 앱 생성, REST API 키를
  `KAKAO_REST_API_KEY`에 설정. 이후 최초 1회 `python scripts/kakao_auth.py` 실행해
  `kakao_token.json`을 생성해야 한다 (access_token 만료 시 자동 갱신됨).
  GitHub Actions에서 사용하려면 이 파일 내용을 `KAKAO_TOKEN_JSON` 시크릿으로 등록한다.
  단, Actions 실행 환경은 매번 초기화되므로 갱신된 토큰이 다시 저장소에 반영되지는
  않는다 — 리프레시 토큰 만료(약 2개월) 전에 재인증이 필요할 수 있다는 점을 알아두자.

## 실행

```bash
# 시그널 계산 + 알림 (watchlist.yaml 기준 전종목)
python scripts/run_daily.py

# 특정 종목 백테스트
python scripts/run_backtest.py --market kr --code 005930 --lookback-days 365
python scripts/run_backtest.py --market us --code AAPL --lookback-days 365
```

## 현재 시그널 룰

`stockbot/signals/engine.py` 참고.

- SMA5/SMA20 골든크로스 → BUY, 데드크로스 → SELL
- RSI(14) 70 이상 → 과매수 알림, 30 이하 → 과매도 알림

새로운 룰은 이 파일에 함수를 추가하고 `generate_signals`에서 호출하면 된다.

## GitHub Actions 자동 실행

`.github/workflows/daily-signals.yml`이 평일 UTC 22:00(KST 07:00, 다음날)에 실행된다.
저장소 Settings → Secrets and variables → Actions 에서 위에서 언급한 환경변수들을
동일한 이름의 Repository secret으로 등록하면 된다.

## 다음 단계 (2단계 아이디어)

- 실거래 자동매매: 키움증권 OpenAPI+(Windows/OCX 필요) 또는 국내외 REST 기반 브로커 연동
- 포지션 사이징, 손절/익절 등 리스크 관리 로직 추가
- `backtrader`/`vectorbt` 등으로 백테스트 고도화, 다중 전략 비교
