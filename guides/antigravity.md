# NH투자증권 Open API × Google Antigravity — 바이브코딩 사전 준비 & 테스트 가이드

이 문서는 **Google Antigravity(에이전트형 AI IDE)** 에서 NH투자증권 Open API **명세 파일(`llms.txt` · `openapi.json` · `README.md`)만** 가지고 프로그램을 AI로 개발하기 위한 **사전 준비**와 **간단한 동작 테스트** 방법을 안내합니다. (MCP 연동 없이 진행)

> ⚠️ 자동매매는 실제 손실이 발생할 수 있습니다. **운영(`api`)이 기본이며 실제 주문이 체결됩니다.** 개발·검증 예제는 반드시 **모의투자 환경(`moapi`)** 에서 먼저 돌리고, 실주문은 사람이 최종 확인하세요. (접근토큰은 운영 전용이라, moapi 호출에도 토큰은 `api` 에서 발급됩니다.)

---

## 0. 준비물

1. **Google Antigravity** 설치 — [antigravity.google](https://antigravity.google)
2. **Python 3.11 이상** (`python --version` 으로 확인 — SDK 패키지 `nhplug` 의 최소 요구 버전)
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

# 3) NH SDK 설치 — 이 프로젝트 안에만 설치됨
pip install nhplug
#   종목마스터를 표(DataFrame)로 다루려면:  pip install "nhplug[instruments]"

# 4) 의존성 고정 (재현성·디버깅 용이)
pip freeze > requirements.txt
```

> `nhplug` 를 설치하면 **인증·토큰 캐시·`Input_0` 봉투·성공코드 판정·실시간·종목마스터**가 함께 들어옵니다.
> `requests` 로 토큰 발급을 직접 짜지 마세요 — 이미 검증된 코드가 있습니다.

프롬프트 앞에 `(.venv)` 가 보이면 활성화 상태입니다. **새 터미널을 열 때마다 2)번으로 다시 활성화**하세요. `.venv/` 는 커밋하지 말고(`.gitignore` 에 추가), `requirements.txt` 만 공유하면 어디서든 `pip install -r requirements.txt` 로 동일 환경을 재현할 수 있습니다.

> 더 강한 격리가 필요하면 프로젝트별 **Dev Container(Docker)** 나 `uv` 도 있지만, 개인 개발엔 venv 로 충분합니다. Node 프로젝트는 폴더별 `node_modules` 로 이미 분리됩니다.

### 1-3. API 명세 — 도메인이 정본(SSOT)

명세를 저장소에 복사해 둘 필요가 없습니다. **정본은 도메인**이며, 아래 1-4 의 규칙 파일에 URL 이 적혀 있어 AI 가 직접 참조합니다.

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

### 1-4. AI 규칙 파일 넣기 ⭐

AI 도구는 프로젝트의 **규칙 파일**을 세션 시작 시 자동으로 읽습니다. 없으면 AI 가 필드명·성공코드·환경을 **추측**해서 틀린 코드를 만듭니다.

**쓰는 도구에 맞는 파일을 프로젝트에 넣으세요.**

| 도구 | 파일 | 위치 |
|---|---|---|
| **Antigravity** · Codex | `AGENTS.md` | 루트 |
| Claude Code | `CLAUDE.md` | 루트 |
| **Cursor** | `nhplug.mdc` | **`.cursor/rules/`** |

```powershell
# Antigravity (PowerShell)
iwr -useb https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/AGENTS.md -OutFile AGENTS.md

# Cursor
New-Item -ItemType Directory -Force .cursor\rules | Out-Null
iwr -useb https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/cursor/nhplug.mdc -OutFile .cursor\rules\nhplug.mdc
```

macOS·Linux 는 `curl -O`, 또는 브라우저로 열어 복사해도 됩니다.

> ⚠️ **Cursor 사용자**: 예전 방식인 `.cursorrules` 파일은 **Agent 모드에서 무시됩니다.** 반드시 `.cursor/rules/` 경로에 두세요.

전체 목록과 설명: **[templates/](https://github.com/PLUG-OpenAPI/nhplug-sdk/tree/main/templates)**

### 1-5. `.env` 파일 준비

앱키/시크릿을 코드에 넣지 말고 `.env` 로 분리합니다(부록 B). `.gitignore` 에 `.env` 를 추가하세요.

---

## 2. 간단한 동작 테스트

목표: **토큰 발급 → 계좌목록 → 현재가 조회**가 실제로 되는지 확인. Antigravity 에이전트에게 아래처럼 시킵니다.

### 2-1. 컨텍스트 인식시키기 (첫 프롬프트)

```
이 프로젝트의 규칙 파일(AGENTS.md 또는 .cursor/rules/nhplug.mdc)을 먼저 읽어줘.
거기 적힌 NH Open API 명세(https://www.nhplug.com/llms.txt)도 확인하고,
인증·계좌조회·시세조회를 각각 어떻게 하는지 요약해줘.
```

### 2-2. 테스트 스크립트 생성 (두 번째 프롬프트)

```
nhplug SDK(pip install nhplug)를 사용해서, 모의투자(moapi) 환경에서
아래를 수행하는 파이썬 스크립트 test_nh.py 를 만들어줘.

1) 계좌 목록 조회 후 출력 (acct_type 도 함께 — 01·02=운영, 03=모의투자)
2) 모의투자용 계좌(acct_type=03)를 골라서 잔고 조회
3) 삼성전자(005930) 현재가 조회 후 출력

