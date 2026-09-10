# Access Token 전역 캐시 — 재발급 알림톡 줄이기

**SDK 를 쓰지 않고 직접 개발하시는 분**을 위한 참고 구현입니다.

## 문제

Access Token 은 **재발급을 요청할 때마다 새로 발급**되고, 그때마다 **알림톡이 발송**됩니다.
가장 흔한 원인은 **토큰을 메모리에만 보관**하는 경우입니다.

| | 결과 |
|---|---|
| 메모리에만 저장 | 스크립트 실행마다 새 프로세스 → **실행할 때마다 재발급** |
| **파일에 저장** | 프로세스가 바뀌어도 재사용 → **하루 1회 발급** |

자주 발생하는 두 가지도 함께 확인하세요.

- **`429`(호출 한도 초과)에 토큰을 재발급** — 429 는 토큰 문제가 아닙니다. 재발급하면 알림톡만 쌓입니다.
- **매 호출마다 발급** — 토큰은 24시간 유효합니다.

## 사용

```bash
pip install requests
export NHPLUG_APP_KEY=발급받은_APP_KEY
export NHPLUG_APP_SECRET=발급받은_APP_SECRET

python nh_token.py
```

```python
from nh_token import api_post

accounts = api_post("/n2/acctinfo", {})["Output_0"]
price = api_post("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})
```

## 이 구현이 지키는 것

| | |
|---|---|
| 파일 캐시 | `~/.nhplug/token_cache.json` — 프로세스가 바뀌어도 재사용 |
| 만료 여유 | 만료 60초 전에 미리 재발급 (경계 오류 방지) |
| 재발급 조건 | **`401`(토큰 무효)일 때만.** `429` 에는 재발급하지 않음 |
| 동시 실행 | `os.replace` 원자적 교체로 캐시 파일 손상 방지 |
| 브랜드 전환 | 캐시에 발급 서버·계정을 기록해 **남의 토큰을 재사용하지 않음** |
| 성공 판정 | **하지 않습니다.** HTTP 200 이면 응답을 그대로 돌려주니 **`rsp_msg` 문장을 읽고 직접 판단**하세요. `rsp_cd` 는 API 마다 의미가 달라 코드값으로 판정할 수 없습니다 |
| 보안 | 캐시에 앱키 **앞 8자리만** 기록 · 토큰 값은 출력하지 않음 |

## 🟢 더 간단한 방법

위 내용이 모두 구현된 **공식 SDK** 를 쓰시면 직접 작성하지 않아도 됩니다.

```bash
pip install nhplug
```

```python
from nhplug import call
call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})
```

## 주의

- 캐시 파일에는 토큰이 담깁니다. **공유·커밋하지 마세요.**
- 토큰 발급은 **운영(`api`) 전용**입니다. 모의투자(`moapi`)로 호출하더라도 `NHPLUG_AUTH_URL` 은 `api` 로 둡니다.
- **N2 고객**은 `NHPLUG_BASE_URL` 과 `NHPLUG_AUTH_URL` 을 **둘 다** `n2plug.com` 으로 바꾸세요.

문의: apisupport@nhsec.com
