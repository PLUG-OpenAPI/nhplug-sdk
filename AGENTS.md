# AGENTS.md — NH투자증권 Open API 개발 규칙 (AI 에이전트용)

이 저장소로 개발하는 AI 코딩 에이전트(Antigravity·Cursor·Claude Code 등)는 아래 규칙을 따른다.

## 저장소 개요
- `nhplug/` : 공용 클라이언트(토큰 발급·캐시, Input_0 봉투, 헤더 자동). 새 코드는 이걸 재사용한다.
- `snippets/` : 기능 단위 실행 샘플(기능당 폴더 = 호출.py + chk_검증.py). 특정 기능 구현 시 참고.
- `examples/` : 카테고리 통합 예제.
- `pipeline/` : 설계→검증→실행 파이프라인 골격.
- `docs/` : 도메인 명세의 로컬 사본 위치(`scripts/fetch_docs.py` 로 받음, 커밋 안 함). 정본은 도메인 URL(아래).

## 문서 (Source of Truth) — 도메인이 정본(SSOT)
- 전체 개요·인증·공통 규약: https://www.nhplug.com/llms.txt
- 자산군 정본(openapi.json·overview.md·README.md): https://www.nhplug.com/openapi-docs/<domain>/
  (domain: common · krstock · gbstock · krfuture · gbfuture · krbond · krgold)
- 엔드포인트·필드·형식은 위 **도메인 openapi.json** 을 정본으로 따른다. 로컬 사본이 필요하면 `python scripts/fetch_docs.py` 로 `docs/` 에 받는다(커밋 안 함).
- 에러 처리: `rsp_cd` `00000`/`00166` 계열=정상, 그 외는 실패로 간주. `IGW…` 계열은 인증·키·환경 문제. 호출제한·상세 코드는 포털 정책 참조.

## 인증·통신 규약
- 토큰 발급: POST /oauth2/token, 쿼리파라미터 appkey, appsecretkey, grant_type=client_credentials, scope=oob,
  Content-Type: application/x-www-form-urlencoded → 응답 access_token
- 발급 토큰은 만료 전까지 캐시·재사용한다(매 호출 재발급 금지). → `nhplug/auth.py` 가 이미 처리.
- 이후 REST 호출 헤더: Authorization: Bearer {token} + x-client-id(앱키) + x-client-secret(앱시크릿)
- 요청 바디 {"Input_0": {...}}, 응답 Output_0(+Output_1) + rsp_cd/rsp_msg 봉투. rsp_cd 가 00000 계열이면 정상.
- 계좌 목록: POST /n2/acctinfo (입력 없음) → Output_0[].acct_no. 이 값을 잔고·주문의 act_no 로 사용(필드명 다름, 값 동일).

## 주문 필드 형식 (중요)
- 종목코드 iem_cd: 6자리 그대로 (예: 005930, 앞에 'A' 붙이지 않는다)
- 주문가격 orr_pr: 원 단위 정수 그대로 (예: 70000). 지정가 nmn_pr_tp_cd='01' + orr_pr, 시장가='05'(orr_pr 생략)
- 시세 조회(현재가 등) 종목코드도 iem_cd(6자리) + market_cd(KRX/NXT/UNT) 를 쓴다. (구 shrn_iscd 폐지)
- 형식이 의심되면 해당 자산군 openapi.json 의 operation 예시를 확인한다: https://www.nhplug.com/openapi-docs/<domain>/openapi.json (또는 `python scripts/fetch_docs.py` 후 docs/<domain>/openapi.json).

## 환경 (Base URL) — 호출 대상은 .env 의 NHPLUG_BASE_URL, 기본값 api(운영)
- 🔴 운영 (Live) [기본]:             https://api.nhplug.com:8443
- 🟢 모의투자 (Mock) 교육·시뮬레이션: https://moapi.nhplug.com:8443
- 접근토큰(/oauth2/token)은 운영(api) 전용 — 모의투자 미제공. 호출이 moapi 여도 토큰은 api 에서 발급(NHPLUG_AUTH_URL, 기본 api).

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
