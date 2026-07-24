# nhplug-sdk

> 🏛️ **NH투자증권 공식 Open API(NHPLUG) 지원 저장소입니다.** &nbsp;·&nbsp; 포털 [www.nhplug.com](https://www.nhplug.com) &nbsp;·&nbsp; 문의 apisupport@nhsec.com
> 대화형 AI(Claude 등)로 쓰려면 → [`nhplug-mcp`](https://github.com/plug-support/nhplug-mcp) &nbsp;|&nbsp; 코드로 개발·자동매매하려면 → 이 저장소(`nhplug-sdk`)

NH투자증권 **NHPLUG** REST Open API 를 파이썬으로 쉽게 쓰기 위한 **샘플코드 · 전략 파이프라인 · 문서** 모음입니다. Python 개발자와 AI 코딩 도구(Antigravity·Cursor·Claude) 모두를 위한 개발자 키트입니다.

> 대화형으로 API 를 쓰고 싶다면 로컬 MCP [`plug-support/nhplug-mcp`](https://github.com/plug-support/nhplug-mcp) 를, 코드로 개발하려면 이 저장소를 사용하세요.

## 구성

```
nhplug/            # 공용 클라이언트 (인증·토큰캐시·Input_0 봉투 자동 처리)
snippets/      # ① 함수 단위 실행 샘플 (기능당 폴더 = 호출 파일 + chk_ 검증 파일)
│   ├── auth/issue_token
│   ├── common/list_accounts
│   ├── krstock/{current_price, current_daily, balance, buyable_quantity, order_cash_buy, order_cash_sell, realtime_execution}
│   │        └ realtime_execution = 실시간 체결가 WebSocket 구독 예제
│   └── gbstock/{current_price, balance, buyable_amount, order_buy}  # 해외주식
examples/     # ② 카테고리 통합 예제 (krstock_functions.py + _examples.py)
pipeline/          # ③ 설계→검증→실행 파이프라인 (골격)
scripts/           # fetch_docs.py — 도메인에서 최신 명세를 docs/ 로 내려받기
docs/              # 명세 로컬 사본(fetch_docs 로 생성, 커밋 안 함) — 정본은 도메인
AGENTS.md          # AI 에이전트 규칙(인증·봉투·환경·안전·주문형식) — 자동 로드
```

## 빠른 시작

```bash
git clone https://github.com/plug-support/nhplug-sdk
cd nhplug-sdk

# 의존성 설치 (uv 권장)
uv sync           # 또는: pip install requests python-dotenv

# 자격증명 설정
cp .env.example .env   # .env 에 APP_KEY / APP_SECRET / BASE_URL 입력

# (선택) 도메인에서 최신 API 명세를 docs/ 로 내려받기 (AI 컨텍스트·오프라인용)
python scripts/fetch_docs.py
```

### 동작 확인 (함수 단위 샘플)

```bash
# 토큰 발급 → 현재가 → 계좌목록 순으로 확인
python snippets/auth/issue_token/chk_issue_token.py
python snippets/krstock/current_price/chk_current_price.py
python snippets/common/list_accounts/chk_list_accounts.py
```

### 통합 예제

```bash
cd examples/krstock
python krstock_examples.py
```

## 브랜드(도메인) — 나무(Namuh) / N2

API·필드·엔드포인트는 **완전히 동일**하고 **접속 도메인만 다릅니다.** 아래 예시는 나무(`nhplug.com`) 기준입니다.

| 브랜드 | 운영(Live) | 모의투자(Mock) | 문서·포털 |
|---|---|---|---|
| 나무(Namuh) | `api.nhplug.com:8443` | `moapi.nhplug.com:8443` | `www.nhplug.com` |
| N2 | `api.n2plug.com:8443` | `moapi.n2plug.com:8443` | `www.n2plug.com` |

> ⚠️ **N2 고객**은 `.env` 의 `NHPLUG_BASE_URL` 과 `NHPLUG_AUTH_URL` 을 **둘 다** n2plug 로 바꾸세요. **AUTH_URL(토큰)까지 안 바꾸면 토큰이 나무(api.nhplug)로 가서 실패합니다.**

## 환경변수

| 변수 | 설명 |
|---|---|
| `NHPLUG_APP_KEY` / `NHPLUG_APP_SECRET` | 발급받은 앱키/시크릿 (`APP_KEY`/`APP_SECRET` 도 허용) |
| `NHPLUG_BASE_URL` | 호출 대상. 기본 `https://api.nhplug.com:8443`(운영) · 교육·시뮬레이션은 `https://moapi.nhplug.com:8443` |
| `NHPLUG_AUTH_URL` | 토큰 발급 URL. 기본 `https://api.nhplug.com:8443`(운영 전용 — moapi 미제공) |
| `NHPLUG_DEFAULT_ACCOUNT` | 잔고 샘플 등에서 사용할 기본 계좌번호 |

## ⚠️ 안전

- 기본 호출 대상은 **운영(api)**. 개발·교육·시뮬레이션은 **모의투자(`moapi`)** 로 전환하세요. 접근토큰은 운영 전용이라, moapi 호출에도 토큰은 api 에서 발급됩니다.
- 주문 샘플은 기본 **드라이런**입니다. 실주문은 `dry_run=False`로, 반드시 모의투자(`moapi`)에서 검증 후.
- 앱키/시크릿은 코드에 넣지 말고 `.env`로 관리(`.gitignore` 처리됨).

## 가이드

- [Antigravity 로 바이브코딩하기](guides/antigravity.md) — 명세만으로 AI IDE(Antigravity·Cursor)에서 NH Open API 개발·테스트하는 준비와 절차

## 라이선스 · 문의

MIT · apisupport@nhsec.com