조건:
- 인증·토큰은 nhplug 가 처리하므로 /oauth2/token 을 직접 호출하지 말 것
- from nhplug import call, NhplugError 를 사용하고 예외를 잡아 코드·메시지를 출력
- 앱키/시크릿은 .env 에서 읽는다(코드에 하드코딩 금지)
```

> ⚠️ AI 가 `requests` 로 토큰 발급 코드를 짜려 하면 **"nhplug 의 call() 을 쓰라"고 다시 지시**하세요. 직접 짠 인증 코드는 토큰 캐시가 없어 **재발급이 반복되고 보안 알림이 쌓입니다.**

### 2-3. 실행

Antigravity 내장 터미널에서 (가상환경 활성화 상태에서):

```powershell
# 1-2 에서 만든 가상환경 활성화 (새 터미널이면 매번)
.\.venv\Scripts\Activate.ps1
python test_nh.py
```

계좌 목록과 삼성전자 현재가가 출력되면 **사전 준비 완료**입니다.

이후 "이 위에 5일/20일 이동평균을 계산해 신호를 출력하는 코드를 붙여줘" 같은 식으로 확장하면 됩니다.

> ⚠️ **주문 로직을 붙일 때**: 반드시 모의투자(`moapi`)에서 먼저 검증하고, 주문 함수는 `dry_run=True` 를 기본으로 두세요. 규칙 파일의 안전수칙을 AI 가 함께 지킵니다. 실주문은 사람이 최종 확인합니다.

> 에러가 나면 터미널 메시지를 그대로 복사해 "이 오류 고쳐줘"라고 하면 됩니다. 자주 나는 오류는 아래 표 참고.

---

## 3. 자주 막히는 점

| 증상 | 해결 |
|---|---|
| 토큰 403 "유효하지 않은 AppSecret" | 키가 그 환경용인지 확인. base url 을 키에 맞는 환경으로 (모의/실거래·개발/운영) |
| 계좌번호 오류 | 계좌목록 응답은 `acct_no`, 잔고·주문 입력은 `act_no` — 값은 동일하니 그대로 사용 |
| 응답 파싱 실패 | 요청 `{"Input_0": {...}}` / 응답 `Output_0`(+`Output_1`) 봉투. **`Output_0` 은 객체일 수도 배열일 수도** 있으니 `openapi.json` 확인 |
| 조회는 됐는데 실패로 처리됨 | 성공코드는 **`00000`·`00166`·`00221`·`13578`** (+`rsp_msg`에 "완료"). `00000` 만 보면 매수가능수량 조회가 항상 실패합니다 |
| 계좌가 있는데 오류 | 계좌구분(`acct_type`) 확인 — `01`·`02`=운영(`api`), `03`=모의투자(`moapi`). 환경과 맞는 계좌를 쓰세요 |
| 주문 거부/형식오류 | `iem_cd` 는 6자리 그대로(예: 005930, `A` 없음), `orr_pr` 은 원 단위 정수 그대로(예: 70000). 형식은 describe_api/openapi.json 최신 예시 기준 |
| 토큰 매번 재발급 | 발급 토큰을 만료까지 캐시·재사용 |

---

## 부록 A. 규칙 파일 — `templates/` 참조

규칙 파일 전문은 저장소의 **[templates/](https://github.com/PLUG-OpenAPI/nhplug-sdk/tree/main/templates)** 에 있습니다. 이 가이드에 사본을 두지 않는 이유는, **두 곳에 두면 한쪽이 낡아 잘못된 규칙을 퍼뜨리기 때문**입니다(실제로 그런 일이 있었습니다).

| 파일 | 도구 | 위치 |
|---|---|---|
| [`AGENTS.md`](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/templates/AGENTS.md) | Antigravity · Codex | 프로젝트 루트 |
| [`CLAUDE.md`](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/templates/CLAUDE.md) | Claude Code | 프로젝트 루트 |
| [`cursor/nhplug.mdc`](https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/templates/cursor/nhplug.mdc) | Cursor | `.cursor/rules/` |

담긴 내용: SDK 우선 사용 · 명세 정본 위치 · **성공코드 4종**(`00000`·`00166`·`00221`·`13578`) · 계좌구분(`acct_type`) · 브랜드 3줄 전환 · 종목마스터 · 실시간 · 주문 필드 형식 · 안전수칙 · MCP 혼동 방지

## 부록 B. `.env` 템플릿

```
NHPLUG_APP_KEY=발급받은_APP_KEY
NHPLUG_APP_SECRET=발급받은_APP_SECRET
NHPLUG_BASE_URL=https://api.nhplug.com:8443
NHPLUG_AUTH_URL=https://api.nhplug.com:8443   # 토큰은 운영 전용(moapi 미제공)
# 브랜드: 나무=nhplug.com / N2=n2plug.com (API 동일, 도메인만 다름).
# N2 고객은 위 두 줄을 둘 다 n2plug 로 (예: api.n2plug.com:8443). AUTH_URL 도 필수!
```

---

*문의: apisupport@nhsec.com · 자동매매 예제는 학습·테스트 목적이며, 투자 손실 책임은 이용자에게 있습니다.*
