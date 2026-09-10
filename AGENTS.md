# AGENTS.md — NH투자증권 Open API 개발 규칙 (AI 에이전트용)

이 저장소로 개발하는 AI 코딩 에이전트(Antigravity·Cursor·Claude Code 등)는 아래 규칙을 따른다.

## 설치 — `pip install nhplug` (패키지명 `nhplug`, 저장소명 `nhplug-sdk`)
- 배포되는 것: `nhplug`(코어) · `nhplug.realtime`(WebSocket) · `nhplug.instruments`(종목마스터 파서 + `.h` 28종).
- 배포되지 않는 것: `snippets/` `examples/` `pipeline/` `guides/` — 저장소를 clone 해서 참고한다.
- `pip install "nhplug[instruments]"` 로 pandas 를 함께 설치하면 마스터가 DataFrame 으로 온다.
- ⚠️ 저장소 경로 `instruments/` 는 설치 시에만 `nhplug/instruments/` 로 매핑된다(`package-dir`).
  **헤더 `.h` 의 GitHub 링크가 포털에 게시돼 있어 저장소 경로를 옮기면 안 된다.**

## 저장소 개요
- `nhplug/` : 공용 클라이언트(토큰 발급·캐시, Input_0 봉투, 헤더 자동) + `realtime.py`. 새 코드는 이걸 재사용한다.
- `snippets/` : 기능 단위 실행 샘플(기능당 폴더 = 호출.py + chk_검증.py). 특정 기능 구현 시 참고.
- `examples/` : 카테고리 통합 예제.
- `pipeline/` : 설계→검증→실행 파이프라인 골격.
- `docs/` : 도메인 명세의 로컬 사본 위치(`scripts/fetch_docs.py` 로 받음, 커밋 안 함). 정본은 도메인 URL(아래).

## 🗺️ 파일 지도 — 무엇을 알고 싶을 때 어디를 여는가

⚠️ **GitHub 은 폴더 목록(`/tree/`)을 크롤러에 막아 둔다.** 아래 링크로 직접 열어야 한다.
파일 목록이 필요하면 이 표와 [README 「구성」 절](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/README.md)을 본다.

