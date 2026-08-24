# nhplug-sdk

[![PyPI](https://img.shields.io/pypi/v/nhplug?color=0073b7&label=pip%20install%20nhplug)](https://pypi.org/project/nhplug/)
[![Python](https://img.shields.io/pypi/pyversions/nhplug)](https://pypi.org/project/nhplug/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-www.nhplug.com-informational)](https://www.nhplug.com/llms.txt)

> 🏛️ **NH투자증권 공식 Open API(NHPLUG) 지원 저장소입니다.** &nbsp;·&nbsp; 포털 [www.nhplug.com](https://www.nhplug.com) &nbsp;·&nbsp; 계정 [@PLUG-OpenAPI](https://github.com/PLUG-OpenAPI) &nbsp;·&nbsp; 문의 apisupport@nhsec.com

NH투자증권 **NHPLUG** REST Open API 를 파이썬으로 쉽게 쓰기 위한 **라이브러리 · 샘플코드 · 종목마스터 파서** 모음입니다. Python 개발자와 AI 코딩 도구(Antigravity·Cursor·Claude) 모두를 위한 개발자 키트입니다.

**어떻게 쓰시겠어요?**

| 하고 싶은 일 | 방법 | 시작 |
|---|---|---|
| 내 프로그램에 넣기 (자동매매) | **PyPI** | `pip install nhplug` |
| 예제 보며 배우기 | **이 저장소** | `git clone` 후 `snippets/` |
| 대화로 시세·잔고 조회 (코딩 불필요) | [nhplug-mcp](https://github.com/PLUG-OpenAPI/nhplug-mcp) | Claude 설정에 `npx` 한 줄 |

### AI·에이전트로 개발한다면

1. **명세 정본** — [llms.txt](https://www.nhplug.com/llms.txt) (N2: [n2plug.com/llms.txt](https://www.n2plug.com/llms.txt)) · 전체 문맥은 [llms-full.txt](https://www.nhplug.com/llms-full.txt)
2. **개발 규칙** — [AGENTS.md](AGENTS.md) (AI IDE 가 자동 로드) · [Antigravity·Cursor 가이드](guides/antigravity.md)
3. ⚠️ **호출 식별자 주의** — 이 SDK 는 **URI 경로**(`/krstock/quote/v1/currentPrice`), MCP 는 **operationId**(`krstockQuoteCurrentPrice`)를 씁니다. **섞어 쓰면 동작하지 않습니다.**

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
instruments/       # 종목마스터(.mst) 파서 + 구조체 오프라인 폴백(headers/*.h 28종) + 일괄 검증
                   #   → 자산군별 28종 목록: instruments/README.md
                   #   ※ 구조체 정본은 포털 www.nhplug.com/instruments/<파일명>.h
templates/         # AI IDE 규칙 파일 (AGENTS.md · CLAUDE.md · Cursor .mdc) — 프로젝트에 복사
guides/            # Antigravity·Cursor 등 AI IDE 개발 가이드
scripts/           # fetch_docs.py — 도메인에서 최신 명세를 docs/ 로 내려받기
docs/              # 명세 로컬 사본(fetch_docs 로 생성, 커밋 안 함) — 정본은 도메인
AGENTS.md          # AI 에이전트 규칙(인증·봉투·환경·안전·주문형식) — 자동 로드
```

> **패키지(`pip install nhplug`)에 포함되는 것**: `nhplug/`(코어·실시간) + `instruments/`(파서·헤더 28종)
> **포함되지 않는 것**: `snippets/` `examples/` `pipeline/` `guides/` — 저장소를 clone 해서 참고하세요.

## 설치

```bash
pip install nhplug                 # 공용 클라이언트 + 실시간(WebSocket) + 종목마스터 파서
pip install "nhplug[instruments]"  # 종목마스터를 pandas DataFrame 으로 받고 싶을 때
pip install "nhplug[tls]"          # Windows 등에서 WebSocket TLS 검증 실패 시
```

```python
from nhplug import call
from nhplug.realtime import subscribe
from nhplug.instruments import load_master

call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})
load_master("m_new_stock")                      # 전 종목 마스터 (자동 다운로드·캐시)
subscribe(["005930"], print, max_messages=5)    # 실시간 체결가
```

> 패키지 이름은 `nhplug`, 저장소 이름은 `nhplug-sdk` 입니다. 샘플코드(`snippets/`·`examples/`)는 패키지에 포함되지 않으니 아래처럼 저장소를 받아 참고하세요.

## 저장소로 시작 (샘플코드 실행)

```bash
git clone https://github.com/PLUG-OpenAPI/nhplug-sdk
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

## 설정 — 파일 하나만 관리하면 됩니다

자격증명과 도메인은 **`.env` 한 곳**에서 읽습니다. 코드마다 따로 지정할 필요가 없습니다.

| 순위 | 위치 | 용도 |
|---|---|---|
| 1 | **실제 환경변수** | CI·컨테이너·`claude_desktop_config.json` 등이 항상 이깁니다 |
| 2 | `NHPLUG_ENV_FILE=경로` | 팀 공용 설정 파일을 직접 지정 |
| 3 | **프로젝트 `.env`** | 현재 폴더에서 위로 올라가며 탐색 — 프로젝트별로 다르게 쓸 때 |
| 4 | **`~/.nhplug/.env`** | **한 번 만들면 모든 프로젝트에 공통 적용** (권장) |

빈 값은 다음 순위에서 보충되므로, 전역에 공통 설정을 두고 프로젝트에서 필요한 줄만 덮어쓸 수 있습니다.

```bash
# 전역 설정 (한 번만)
mkdir -p ~/.nhplug && cp .env.example ~/.nhplug/.env   # Windows: %USERPROFILE%\.nhplug\.env
```

```python
from nhplug import loaded_files, get_base_url, get_auth_url
loaded_files()     # 어떤 설정 파일을 읽었는지 확인 (문제 생기면 여기부터)
```

## 브랜드(도메인) — 나무(Namuh) / N2

API·필드·엔드포인트는 **완전히 동일**하고 **접속 도메인만 다릅니다.** 아래 예시는 나무(`nhplug.com`) 기준입니다.

| 브랜드 | 운영(Live) | 모의투자(Mock) | 문서·포털 |
|---|---|---|---|
| 나무(Namuh) | `api.nhplug.com:8443` | `moapi.nhplug.com:8443` | `www.nhplug.com` |
| N2 | `api.n2plug.com:8443` | `moapi.n2plug.com:8443` | `www.n2plug.com` |

> ⚠️ **N2 고객은 `.env` 에서 세 줄을 모두 n2plug 로** 바꾸세요. 하나라도 빠지면 그 기능만 조용히 나무 도메인으로 갑니다.
>
> ```env
> NHPLUG_BASE_URL=https://api.n2plug.com:8443          # 호출 (모의투자는 moapi.n2plug.com:8443)
> NHPLUG_AUTH_URL=https://api.n2plug.com:8443          # 토큰 — 안 바꾸면 인증 실패
> NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments   # 종목마스터
> ```
>
> 실시간(WebSocket) 주소는 `NHPLUG_BASE_URL` 에서 **자동으로 유도**되므로 따로 설정하지 않아도 됩니다.

## 환경변수

| 변수 | 설명 |
|---|---|
| `NHPLUG_APP_KEY` / `NHPLUG_APP_SECRET` | 발급받은 앱키/시크릿 (`APP_KEY`/`APP_SECRET` 도 허용) |
| `NHPLUG_BASE_URL` | 호출 대상. 기본 `https://api.nhplug.com:8443`(운영) · 교육·시뮬레이션은 `https://moapi.nhplug.com:8443` |
| `NHPLUG_AUTH_URL` | 토큰 발급 URL. 기본 `https://api.nhplug.com:8443`(운영 전용 — moapi 미제공) |
| `NHPLUG_DEFAULT_ACCOUNT` | 잔고 샘플 등에서 사용할 기본 계좌번호 |
| `NHPLUG_INSTRUMENTS_BASE` | 종목마스터(.mst) 다운로드 기준 URL. 기본 `https://www.nhplug.com/instruments` · **N2 는 `https://www.n2plug.com/instruments`** |
| `NHPLUG_INSTRUMENTS_CACHE_DIR` | 종목마스터 캐시 위치. 기본 `~/.nhplug/instruments/` (`.mst` · `.h` 공용) |
| `NHPLUG_HEADERS_REMOTE` | `0` 이면 구조체(`.h`)를 포털에서 받지 않고 패키지 폴백만 사용. 사내망·오프라인용 |
| `NHPLUG_WS_URL` | 실시간 WebSocket 주소를 직접 지정. 없으면 `NHPLUG_BASE_URL` 호스트·`tr_cd` 에서 자동 유도 |
| `NHPLUG_WS_MAX_KEYS` | 세션당 실시간 등록 수. 기본·상한 `10` (**낮추는 것만** 가능) |
| `NHPLUG_WS_MAX_SESSIONS` | 동시 WebSocket 세션. 기본·상한 `2` (**낮추는 것만** 가능) |
| `NHPLUG_WS_SUBSCRIBE_RATE` | 구독 전송 속도(초당). 기본·상한 `10` (**낮추는 것만** 가능) |
| `NHPLUG_ALLOW_HOSTS` | 사내 검증 서버 등 **허용 호스트 추가**(쉼표 구분). 보통 설정하지 않습니다 |
| `NHPLUG_RATE_LIMIT` | REST 자동 스로틀(초당 호출 수). 기본 `4` · 상한 `5` · `0` 이면 끔 |

### 🔒 주소 오타는 호출 전에 막힙니다

`NHPLUG_BASE_URL`·`NHPLUG_AUTH_URL` 은 **허용된 호스트만** 통과합니다.

```
api.nhplug.com  ·  moapi.nhplug.com  ·  api.n2plug.com  ·  moapi.n2plug.com
```

한 글자만 틀려도 앱키·시크릿이 그대로 전송되기 때문에, 호출하기 전에 막고 무엇이 잘못됐는지 알려줍니다.

```
NHPLUG_BASE_URL 의 호스트 'moapi.nhplg.com' 는 허용되지 않습니다.
  혹시 'moapi.nhplug.com' 인가요?
  허용: api.nhplug.com, moapi.nhplug.com, api.n2plug.com, moapi.n2plug.com
```

`http://`(평문)와 경로가 붙은 주소(`…:8443/krstock`)도 같이 막습니다. 사내 검증 서버가 있다면 `NHPLUG_ALLOW_HOSTS=stg.example.com` 으로 추가하세요.

## 계좌구분(`acct_type`) — 환경에 맞는 계좌 고르기

계좌목록(`/n2/acctinfo`)은 **여러 구분의 계좌를 섞어서** 내려줍니다. 계좌구분이 사용 환경을 결정합니다.

| `acct_type` | 용도 | 사용 도메인 |
|---|---|---|
| `01` | 🔴 운영 (일반) | `api.nhplug.com:8443` |
| `02` | 🔴 운영 (주문대리인) | `api.nhplug.com:8443` |
| `03` | 🟢 모의투자 | `moapi.nhplug.com:8443` |

> ⚠️ **운영 도메인에 `03` 계좌를, 모의투자 도메인에 `01`·`02` 계좌를 쓰면 실패합니다.** 목록의 첫 계좌를 그대로 쓰지 마세요.

**설치해서 쓰는 경우** — 계좌목록을 받아 `acct_type` 으로 직접 거르면 됩니다.

```python
from nhplug import call, get_base_url

LIVE = {"01", "02"}          # 운영 전용 · 03 = 모의투자 전용
env_is_live = not get_base_url().split("//")[-1].startswith("moapi")

accounts = call("/n2/acctinfo", {}).get("Output_0", [])
usable = [a for a in accounts
          if (a.get("acct_type") in LIVE) == env_is_live]
```

**저장소를 clone 한 경우** — 같은 판정을 해주는 샘플이 있습니다(`usable_accounts()` · `current_env()`).

```bash
python snippets/common/list_accounts/list_accounts.py   # 계좌별 환경·사용가능 여부 표로 출력
```

> `snippets/` 는 패키지(`pip install nhplug`)에 포함되지 않습니다. 저장소를 받아야 실행됩니다.

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
- **429(호출 유량 초과)** 는 자동 재시도하지 않고 `category="rate_limit"` 예외로 알립니다. 다만 아래 **자동 스로틀**이 걸려 있어 정상 사용에서는 잘 나지 않습니다.

## 호출 유량 — 자동으로 조절됩니다

실측 한도가 **초당 5회** 수준이라, `call()` 이 **초당 4회**로 자동 스로틀합니다. 직접 `sleep` 을 넣지 않아도 됩니다.

```python
for code in codes:                 # 200종목을 그냥 돌려도 429 가 나지 않습니다
    call("/krstock/quote/v1/currentPrice", {"iem_cd": code, "market_cd": "UNT"})
```

| 설정 | 값 |
|---|---|
| 기본 | 초당 **4회** |
| 상한 | 초당 **5회** (실측 한도. 넘겨 설정하면 5로 깎고 경고) |
| 변경 | `NHPLUG_RATE_LIMIT=2` |
| 끄기 | `NHPLUG_RATE_LIMIT=0` — **권장하지 않습니다**(429 발생) |

슬라이딩 1초 창 방식이라 균등 대기가 아니라 **실제로 넘칠 때만** 기다립니다. 스레드 안전합니다.

## 연속조회(`cts`) — 목록이 여러 페이지로 옵니다

연속조회 키가 오는 위치는 **API 마다 다릅니다.**

| 위치 | 필드 | 비고 |
|---|---|---|
| 응답 **헤더** | `cts` · `cts_flag` | 본문만 보면 놓칩니다 |
| 응답 **본문** `Output_*` | `ctsz16` · `ctsz18` · `ctsz20` · `ctsz30` | 자산군마다 자릿수가 다릅니다 |

SDK 는 **헤더를 먼저 보고, 없으면 본문에서 찾습니다.** 어느 쪽으로 오든 동작합니다.

**전체를 순회할 때 — `paginate()`**

```python
from nhplug import paginate

for page in paginate("/krstock/…", {"act_no": "12345678901"}):
    for row in page.get("Output_0", []):
        print(row)
```

종료 판정·다음 키 전달·무한루프 방지가 모두 들어 있습니다. 호출 간격도 위 스로틀이 처리합니다.

**한 페이지씩 직접 다룰 때 — `want_meta=True`**

```python
from nhplug import call

data, meta = call("/krstock/…", {"act_no": "…"}, want_meta=True)
meta.cts         # 다음 페이지 키 (헤더 → 본문 순으로 탐색)
meta.cts_flag    # "Y" 다음 있음 / "N" 마지막
meta.cts_source  # 키를 어디서 찾았나 — "header" / "body"
meta.has_next    # 위를 종합한 판정
meta.headers     # 응답 헤더 전체

if meta.has_next:
    nxt, meta = call("/krstock/…", {"act_no": "…"},
                     cts=meta.cts, cts_flag=meta.cts_flag, want_meta=True)
```

> `want_meta` 를 주지 않으면 **기존과 똑같이 본문 dict** 만 돌려줍니다. 기존 코드는 그대로 동작합니다.

### 종료 판정 규칙 (실측)

| 조건 | 판정 |
|---|---|
| `cts` 가 비어 있음 | 종료 |
| `cts_flag == "N"` | 종료 |
| `cts_flag == "Y"` | 계속 |
| `cts_flag` 없음 + 키를 **본문**에서 찾음 | 계속 |
| `cts_flag` 없음 + 키가 **헤더** + `rsp_cd` 가 `00165`·`00218` | 계속 |
| 🔴 **`cts` 가 직전과 동일** | **즉시 종료** |

마지막 항목이 중요합니다. 같은 키를 다시 보내면 서버가 **같은 페이지를 계속** 주므로 무한루프가 됩니다. 정상 연속조회는 키가 매번 바뀌지만 **끝 2~3자만 다른 경우**가 있어 전체 문자열로 비교합니다.

```python
for page in paginate("/krstock/…", {...}, max_pages=20):   # 상한도 걸 수 있습니다
    ...
```

## 실시간 (WebSocket)

```python
from nhplug.realtime import subscribe

subscribe(["005930", "000660"], print, max_messages=10)   # 국내 체결가 통합(mc)
subscribe(["005930"], print, tr_cd="mb")                  # 국내 호가 통합
subscribe([], print, tr_cd="d2")                          # 체결통보 (tr_key 불필요)
```

접속 주소는 `NHPLUG_BASE_URL` 과 `tr_cd` 에서 자동으로 만들어집니다.

```
wss://api.nhplug.com:7070/websocket
```

> ⚠️ **경로 `/websocket` 이 필수**입니다. 직접 접속 코드를 짜신다면 빠뜨리지 마세요.

### 채널코드는 시장별로 다릅니다

REST 는 `market_cd` 파라미터로 시장을 고르지만, **실시간은 채널코드 자체가 갈립니다.**

| REST `market_cd` | 체결가 | 호가 | 예상체결 | 회원사 | 프로그램매매 |
|---|---|---|---|---|---|
| `KRX` | `oc` | `ob` | `oa` | `t1` | `t8` |
| `NXT` | `nc` | `nb` | `na` | `ng` | `nn` |
| **`UNT` 통합** | **`mc`** ← 기본 | `mb` | `ma` | `mg` | `mn` |

`oc` 를 쓰면 **NXT 체결이 오지 않습니다.** 오류 없이 데이터만 덜 옵니다.

### 포트 — 통보 채널은 해외라도 7070

| 대상 | 포트 |
|---|---|
| 국내 시세 | `7070` |
| **해외 시세** (`RC`·`RH`·`rc`·`rh`) | `7080` |
| **통보** (`d0`·`d1`·`d2`·`d3`·`de`·`dj`·`dk`·`dv`·`dn`) | **`7070`** — 국내·해외 공통 |
| 모의투자 | `17070` — 국내·해외 공통 |

> 해외파생 통보(`dk`·`dj`)를 7080 으로 보내면 **`WSS10006`** 이 납니다. SDK 가 `tr_cd` 로 자동 판별합니다.

### `tr_key` 는 채널마다 넣는 값이 다릅니다

| 채널 | `tr_key` | 넣는 값 |
|---|---|---|
| 국내 시세 (`mc`·`ob`…) | `code` | 종목코드 `005930` |
| 시간외 (`e2`·`e4`·`e5`) | `ecn_code` | 시간외 코드 |
| **통보** (`d0`~`d3`…) | `userid` | 사용자ID 또는 **빈 값** |
| **해외 시세** (`RC`·`RH`) | `gicz15` | **GIC 15자리 — 티커 아님** |
| 채권지수 (`uB`) | `jisuid` | 지수ID |

### 서버 한도 — SDK 가 자동으로 지킵니다

| 항목 | 한도 | 초과 시 |
|---|---|---|
| 앱키당 동시 세션 | **2** | `WSS10015` |
| 세션당 실시간 등록 | **10** | close code 1000 `"Bye"` — **오류 메시지 없이 끊김** |
| 구독 전송 | **초당 10건** | `WSS10010` |

`subscribe()` 가 알아서 처리합니다.

- 종목이 10개를 넘으면 **10개씩 나눠 여러 세션**으로 구독
- 동시 세션은 **2개**를 넘지 않음(초과분은 앞 세션이 끝나면 이어서)
- 구독 전송 간격 제어
- 종료 시 `tr_type=2` 로 **등록 반납**

> 위 한도는 서버가 강제하는 값이라 **환경변수로 올릴 수 없습니다.** 낮추는 것만 가능합니다.

### 🔒 Windows 에서 TLS 오류가 난다면

실거래 WebSocket(`:7070`·`:7080`)은 서버가 **중간 CA 를 보내지 않습니다.** `curl` 이나 브라우저는 OS 인증서 저장소로 자동 보완해 성공하지만, 파이썬 기본 OpenSSL 검증은 실패합니다.

```bash
pip install "nhplug[tls]"      # truststore — OS 인증서 저장소 사용
```

설치만 하면 **자동으로 적용**됩니다. 코드 수정은 필요 없습니다.

> ⚠️ 검증을 끄는 방법(`CERT_NONE`)은 제공하지 않습니다. 중간자 공격에 그대로 노출됩니다.

> **구독 등록 응답(ACK)은 시세로 세지 않습니다.** 서버는 구독 직후
> `{"header":{"tr_type":"1","rsp_cd":"00000",…}}` 을 한 번 보내는데, SDK 가 이를 걸러내므로
> `max_messages=1` 이어도 **실제 시세 1건**을 받습니다. 등록이 실패하면(`WSS10015` 등) stderr 로 알립니다.
> 응답까지 보려면 `include_ack=True`.

> **통보 채널은 실제 주문이 발생할 때만** 내려옵니다. 조용하다고 연결이 잘못된 것은 아닙니다.
> 시세 채널도 **장 마감 시간에는 0건**이 정상입니다.

**전체 채널 목록(국내 21 · 해외 6)과 `tr_key` 대응표** → [`docs/realtime_channels.md`](docs/realtime_channels.md)

```bash
python snippets/krstock/realtime_execution/chk_realtime_execution.py       # 체결가 통합(mc)
python snippets/krstock/realtime_execution/chk_realtime_execution.py mb    # 호가
python snippets/krstock/realtime_execution/chk_realtime_execution.py d2    # 체결통보
```

접속 주소와 보낸 구독 메시지를 함께 출력하므로, **수신 0건일 때 무엇을 확인해야 하는지** 알 수 있습니다.

## ⚠️ 안전

- 기본 호출 대상은 **운영(api)**. 개발·교육·시뮬레이션은 **모의투자(`moapi`)** 로 전환하세요. 접근토큰은 운영 전용이라, moapi 호출에도 토큰은 api 에서 발급됩니다.
- 주문 샘플은 기본 **드라이런**입니다. 실주문은 `dry_run=False`로, 반드시 모의투자(`moapi`)에서 검증 후.
- 앱키/시크릿은 코드에 넣지 말고 `.env`로 관리(`.gitignore` 처리됨).

## AI IDE 로 개발하기

**[`templates/`](templates/) — 프로젝트에 넣는 규칙 파일.** 규칙이 없으면 AI 가 필드명·성공코드를 추측해 틀린 코드를 만듭니다.

| 도구 | 파일 | 위치 |
|---|---|---|
| Antigravity · Codex | [`AGENTS.md`](templates/AGENTS.md) | 프로젝트 루트 |
| Claude Code | [`CLAUDE.md`](templates/CLAUDE.md) | 프로젝트 루트 |
| **Cursor** | [`nhplug.mdc`](templates/cursor/nhplug.mdc) | **`.cursor/rules/`** |

```powershell
iwr -useb https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/AGENTS.md -OutFile AGENTS.md
```

> ⚠️ Cursor 의 레거시 `.cursorrules` 는 **Agent 모드에서 무시됩니다.** `.cursor/rules/` 경로를 쓰세요.

- [Antigravity 로 바이브코딩하기](guides/antigravity.md) — 설치부터 첫 실행까지 절차

## 라이선스 · 문의

MIT · apisupport@nhsec.com
