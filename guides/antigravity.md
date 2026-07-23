# NH투자증권 Open API × Google Antigravity — 바이브코딩 사전 준비 & 테스트 가이드

이 문서는 **Google Antigravity(에이전트형 AI IDE)** 에서 NH투자증권 Open API **명세 파일(`llms.txt` · `openapi.json` · `README.md`)만** 가지고 프로그램을 AI로 개발하기 위한 **사전 준비**와 **간단한 동작 테스트** 방법을 안내합니다. (MCP 연동 없이 진행)

> ⚠️ 자동매매는 실제 손실이 발생할 수 있습니다. **운영(`api`)이 기본이며 실제 주문이 체결됩니다.** 개발·검증 예제는 반드시 **모의투자 환경(`moapi`)** 에서 먼저 돌리고, 실주문은 사람이 최종 확인하세요. (접근토큰은 운영 전용이라, moapi 호출에도 토큰은 `api` 에서 발급됩니다.)

---

## 0. 준비물

1. **Google Antigravity** 설치 — [antigravity.google](https://antigravity.google)
2. **Python 3.10+** 또는 **Node.js 18+** (예제는 Python 기준)
3. **NH투자증권 Open API 앱키/앱시크릿** — 포털 [www.nhplug.com](https://www.nhplug.com/intro) 에서 발급
4. (권장) 처음엔 **모의투자 환경**으로 시작

---

## 1. 사전 준비

### 1-1. 프로젝트 폴더 만들고 Antigravity로 열기

1. 빈 폴더 생성 (예: `nh-api-test`)
2. Antigravity 실행 → **Open Folder** → 그 폴더 선택

> **프로젝트는 폴더 하나 = 프로젝트 하나로 분리하세요.** Antigravity(IDE)는 공용이어도, 아래 가상환경을 프로젝트마다 두면 서로 간섭하지 않습니다.

### 1-2. 프로젝트 전용 가상환경(venv) 만들기 ⭐

파이썬 패키지를 **전역(`pip install`)에 설치하면 모든 프로젝트가 하나의 시스템 파이썬을 공유**해 버전 충돌·오류 추적이 어려워집니다. 프로젝트마다 **가상환경(venv)** 을 두면 패키지가 그 폴더 안에만 설치되어 완전히 분리됩니다.

Antigravity 내장 터미널에서(프로젝트 폴더 기준):

```powershell
# 1) 가상환경 생성 (프로젝트당 최초 1회)
python -m venv .venv

# 2) 활성화 — PowerShell
.\.venv\Scripts\Activate.ps1
#   (cmd: .venv\Scripts\activate.bat  ·  macOS/Linux: source .venv/bin/activate)

# 3) 이제 pip install 은 이 프로젝트 안에만 설치됨
pip install requests python-dotenv

# 4) 의존성 고정 (재현성·디버깅 용이)
pip freeze > requirements.txt
```

프롬프트 앞에 `(.venv)` 가 보이면 활성화 상태입니다. **새 터미널을 열 때마다 2)번으로 다시 활성화**하세요. `.venv/` 는 커밋하지 말고(`.gitignore` 에 추가), `requirements.txt` 만 공유하면 어디서든 `pip install -r requirements.txt` 로 동일 환경을 재현할 수 있습니다.

> 더 강한 격리가 필요하면 프로젝트별 **Dev Container(Docker)** 나 `uv` 도 있지만, 개인 개발엔 venv 로 충분합니다. Node 프로젝트는 폴더별 `node_modules` 로 이미 분리됩니다.

### 1-3. API 명세 — 도메인이 정본(SSOT)

명세를 저장소에 복사해 둘 필요가 없습니다. **정본은 도메인**이며, `AGENTS.md`(1-4) 에 URL 을 적어두면 AI 가 직접 참조합니다.

- 전체 개요·인증·공통 규약: https://www.nhplug.com/llms.txt
- 자산군 정본: `https://www.nhplug.com/openapi-docs/<자산>/{openapi.json, overview.md, README.md}`
  - 자산: `common`(필수·인증/계좌) · `krstock` · `gbstock` · `krfuture` · `gbfuture` · `krbond` · `krgold`

오프라인이거나 AI 에 로컬 파일로 주고 싶으면, 프로젝트 폴더에서 아래로 필요한 자산만 내려받으세요:

```bash
python - <<'PY'
import urllib.request, os
BASE, want = "https://www.nhplug.com", ["common", "krstock"]   # 필요한 자산만
os.makedirs("docs", exist_ok=True)
urllib.request.urlretrieve(f"{BASE}/llms.txt", "docs/llms.txt")
for a in want:
    os.makedirs(f"docs/{a}", exist_ok=True)
    for f in ("openapi.json", "overview.md", "README.md"):
        urllib.request.urlretrieve(f"{BASE}/openapi-docs/{a}/{f}", f"docs/{a}/{f}")
print("done")
PY
```

> `llms.txt` 와 `common` 은 필수(인증·계좌 흐름의 정본). 개발 대상 자산만 `want` 에 추가하면 됩니다.

### 1-4. `AGENTS.md` 규칙 파일 작성

Antigravity는 프로젝트 루트의 **`AGENTS.md`** 를 세션 시작 시 자동으로 읽어 규칙으로 삼습니다. 여기에 문서 위치·인증 규약·안전수칙을 적어두면 AI가 매번 정확하게 코딩합니다. **부록 A의 템플릿을 그대로 `AGENTS.md` 로 저장**하세요.

### 1-5. `.env` 파일 준비

앱키/시크릿을 코드에 넣지 말고 `.env` 로 분리합니다(부록 B). `.gitignore` 에 `.env` 를 추가하세요.

---

## 2. 간단한 동작 테스트

목표: **토큰 발급 → 계좌목록 → 현재가 조회**가 실제로 되는지 확인. Antigravity 에이전트에게 아래처럼 시킵니다.

### 2-1. 컨텍스트 인식시키기 (첫 프롬프트)

```
이 프로젝트의 AGENTS.md 규칙과 거기 적힌 NH Open API 명세(도메인 URL 또는 docs/ 로컬 사본)를 먼저 읽어줘.
읽고 나서, 어떤 엔드포인트로 인증·계좌조회·시세조회를 하는지 요약해줘.
```

### 2-2. 테스트 스크립트 생성 (두 번째 프롬프트)

```
docs 명세를 기준으로, 모의투자(moapi) 환경에서 아래를 수행하는
파이썬 스크립트 test_nh.py 를 만들어줘.
1) /oauth2/token 으로 접근 토큰 발급 (앱키/시크릿은 .env 에서 읽기)
2) /n2/acctinfo 로 내 계좌 목록 조회 후 출력
3) 삼성전자(005930) 현재가 조회 후 출력
토큰은 발급 후 재사용하고, 모든 호출에 타임아웃과 에러 처리를 넣어줘.
```

### 2-3. 실행

Antigravity 내장 터미널에서 (가상환경 활성화 상태에서):

```powershell
# 1-2 에서 만든 가상환경 활성화 (새 터미널이면 매번)
.\.venv\Scripts\Activate.ps1
pip install requests python-dotenv
python test_nh.py
```

계좌 목록과 삼성전자 현재가가 출력되면 **사전 준비 완료**입니다. 이후 "이 위에 5일/20일 이평 골든크로스 매수 로직을 붙여줘" 같은 식으로 확장하면 됩니다. (주문 로직은 반드시 모의투자에서, 부록 A의 안전규칙 적용)

> 에러가 나면 터미널 메시지를 그대로 복사해 "이 오류 고쳐줘"라고 하면 됩니다. 자주 나는 오류는 아래 표 참고.

---

## 3. 자주 막히는 점

| 증상 | 해결 |
|---|---|
| 토큰 403 "유효하지 않은 AppSecret" | 키가 그 환경용인지 확인. base url 을 키에 맞는 환경으로 (모의/실거래·개발/운영) |
| 계좌번호 오류 | 계좌목록 응답은 `acct_no`, 잔고·주문 입력은 `act_no` — 값은 동일하니 그대로 사용 |
| 응답 파싱 실패 | 요청 `{"Input_0": {...}}` / 응답 `Output_0`(+`Output_1`) 봉투, `rsp_cd`=`00000` 정상 |
| 주문 거부/형식오류 | `iem_cd` 는 6자리 그대로(예: 005930, `A` 없음), `orr_pr` 은 원 단위 정수 그대로(예: 70000). 형식은 describe_api/openapi.json 최신 예시 기준 |
| 토큰 매번 재발급 | 발급 토큰을 만료까지 캐시·재사용 |

---

## 부록 A. `AGENTS.md` 붙여넣기 템플릿

프로젝트 루트에 `AGENTS.md` 로 저장하세요.

```markdown
# 프로젝트 규칙 — NH투자증권 Open API 개발

## 문서 (Source of Truth) — 도메인이 정본
- API 개요·인증·공통 규약: https://www.nhplug.com/llms.txt
- 자산군 정본: https://www.nhplug.com/openapi-docs/<자산>/openapi.json
  (자산: common·krstock·gbstock·krfuture·gbfuture·krbond·krgold)
- 코드 작성 전 위 문서를 먼저 참고하고, 엔드포인트·필드는 openapi.json 을 정본으로 따른다. (로컬 사본이 필요하면 docs/ 에 내려받아 사용)

## 인증·통신 규약
- 토큰 발급: POST /oauth2/token, 쿼리파라미터 appkey, appsecretkey,
  grant_type=client_credentials, scope=oob, Content-Type: application/x-www-form-urlencoded → 응답 access_token
- 발급 토큰은 만료 전까지 캐시·재사용 (매 호출 재발급 금지)
- 이후 REST 호출 헤더: Authorization: Bearer {token} + x-client-id(앱키) + x-client-secret(앱시크릿)
- 요청 바디 {"Input_0": {...}}, 응답 Output_0(+Output_1) + rsp_cd/rsp_msg 봉투
- 계좌 목록: POST /n2/acctinfo (입력 없음) → Output_0[].acct_no. 이 값을 잔고·주문의 act_no 로 사용
- 주문 종목코드 iem_cd: 6자리 그대로 (예: 005930). 주문가격 orr_pr: 원 단위 정수 그대로 (예: 70000)
- 필드 형식은 항상 describe_api / openapi.json 의 최신 예시를 정본으로 따른다

## 환경 (Base URL)
- 🔴 운영 (Live) [기본]:             https://api.nhplug.com:8443
- 🟢 모의투자 (Mock) 교육·시뮬레이션: https://moapi.nhplug.com:8443
- 접근토큰(/oauth2/token)은 운영(api) 전용 — 모의투자 미제공. 호출이 moapi 여도 토큰은 api 에서 발급.
- 호출 대상은 .env 의 NHPLUG_BASE_URL(기본 api), 토큰은 NHPLUG_AUTH_URL(기본 api).

## 보안·안전 규칙 (필수)
- 앱키/앱시크릿은 코드에 하드코딩 금지, .env 에서 읽는다. .env 는 .gitignore 에 넣는다.
- 기본 호출 대상은 운영(api). 개발·교육·시뮬레이션은 모의투자(moapi)로 전환한다.
- 주문(매수/매도) 실행 전 로그를 남기고, rsp_cd 가 00000 이 아니면 중단한다.
- 실주문은 사람 확인 절차를 둔다. 완전 무인 실거래는 지양.

## 개발 환경 (프로젝트 격리)
- 이 프로젝트는 전용 가상환경 .venv 를 사용한다. 패키지를 전역(global)에 설치하지 말고, 항상 .venv 활성화 후 설치·실행한다.
- 새 의존성을 추가하면 requirements.txt 를 갱신한다(pip freeze > requirements.txt).
- .venv/ 와 .env 는 커밋하지 않는다(.gitignore).

## 코드 스타일
- 언어: Python(requests). 토큰/HTTP 로직은 별도 모듈로 분리.
- 모든 API 호출에 타임아웃·예외처리·에러코드 로깅 포함.
```

## 부록 B. `.env` 템플릿

```
NHPLUG_APP_KEY=발급받은_APP_KEY
NHPLUG_APP_SECRET=발급받은_APP_SECRET
NHPLUG_BASE_URL=https://api.nhplug.com:8443
NHPLUG_AUTH_URL=https://api.nhplug.com:8443   # 토큰은 운영 전용(moapi 미제공)
```

---

*문의: apisupport@nhsec.com · 자동매매 예제는 학습·테스트 목적이며, 투자 손실 책임은 이용자에게 있습니다.*
