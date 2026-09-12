# 프로젝트 규칙 — NH투자증권 Open API 개발

<!--
  이 파일을 당신의 프로젝트 루트에 `CLAUDE.md` 로 두면
  Claude Code 가 세션 시작 시 자동으로 읽습니다.
  (Antigravity·Codex 는 `AGENTS.md`, Cursor 는 `.cursor/rules/nhplug.mdc` 를 씁니다.
   같은 내용이므로 여러 도구를 쓰면 파일을 모두 두면 됩니다.)
  정본: https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/templates/README.md
-->

## 시작 — SDK 를 쓴다 (직접 HTTP 를 짜지 않는다)

```bash
pip install nhplug                 # 인증·토큰캐시·에러판정·실시간·종목마스터 포함
pip install "nhplug[instruments]"  # 종목마스터를 pandas DataFrame 으로 받을 때
```

```python
from nhplug import call, NhplugError

data = call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})
```

- 토큰 발급·갱신·캐시, `Input_0` 봉투, 인증 헤더, 연속조회, 유량 제어를 **`call()` 이 전부 처리**한다.
  (업무 성공/실패는 판정하지 않는다 — 아래 「에러 처리」 참조)
- `requests` 로 직접 `/oauth2/token` 을 호출하는 코드를 새로 만들지 말 것. 이미 있는 걸 재사용한다.

## 문서 (Source of Truth) — 도메인이 정본

- 전체 개요·인증·공통 규약: https://www.nhplug.com/llms.txt (N2: https://www.n2plug.com/llms.txt)
- 자산군 정본: `https://www.nhplug.com/openapi-docs/<자산>/openapi.json`
  (자산: `common` · `krstock` · `gbstock` · `krfuture` · `gbfuture` · `krbond` · `krgold`)
- **엔드포인트 경로·필드명·필수여부는 `openapi.json` 을 정본으로 따른다. 추측하지 않는다.**
- 전체 문맥이 한 번에 필요하면 https://www.nhplug.com/llms-full.txt (약 160KB)

## 설정 — `.env` 한 곳에서 읽는다

```env
NHPLUG_APP_KEY=발급받은_APP_KEY
NHPLUG_APP_SECRET=발급받은_APP_SECRET
NHPLUG_BASE_URL=https://api.nhplug.com:8443     # 호출 (모의투자: moapi.nhplug.com:8443)
NHPLUG_AUTH_URL=https://api.nhplug.com:8443     # 토큰 — 운영 전용(moapi 미제공)
NHPLUG_INSTRUMENTS_BASE=https://www.nhplug.com/instruments   # 종목마스터
```

- 앱키/시크릿을 **코드에 하드코딩 금지**. `.env` 는 `.gitignore` 에 넣는다.
- 우선순위: 실제 환경변수 > `NHPLUG_ENV_FILE` > 프로젝트 `.env` > 전역 `~/.nhplug/.env`
- 어떤 파일을 읽었는지: `from nhplug import loaded_files; loaded_files()`

### ⚠️ 브랜드(도메인) — 나무 / N2

API·필드는 완전히 같고 **도메인만 다르다.** N2 고객은 **위 세 줄을 모두** `n2plug.com` 으로 바꾼다.
하나라도 빠지면 **그 기능만 조용히 나무 도메인으로 간다.** 실시간(WebSocket) 주소는 `NHPLUG_BASE_URL` 에서 자동 유도된다.

## 호출 규약

- REST: `POST` + JSON. 요청 `{"Input_0": {...}}` / 응답 `Output_0`(+`Output_1`·`Output_2`) + `rsp_cd`·`rsp_msg`
- **`Output_0` 은 배열이 아닐 수 있다.** API 에 따라 객체(집계값)이거나 배열(목록)이다. 타입을 추측하지 말고 `openapi.json` 을 확인한다.
- 계좌 목록: `POST /n2/acctinfo` (입력 없음) → `Output_0[].acct_no` · `acct_type`
  이 `acct_no` 값을 이후 잔고·주문의 **`act_no`** 로 쓴다(필드명은 다르고 값은 같다).
