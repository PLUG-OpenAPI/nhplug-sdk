# nhplug-sdk

NH투자증권 **NHPLUG** REST Open API 를 파이썬으로 쉽게 쓰기 위한 **샘플코드 · 전략 파이프라인 · 문서** 모음입니다. Python 개발자와 AI 코딩 도구(Antigravity·Cursor·Claude) 모두를 위한 개발자 키트입니다.

> 대화형으로 API 를 쓰고 싶다면 로컬 MCP [`plug-support/nhplug-mcp`](https://github.com/plug-support/nhplug-mcp) 를, 코드로 개발하려면 이 저장소를 사용하세요.

## 구성

```
nhplug/            # 공용 클라이언트 (인증·토큰캐시·Input_0 봉투 자동 처리)
snippets/      # ① 함수 단위 실행 샘플 (기능당 폴더 = 호출 파일 + chk_ 검증 파일)
│   ├── auth/issue_token
│   ├── common/list_accounts
│   └── krstock/{current_price, balance, order_cash_buy}
examples/     # ② 카테고리 통합 예제 (krstock_functions.py + _examples.py)
pipeline/          # ③ 설계→검증→실행 파이프라인 (골격)
docs/              # API 명세(llms.txt/openapi) 배치 + 에러코드/레이트리밋
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

## 환경변수

| 변수 | 설명 |
|---|---|
| `NHPLUG_APP_KEY` / `NHPLUG_APP_SECRET` | 발급받은 앱키/시크릿 (`APP_KEY`/`APP_SECRET` 도 허용) |
| `NHPLUG_BASE_URL` | 접속 환경. 기본 `https://devmoapi.nhplug.com:8443`(개발 모의투자) |
| `NHPLUG_DEFAULT_ACCOUNT` | 잔고 샘플 등에서 사용할 기본 계좌번호 |

## ⚠️ 안전

- 기본 환경은 **모의투자**. 운영 실거래(`api.nhplug.com`)는 명시적으로 전환할 때만.
- 주문 샘플은 기본 **드라이런**입니다. 실주문은 `dry_run=False`로, 반드시 모의투자에서 검증 후.
- 앱키/시크릿은 코드에 넣지 말고 `.env`로 관리(`.gitignore` 처리됨).

## 라이선스 · 문의

MIT · apisupport@nhsec.com