| 알고 싶은 것 | 열어볼 파일 |
|---|---|
| REST 호출 · `rsp_cd` 판정 · **연속조회** · **유량 스로틀** | [nhplug/client.py](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/nhplug/client.py) |
| WebSocket 구독 · 포트 라우팅 · **서버 한도** · TLS | [nhplug/realtime.py](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/nhplug/realtime.py) |
| 토큰 발급·캐시 · **호스트 가드** · 브랜드 판정 | [nhplug/auth.py](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/nhplug/auth.py) |
| 오류 분류(`config`·`auth`·`rate_limit`·`business`…) | [nhplug/errors.py](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/nhplug/errors.py) |
| `.env` 탐색 순서 | [nhplug/\_env.py](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/nhplug/_env.py) |
| **실시간 채널 27종** · `tr_key` 대응표 | [docs/realtime_channels.md](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/docs/realtime_channels.md) |
| **종목마스터 28종** 목록 · 파서 사용법 | [instruments/README.md](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/instruments/README.md) |
| `.mst` 파싱 구현 | [instruments/master.py](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/instruments/master.py) |
| **SDK 없이** 원시 호출(urllib·requests) | [snippets/standalone/README.md](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/snippets/standalone/README.md) |
| 계좌구분(`acct_type`) 판정 예제 | [snippets/common/list_accounts](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/snippets/common/list_accounts/list_accounts.py) |
| 실시간 구독 예제·검증 | [snippets/krstock/realtime_execution](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/snippets/krstock/realtime_execution/chk_realtime_execution.py) |
| AI IDE 규칙 파일(고객 배포용) | [templates/README.md](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/templates/README.md) |
| 설치부터 첫 실행까지 절차 | [guides/antigravity.md](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/guides/antigravity.md) |
| **대화로 조회**(MCP 서버) | [nhplug-mcp](https://github.com/PLUG-OpenAPI/nhplug-mcp) |

**명세 자체**를 알고 싶으면 저장소가 아니라 도메인을 본다 → 아래 「문서 (Source of Truth)」 절.

## 문서 (Source of Truth) — 도메인이 정본(SSOT)
- 전체 개요·인증·공통 규약: https://www.nhplug.com/llms.txt (나무) · https://www.n2plug.com/llms.txt (N2)
- 자산군 정본(openapi.json·overview.md·README.md): https://www.nhplug.com/openapi-docs/<domain>/ (나무) · https://www.n2plug.com/openapi-docs/<domain>/ (N2)
  (domain: common · krstock · gbstock · krfuture · gbfuture · krbond · krgold)
- 엔드포인트·필드·형식은 위 **도메인 openapi.json** 을 정본으로 따른다. 로컬 사본이 필요하면 `python scripts/fetch_docs.py` 로 `docs/` 에 받는다(커밋 안 함).
- 🔴 **에러 처리(가장 중요)**: **HTTP 200 ≠ 업무 성공.** 그리고 **`rsp_cd` 만으로 판정하지 말 것.**
  **`rsp_msg` 의 내용이 우선**이다. **같은 `rsp_cd` 값이 API 에 따라 정상일 수도 오류일 수도 있다.**
  판정 규약 정본은 [llms.txt](https://www.nhplug.com/llms.txt) (N2: https://www.n2plug.com/llms.txt).
  ```python
  data = call("/krstock/...", {...})
  # 중요한 처리라면 메시지를 직접 확인한다
  print(data.get("rsp_cd"), data.get("rsp_msg"))
  ```
  ⚠️ **`if rsp_cd == "00000"` 같은 코드를 쓰지 말 것.** 특정 코드값을 하드코딩한 판정은 API 를 바꾸면 무너진다.
  `nhplug.call()` 이 1차 판정해 `NhplugError`(category: config|auth|rate_limit|business|network|http)를 던지지만,
  **그 판정은 라이브에서 관찰된 코드 목록 + "완료" 메시지 기반이라 전수가 아니다.** 예외 없이 원본이 필요하면
  `call(..., raise_on_error=False)` 로 받아 `rsp_msg` 를 직접 본다.
  (관찰된 정상 응답 예: `00000` 현재가·계좌목록 / `00166` 잔고 / `00221` 매수가능수량 / `13578` 조회 내역 없음
   — **참고용 예시이며 판정 기준이 아니다.**)
- **토큰(중요)**: 24시간 유효. `~/.nhplug/` 에 **파일 캐시**되어 프로세스가 바뀌어도 재사용된다(재발급 1회 = 보안 알림 1건).
  캐시 파일 권한은 OS 기본값이다(별도 chmod 없음). 공유 환경이면 `NHPLUG_TOKEN_CACHE_DIR` 로 옮기거나 `NHPLUG_TOKEN_CACHE=0`.
  **재발급은 401(토큰 무효)일 때만.** `429`(유량 초과) 재시도에는 기존 토큰을 그대로 쓴다 — 토큰을 직접 재발급하는 코드를 새로 만들지 말 것.
- **429(IGW42902)**: 자동 재시도하지 않는다. `NhplugError(category="rate_limit")` 로 올라오며 `retry_after_ms` 를 참고해 **호출 간격을 늘려서**(실측 초당 5회 수준) 재시도할지 호출자가 결정한다.

## ⚠️ MCP 와 SDK 는 호출 식별자가 다르다 (섞지 말 것)
- **SDK 는 URI 경로**로 호출한다: `call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})`
- **MCP 는 operationId**로 호출한다: `call_api("krstockQuoteCurrentPrice", {...})`
- `call("krstockQuoteCurrentPrice", ...)` 처럼 **operationId 를 SDK 에 넣으면 실패한다.**
  MCP 로 조회하던 흐름을 그대로 코드로 옮길 때 자주 발생하는 실수다.
- 이 차이는 의도된 것이다. **경로는 프로토콜 식별자**(실제 HTTP 주소)이고,
  **operationId 는 명세 문서의 이름표**라 명세 재생성 시 바뀌거나 사라질 수 있다.
- 자산군 `README.md` 표에 `URI` 와 `operationId` 가 나란히 있다 — **SDK 코드에는 `URI` 칸을 쓴다.**

## 인증·통신 규약
- 토큰 발급: POST /oauth2/token, 쿼리파라미터 appkey, appsecretkey, grant_type=client_credentials, scope=oob,
  Content-Type: application/x-www-form-urlencoded → 응답 access_token
- 발급 토큰은 만료 전까지 캐시·재사용한다(매 호출 재발급 금지). → `nhplug/auth.py` 가 이미 처리.
- 이후 REST 호출 헤더: Authorization: Bearer {token} + x-client-id(앱키) + x-client-secret(앱시크릿)
- 요청 바디 {"Input_0": {...}}, 응답 Output_0(+Output_1) + rsp_cd/rsp_msg 봉투.
  **성공 판정은 위 「에러 처리」 절을 따른다** — `rsp_msg` 우선, `rsp_cd` 단독 판정 금지.
  특정 코드값을 하드코딩하지 말고 `nhplug.call()` 에 맡기거나 `rsp_msg` 를 직접 확인한다.
- 계좌 목록: POST /n2/acctinfo (입력 없음) → Output_0[].acct_no · acct_type. acct_no 값을 잔고·주문의 act_no 로 사용(필드명 다름, 값 동일).

## 계좌구분(acct_type) — 환경과 맞는 계좌를 골라야 한다 (중요)
- `/n2/acctinfo` 는 **여러 구분의 계좌를 섞어서** 내려준다. 계좌구분이 호출 환경을 결정한다.

  | `acct_type` | 용도 | 사용 도메인 |
  |---|---|---|
  | `01` | 🔴 운영 (일반) | `api.…:8443` |
  | `02` | 🔴 운영 (주문대리인) | `api.…:8443` |
  | `03` | 🟢 모의투자 | `moapi.…:8443` |

- **운영 도메인에 `03` 계좌를, 모의투자 도메인에 `01`·`02` 계좌를 쓰면 실패한다.** 첫 계좌를 무조건 집어 쓰는 코드를 쓰지 말 것.
- 헬퍼: `snippets/common/list_accounts` 의 `usable_accounts()` 가 현재 `NHPLUG_BASE_URL` 환경에 맞는 계좌만 걸러 준다(`current_env()` 로 live/mock 판별).
- 실시간(WebSocket): 접속 wss://<host>:7070(국내 시세 + **통보 전부**)·7080(**해외 시세 8종** — 해외주식 RH·rh·RC·rc / 해외파생 FH·fh·FC·fc)·moapi 17070. ⚠️ 채널코드는 **대소문자 구분** — 해외주식 지연 `rh`·`rc`(7080) vs 국내파생 지수옵션미니 `rH`·`rC`·`rE`(7070). tr_cd 를 소문자로 정규화하지 말 것. 구독 {"header":{"token":TOKEN,"tr_type":"1"},"body":{"tr_cd":<채널코드>,"tr_key":<종목코드>}}, 해제 tr_type=2. 푸시 {"header":{tr_cd,tr_key},"body":{...}}. 토큰은 header.token 으로만 전달(운영 발급). 채널코드·필드는 자산군 openapi.json 의 x-realtime-channels 참조. 예: snippets/krstock/realtime_execution.

## 주문가능수량 — 국내·해외 구조가 다르다 (중요)
- **국내**: 매수 `/krstock/inquiry/v1/buyableQuantity` · 매도 `/krstock/inquiry/v1/sellableQuantity` — **API 2개로 분리**.
  매도는 명세상 iem_cd 가 선택이지만 **실제로는 필수**(없으면 rsp_cd 10006 "종목코드 항목을 입력하세요").
- **해외**: `/gbstock/inquiry/v1/buyableAmount` **API 1개**에서 `pcs_dit` 로 구분한다.
  1.매수가능금액 2.매수가능수량 **3.매도가능수량** 4.예약매수금액/수량 5.예약매도수량.
  (엔드포인트 이름이 "buyable" 이라 매도가 없어 보이지만, pcs_dit=3 으로 조회한다)
- 응답의 매도가능수량 필드는 국내·해외 모두 `sll_pbl_qty`.
- 샘플: `snippets/krstock/sellable_quantity`, `snippets/gbstock/sellable_quantity`.

## 종목마스터(.mst) — instruments/
- 🔴 **구조체 정본은 포털**이다 — `https://www.nhplug.com/instruments/<파일명>.h` (N2: `www.n2plug.com`).
  `.mst` 와 1:1 대응이며 인증 없이 받을 수 있다. 필드 오프셋·길이가 필요하면 이 파일을 읽는다.
- 파서(`instruments/master.py`)는 **`.h` 를 포털에서 받아서** 쓴다(`.mst` 와 같은 서버 · 캐시 6h).
  구조체가 개정돼도 **자동 반영**되며 PyPI 재배포가 필요 없다.
  저장소의 `instruments/headers/*.h` (28종)는 **오프라인 폴백**이며 정본이 아니다
  (원격을 끄려면 `NHPLUG_HEADERS_REMOTE=0`). **필드를 추측하지 말고 헤더를 읽을 것.**
- 사용: `from master import load_master; df = load_master("m_new_stock")` (자동 다운로드·캐시). 포털에서 받은 파일은 `path=` 로 지정.
- **다운로드는 인증 불필요**(토큰·`x-client-*` 헤더 없이 공개 접근). 마스터 받으려고 토큰을 발급하지 말 것.
- **브랜드**: `.h` 의 `@url` 은 나무(`www.nhplug.com/instruments`) 기준이다. **N2 는 `NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments`** 로 전환한다(캐시는 도메인별로 분리됨).
- 공통 규칙: CP949 · 고정길이 · 파일헤더 없음 · 레코드 끝 1B LF · **반드시 "rb" 로 열 것** · NUL 종료 아님(길이 슬라이싱 후 rstrip) · **파일크기 % 레코드크기 == 0** 검증 필수.
- 함정(파서가 이미 처리): 지수옵션 `sPrice`는 ×100이라 **/100** 필요(주식옵션 `sValue`는 스케일 없음) · 위클리 `sMonth`는 **YYMMWW(주차)** · 콜풋은 **CP949 한글 2바이트** · 지수편입은 **`=="Y"`로만** 판정(공백≠N) · 한글종목명 선두 `*`·`#`는 지수 마커.
- `.mst` 원본은 **커밋 금지**(gitignore). 매일 갱신되며 포털이 배포 정본.

## 주문 필드 형식 (중요)
- 종목코드 iem_cd: 6자리 그대로 (예: 005930, 앞에 'A' 붙이지 않는다)
- 주문가격 orr_pr: 원 단위 정수 그대로 (예: 70000). 지정가 nmn_pr_tp_cd='01' + orr_pr, 시장가='05'(orr_pr 생략)
- 시세 조회(현재가 등) 종목코드도 iem_cd(6자리) + market_cd(KRX/NXT/UNT) 를 쓴다. (구 shrn_iscd 폐지)
- 형식이 의심되면 해당 자산군 openapi.json 의 operation 예시를 확인한다: https://www.nhplug.com/openapi-docs/<domain>/openapi.json (또는 `python scripts/fetch_docs.py` 후 docs/<domain>/openapi.json).

## 환경 (Base URL) — 호출 대상은 .env 의 NHPLUG_BASE_URL, 기본값 api(운영)
- 🔴 운영 (Live) [기본]:             https://api.nhplug.com:8443
- 🟢 모의투자 (Mock) 교육·시뮬레이션: https://moapi.nhplug.com:8443
- 접근토큰(/oauth2/token)은 운영(api) 전용 — 모의투자 미제공. 호출이 moapi 여도 토큰은 api 에서 발급(NHPLUG_AUTH_URL, 기본 api).
- **브랜드(도메인)**: 위는 나무(nhplug.com) 기준. **N2 고객은 NHPLUG_BASE_URL·NHPLUG_AUTH_URL 을 둘 다 n2plug.com 으로** 설정한다(운영 api.n2plug.com / 모의 moapi.n2plug.com). API·필드는 동일, 도메인만 다름. AUTH_URL 까지 같은 브랜드로 안 바꾸면 토큰 발급이 실패한다.

## 설정 파일 — 한 곳만 고친다 (중요)
- 자격증명·도메인은 **`.env` 한 파일**에서 읽는다. 코드에 URL·키를 직접 쓰거나 스크립트마다 따로 지정하지 말 것.
- 우선순위: **실제 환경변수 > `NHPLUG_ENV_FILE` > 프로젝트 `.env`(CWD 기준 상위 탐색) > 전역 `~/.nhplug/.env`**.
  빈 값은 다음 순위에서 보충되므로, 전역에 공통 설정을 두고 프로젝트에서 필요한 줄만 덮어쓸 수 있다.
- 어떤 파일을 읽었는지는 `from nhplug import loaded_files; loaded_files()` 로 확인한다(설정 문제 진단 1순위).
- ⚠️ **브랜드 전환은 3줄 모두**: `NHPLUG_BASE_URL`(호출) · `NHPLUG_AUTH_URL`(토큰) · `NHPLUG_INSTRUMENTS_BASE`(종목마스터).
  하나라도 빠지면 그 기능만 조용히 나무 도메인으로 간다. 실시간(WS) 주소는 BASE_URL 에서 자동 유도된다.

## 보안·안전 규칙 (필수)
- 앱키/앱시크릿은 코드에 하드코딩하지 않는다. .env(NHPLUG_APP_KEY/NHPLUG_APP_SECRET)에서 읽는다. .env 는 커밋 금지.
- 기본 호출 대상은 운영(api). 개발·교육·시뮬레이션은 모의투자(moapi)로 전환한다.
- 주문(매수/매도) 실행 전 로그를 남기고, **업무 오류면 중단한다**(판정은 위 「에러 처리」 절 — `rsp_msg` 우선).
  `nhplug.call()` 을 쓰면 `NhplugError` 로 올라오므로 예외를 잡아 중단하면 된다.
- 실주문은 사람 확인 절차를 둔다. 완전 무인 실거래는 지양.

## 개발 환경 (프로젝트 격리)
- 전용 가상환경(.venv)을 사용한다. 패키지를 전역(global)에 설치하지 말고 .venv 활성화 후 설치한다.
- 새 의존성은 requirements.txt(또는 pyproject.toml)에 반영한다. .venv/ 는 커밋하지 않는다.

## 코드 스타일
- 언어: Python(requests). 모든 API 호출에 타임아웃·예외처리·에러코드 로깅을 포함한다.
- 인증·HTTP 로직은 nhplug 패키지를 재사용하고 중복 구현하지 않는다.