- 페이지네이션: 목록 조회는 응답의 연속조회키(`ctsz16`·`ctsz20`·`ctsz30` 등)를 요청 헤더 `cts` 에 넣어 반복한다.

### 🔴 정규장 / 전체장 — 빠뜨리면 호출이 실패하는 **필수** 파라미터

KRX 거래시간 연장(명세 260911)으로 정규장외 시세가 섞이게 돼, 어느 시간대 기준인지 지정해야 한다.

| 파라미터 | 값 | 필수인 API |
|---|---|---|
| **`view_main_yn`** | `Y` 정규장 · `N` 전체장 | `currentDaily` · `currentExecution` · `period` |
| **`aly_qut_cd`** | `1` 정규장 · `2` 전체장 | `balance` · `assetStatus` · `realizedPnl` |

- ⚠️ **`qut_dit_cd`(UNT/KRX/NXT)와 다른 축이다.** 그쪽은 **시장**, 이쪽은 **시간대**. 둘 다 넣는다.
- 기존 동작 유지 = **정규장(`Y`/`1`)**. 전체장으로 바꾸면 시간외가 섞여 결과가 달라진다.
- `currentPrice` 는 입력 불변. 대신 응답에 `main_cls_*`(정규장 기준)·`market_status` 가 추가됐다.

### ⚠️ 계좌구분(`acct_type`) — 환경과 맞는 계좌를 고른다

| `acct_type` | 용도 | 사용 도메인 |
|---|---|---|
| `01` · `02` | 🔴 운영 (02=주문대리인) | `api.…:8443` |
| `03` | 🟢 모의투자 | `moapi.…:8443` |

계좌목록에는 **여러 구분이 섞여** 내려온다. **첫 계좌를 그대로 쓰지 말 것** — 환경과 다른 구분을 쓰면 실패한다.

### ⚠️ 성공 판정 — HTTP 200 ≠ 업무 성공

- 🔴 **SDK 는 업무 성공/실패를 판정하지 않는다.** 기준은 HTTP 상태코드 하나다.
  **HTTP 200 → 응답 본문 그대로 반환(예외 없음)** / **200 아님 → `NhplugError`**(본문은 `.raw` 에 원문).
- 🔴 **`rsp_msg` 문장을 읽고 판단한다.** **같은 `rsp_cd` 값이 API 에 따라 정상일 수도 오류일 수도 있어**
  어떤 코드 목록도 기준이 될 수 없다. 규약 정본은 llms.txt 「성공 판정」 절.
  ```python
  from nhplug import call, status_of
  data = call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "UNT"})
  rsp_cd, rsp_msg = status_of(data)     # 꺼내 줄 뿐 — 판정하지 않는다
  price = (data.get("Output_0") or {}).get("stck_prpr")
  if price is None:
      print("⚠️ 기대한 값 없음:", rsp_msg)
  ```
- ⚠️ **`if rsp_cd == "00000"` 같은 코드를 절대 쓰지 말 것.** 코드값 비교는 API 를 바꾸면 무너진다.
- 🔴 **주문 등 되돌릴 수 없는 처리 전에는 직전 응답의 `rsp_msg` 를 반드시 확인한다.** SDK 가 막아 주지 않는다.
- ⚠️ `is_success()`·`NHPLUG_SUCCESS_CODES`·`category="business"` 는 **0.4.0 에서 삭제됐다.** 되살리지 말 것.
- `429`(IGW42902, 실측 초당 5회): **자동 재시도하지 않는다.** 호출 간격을 늘려서 호출자가 결정한다.
  **429 재시도에 토큰을 재발급하지 말 것**(보안 알림이 쌓인다). 재발급은 `401` 일 때만.

## 종목마스터 — 전 종목 목록은 REST 가 아니다

```python
from nhplug.instruments import load_master, list_masters
df = load_master("m_new_stock")     # 자동 다운로드·캐시(6h) → 파싱
```

