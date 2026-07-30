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
│   ├── krstock/{current_price, current_daily, balance, buyable_quantity, sellable_quantity, order_cash_buy, order_cash_sell, realtime_execution}
│   │        └ realtime_execution = 실시간 체결가 WebSocket 구독 예제
│   └── gbstock/{current_price, balance, buyable_amount, sellable_quantity, order_buy}  # 해외주식
│            └ 해외는 매수/매도 가능수량이 buyableAmount 한 API(pcs_dit)로 통합 — AGENTS.md 참고
examples/     # ② 카테고리 통합 예제 (krstock_functions.py + _examples.py)
pipeline/          # ③ 설계→검증→실행 파이프라인 (골격)
instruments/       # 종목마스터(.mst) 구조체 문서(headers/*.h) + 파서 + 28종 일괄 검증
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
> 종목마스터를 쓴다면 `NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments` 도 함께 설정하세요.

## 환경변수

| 변수 | 설명 |
|---|---|
| `NHPLUG_APP_KEY` / `NHPLUG_APP_SECRET` | 발급받은 앱키/시크릿 (`APP_KEY`/`APP_SECRET` 도 허용) |
| `NHPLUG_BASE_URL` | 호출 대상. 기본 `https://api.nhplug.com:8443`(운영) · 교육·시뮬레이션은 `https://moapi.nhplug.com:8443` |
| `NHPLUG_AUTH_URL` | 토큰 발급 URL. 기본 `https://api.nhplug.com:8443`(운영 전용 — moapi 미제공) |
| `NHPLUG_DEFAULT_ACCOUNT` | 잔고 샘플 등에서 사용할 기본 계좌번호 |
| `NHPLUG_INSTRUMENTS_BASE` | 종목마스터(.mst) 다운로드 기준 URL. 기본 `https://www.nhplug.com/instruments` · **N2 는 `https://www.n2plug.com/instruments`** |

## 계좌구분(`acct_type`) — 환경에 맞는 계좌 고르기

계좌목록(`/n2/acctinfo`)은 **여러 구분의 계좌를 섞어서** 내려줍니다. 계좌구분이 사용 환경을 결정합니다.

| `acct_type` | 용도 | 사용 도메인 |
|---|---|---|
| `01` | 🔴 운영 (일반) | `api.nhplug.com:8443` |
| `02` | 🔴 운영 (주문대리인) | `api.nhplug.com:8443` |
| `03` | 🟢 모의투자 | `moapi.nhplug.com:8443` |

> ⚠️ **운영 도메인에 `03` 계좌를, 모의투자 도메인에 `01`·`02` 계좌를 쓰면 실패합니다.** 목록의 첫 계좌를 그대로 쓰지 마세요.

```python
from snippets.common.list_accounts.list_accounts import usable_accounts, current_env

current_env()        # 'live' | 'mock'  — NHPLUG_BASE_URL 기준
usable_accounts()    # 현재 환경에서 쓸 수 있는 계좌만
```

```bash
python snippets/common/list_accounts/list_accounts.py   # 계좌별 환경·사용가능 여부 표로 출력
```

## 오류 처리 · 토큰 캐시

```python
from nhplug import call, NhplugError

try:
    data = call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})
except NhplugError as e:
    print(e.category, e.code, e.message)   # business / rate_limit / auth / network / http
```

- **HTTP 200 이어도 `rsp_cd` 가 성공 코드가 아니면 예외**입니다. 실패를 성공으로 오판하지 않습니다.
  - 기본 성공 코드: **`00000`·`00166`·`00221`·`13578`** (+ `rsp_msg` 에 "완료" 가 포함되면 성공으로 처리하는 안전망)
  - 성공 코드 교체: `NHPLUG_SUCCESS_CODES=00000,00166,00221,13578,...`
  - 예외 없이 원본 응답이 필요하면: `call(..., raise_on_error=False)`
- **토큰은 24시간 유효하며 `~/.nhplug/token-*.json` 에 캐시**되어 스크립트를 여러 번 실행해도 **재발급하지 않습니다**(재발급 1회 = 보안 알림 1건).
  - 파일 권한은 **OS 기본값**을 따릅니다(별도 `chmod` 없음). 공용 계정·공유 서버에서는 `NHPLUG_TOKEN_CACHE_DIR` 로 접근이 제한된 경로를 지정하거나 `NHPLUG_TOKEN_CACHE=0` 으로 끄세요.
  - 끄기: `NHPLUG_TOKEN_CACHE=0` · 위치 변경: `NHPLUG_TOKEN_CACHE_DIR`
  - 재발급은 **401(토큰 무효)** 일 때만 합니다. `429` 재시도에는 기존 토큰을 그대로 사용합니다.
- **429(호출 유량 초과)** 는 자동 재시도하지 않고 `category="rate_limit"` 예외로 알립니다(실측 한도 초당 5회 수준). 호출 간격을 늘려 주세요.

## ⚠️ 안전

- 기본 호출 대상은 **운영(api)**. 개발·교육·시뮬레이션은 **모의투자(`moapi`)** 로 전환하세요. 접근토큰은 운영 전용이라, moapi 호출에도 토큰은 api 에서 발급됩니다.
- 주문 샘플은 기본 **드라이런**입니다. 실주문은 `dry_run=False`로, 반드시 모의투자(`moapi`)에서 검증 후.
- 앱키/시크릿은 코드에 넣지 말고 `.env`로 관리(`.gitignore` 처리됨).

## 가이드

- [Antigravity 로 바이브코딩하기](guides/antigravity.md) — 명세만으로 AI IDE(Antigravity·Cursor)에서 NH Open API 개발·테스트하는 준비와 절차

## 라이선스 · 문의

MIT · apisupport@nhsec.com
