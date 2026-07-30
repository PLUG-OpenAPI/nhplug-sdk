# AGENTS.md — NH투자증권 Open API 개발 규칙 (AI 에이전트용)

이 저장소로 개발하는 AI 코딩 에이전트(Antigravity·Cursor·Claude Code 등)는 아래 규칙을 따른다.

## 저장소 개요
- `nhplug/` : 공용 클라이언트(토큰 발급·캐시, Input_0 봉투, 헤더 자동). 새 코드는 이걸 재사용한다.
- `snippets/` : 기능 단위 실행 샘플(기능당 폴더 = 호출.py + chk_검증.py). 특정 기능 구현 시 참고.
- `examples/` : 카테고리 통합 예제.
- `pipeline/` : 설계→검증→실행 파이프라인 골격.
- `docs/` : 도메인 명세의 로컬 사본 위치(`scripts/fetch_docs.py` 로 받음, 커밋 안 함). 정본은 도메인 URL(아래).

## 문서 (Source of Truth) — 도메인이 정본(SSOT)
- 전체 개요·인증·공통 규약: https://www.nhplug.com/llms.txt (나무) · https://www.n2plug.com/llms.txt (N2)
- 자산군 정본(openapi.json·overview.md·README.md): https://www.nhplug.com/openapi-docs/<domain>/ (나무) · https://www.n2plug.com/openapi-docs/<domain>/ (N2)
  (domain: common · krstock · gbstock · krfuture · gbfuture · krbond · krgold)
- 엔드포인트·필드·형식은 위 **도메인 openapi.json** 을 정본으로 따른다. 로컬 사본이 필요하면 `python scripts/fetch_docs.py` 로 `docs/` 에 받는다(커밋 안 함).
- **에러 처리(중요)**: **HTTP 200 ≠ 업무 성공.** 응답 `rsp_cd` 가 성공 코드가 아니면 실패다.
  성공 코드는 **`00000`·`00166`·`00221`·`13578`** (+ `rsp_msg` 에 "완료" 포함 시 성공으로 보는 안전망).
  ⚠️ `00000`/`00166` 만 성공으로 보는 코드를 새로 쓰지 말 것 — 매수가능수량 조회는 `00221`("조회가 완료되었습니다") 로 응답한다.
  `nhplug.call()` 이 이를 자동 판정해 `NhplugError`(category: auth|rate_limit|business|network|http)를 던진다.
  성공 코드 교체는 `NHPLUG_SUCCESS_CODES`, 예외 없이 원본이 필요하면 `call(..., raise_on_error=False)`.
- **토큰(중요)**: 24시간 유효. `~/.nhplug/` 에 **파일 캐시**되어 프로세스가 바뀌어도 재사용된다(재발급 1회 = 보안 알림 1건).
  캐시 파일 권한은 OS 기본값이다(별도 chmod 없음). 공유 환경이면 `NHPLUG_TOKEN_CACHE_DIR` 로 옮기거나 `NHPLUG_TOKEN_CACHE=0`.
  **재발급은 401(토큰 무효)일 때만.** `429`(유량 초과) 재시도에는 기존 토큰을 그대로 쓴다 — 토큰을 직접 재발급하는 코드를 새로 만들지 말 것.
- **429(IGW42902)**: 자동 재시도하지 않는다. `NhplugError(category="rate_limit")` 로 올라오며 `retry_after_ms` 를 참고해 **호출 간격을 늘려서**(실측 초당 5회 수준) 재시도할지 호출자가 결정한다.

## 인증·통신 규약
- 토큰 발급: POST /oauth2/token, 쿼리파라미터 appkey, appsecretkey, grant_type=client_credentials, scope=oob,
  Content-Type: application/x-www-form-urlencoded → 응답 access_token
- 발급 토큰은 만료 전까지 캐시·재사용한다(매 호출 재발급 금지). → `nhplug/auth.py` 가 이미 처리.
- 이후 REST 호출 헤더: Authorization: Bearer {token} + x-client-id(앱키) + x-client-secret(앱시크릿)
- 요청 바디 {"Input_0": {...}}, 응답 Output_0(+Output_1) + rsp_cd/rsp_msg 봉투. rsp_cd 가 00000 계열이면 정상.
- 계좌 목록: POST /n2/acctinfo (입력 없음) → Output_0[].acct_no. 이 값을 잔고·주문의 act_no 로 사용(필드명 다름, 값 동일).
- 실시간(WebSocket): 접속 wss://<host>:7070(국내)·7080(해외)·moapi 17070. 구독 {"header":{"token":TOKEN,"tr_type":"1"},"body":{"tr_cd":<채널코드>,"tr_key":<종목코드>}}, 해제 tr_type=2. 푸시 {"header":{tr_cd,tr_key},"body":{...}}. 토큰은 header.token 으로만 전달(운영 발급). 채널코드·필드는 자산군 openapi.json 의 x-realtime-channels 참조. 예: snippets/krstock/realtime_execution.

## 주문가능수량 — 국내·해외 구조가 다르다 (중요)
- **국내**: 매수 `/krstock/inquiry/v1/buyableQuantity` · 매도 `/krstock/inquiry/v1/sellableQuantity` — **API 2개로 분리**.
  매도는 명세상 iem_cd 가 선택이지만 **실제로는 필수**(없으면 rsp_cd 10006 "종목코드 항목을 입력하세요").
- **해외**: `/gbstock/inquiry/v1/buyableAmount` **API 1개**에서 `pcs_dit` 로 구분한다.
  1.매수가능금액 2.매수가능수량 **3.매도가능수량** 4.예약매수금액/수량 5.예약매도수량.
  (엔드포인트 이름이 "buyable" 이라 매도가 없어 보이지만, pcs_dit=3 으로 조회한다)
- 응답의 매도가능수량 필드는 국내·해외 모두 `sll_pbl_qty`.
- 샘플: `snippets/krstock/sellable_quantity`, `snippets/gbstock/sellable_quantity`.

## 종목마스터(.mst) — instruments/
- 구조체 **정본은 `instruments/headers/<키>.h`** (오프셋·길이·코드값·다운로드 URL·레코드 크기 포함). 파서(`instruments/master.py`)가 이 헤더를 읽어 동작하므로 **필드를 추측하지 말고 헤더를 읽을 것**.
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

## 보안·안전 규칙 (필수)
- 앱키/앱시크릿은 코드에 하드코딩하지 않는다. .env(NHPLUG_APP_KEY/NHPLUG_APP_SECRET)에서 읽는다. .env 는 커밋 금지.
- 기본 호출 대상은 운영(api). 개발·교육·시뮬레이션은 모의투자(moapi)로 전환한다.
- 주문(매수/매도) 실행 전 로그를 남기고, rsp_cd 가 정상(00000)이 아니면 중단한다.
- 실주문은 사람 확인 절차를 둔다. 완전 무인 실거래는 지양.

## 개발 환경 (프로젝트 격리)
- 전용 가상환경(.venv)을 사용한다. 패키지를 전역(global)에 설치하지 말고 .venv 활성화 후 설치한다.
- 새 의존성은 requirements.txt(또는 pyproject.toml)에 반영한다. .venv/ 는 커밋하지 않는다.

## 코드 스타일
- 언어: Python(requests). 모든 API 호출에 타임아웃·예외처리·에러코드 로깅을 포함한다.
- 인증·HTTP 로직은 nhplug 패키지를 재사용하고 중복 구현하지 않는다.