- 전 종목 코드·종목명·업종·지수편입은 **마스터 파일(.mst) 28종**으로 제공된다(REST API 없음).
- 다운로드는 **인증 불필요**. 마스터 받으려고 토큰을 발급하지 말 것.
- **구조체 정본은 포털**이다 — `https://www.nhplug.com/instruments/<파일명>.h` (N2: `www.n2plug.com`)
  `.mst` 와 **1:1 대응**(`m_new_stock.mst` → `m_new_stock.h`) · 인증 불필요 · 파이썬 파서 코드가 주석에 포함돼 있다.
  필드 오프셋·길이가 필요하면 **이 파일을 읽는다.** 추측하지 말 것.

## 실시간 (WebSocket)

```python
from nhplug.realtime import subscribe
subscribe(["005930"], print, max_messages=5)              # 국내 체결가(oc)
subscribe(["AAPL"], print, tr_cd="RC", overseas=True)     # 해외 체결가
```

채널 코드(`tr_cd`)는 자산군 `openapi.json` 의 `x-realtime-channels` 참조. 포트는 BASE_URL 에서 자동 유도(국내 시세·**통보 전부** 7070 · **해외 시세** 7080 · 모의 17070).

- 해외 시세 8종만 7080 — 해외주식 `RH`·`rh`·`RC`·`rc` / 해외파생 `FH`·`fh`·`FC`·`fc`. 나머지는 전부 7070.
- 🔴 **`tr_cd` 를 소문자로 바꾸지 말 것.** 해외주식 지연 `rh`·`rc`(7080) 와 국내파생 지수옵션미니 `rH`·`rC`·`rE`(7070) 는 대소문자만 다르고 포트가 다르다.

## 주문 필드 형식 (중요)

- 종목코드 `iem_cd`: **6자리 그대로**(예: `005930`). 앞에 `A` 를 붙이지 않는다.
- 주문가격 `orr_pr`: **원 단위 정수**(예: `70000`). 소수 금지.
- 지정가 `nmn_pr_tp_cd='01'` + `orr_pr` · 시장가 `'05'`(`orr_pr` 생략)
- **해외주식은 `iem_cd` 가 티커**(예: `AAPL`).
- 매수/매도 가능수량: 국내는 `buyableQuantity`·`sellableQuantity` **2개**, 해외는 `buyableAmount` **1개**에서 `pcs_dit` 로 구분(1 매수금액 / 2 매수수량 / **3 매도수량**).

## 🔒 보안·안전 규칙 (필수)

- 앱키·시크릿·토큰을 **로그·화면에 출력하지 않는다**(일부라도).
- 기본 호출 대상은 **운영(api)** 이며 **주문이 실제 체결된다.** 개발·검증은 **모의투자(`moapi`)** 로 전환한다.
- 주문 실행 전 로그를 남기고, 업무 오류면 **중단**한다.
- **실주문은 사람 확인 절차를 둔다. 완전 무인 실거래는 지양.**
- 주문 함수를 새로 만들면 **`dry_run=True` 를 기본값**으로 두고, 실전송은 명시적으로 켜게 한다.

## 개발 환경

- 프로젝트 전용 가상환경(`.venv`)을 쓴다. 전역 설치 금지.
- 새 의존성은 `requirements.txt`(또는 `pyproject.toml`)에 반영한다. `.venv/`·`.env` 는 커밋하지 않는다.
- 모든 API 호출에 타임아웃·예외처리·에러코드 로깅을 포함한다.

## ⚠️ MCP 와 혼동 금지

- **이 SDK 는 URI 경로**로 호출한다: `call("/krstock/quote/v1/currentPrice", {...})`
- **MCP 는 operationId**: `krstockQuoteCurrentPrice`
- MCP 로 쓰던 이름을 SDK 에 그대로 넣으면 **동작하지 않는다.** 자산군 `README.md` 표에서 **URI 칸**을 쓴다.
