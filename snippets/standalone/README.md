# standalone — SDK 없이 쓰는 원시 예제

**`pip install nhplug` 없이** 표준 라이브러리와 널리 쓰이는 패키지만으로 NH Open API 를 호출하는 예제입니다.
토큰 발급부터 계좌·잔고·현재가 조회, 실시간 시세 구독까지 **한 파일에 처음부터 끝까지** 들어 있습니다.

> 대부분의 경우 **[`nhplug` SDK](https://pypi.org/project/nhplug/) 를 쓰는 편이 훨씬 짧고 안전합니다.**
> ```bash
> pip install nhplug
> ```
> 아래 예제는 SDK 를 쓸 수 없거나, 내부 동작을 직접 확인하고 싶을 때를 위한 것입니다.

## 언제 이걸 쓰나

- 사내 정책상 **외부 패키지 설치가 제한**된 환경
- **다른 언어로 포팅**하려는 경우 — 원시 HTTP·WebSocket 흐름이 그대로 보입니다 (Java·C#·Node…)
- SDK 가 내부에서 무엇을 하는지 확인하고 싶을 때

## 두 가지 버전

같은 일을 **다른 라이브러리**로 구현했습니다. 환경에 맞는 쪽을 고르세요.

| | [`nhplug_stock_demo1.py`](nhplug_stock_demo1.py) | [`nhplug_stock_demo2.py`](nhplug_stock_demo2.py) |
|---|---|---|
| REST | `urllib.request` (**표준 라이브러리**) | `requests` |
| WebSocket | `websocket-client` (콜백) | `websockets` (async/await) |
| 설치 | `websocket-client` `truststore` | `requests` `websockets` `truststore` |
| 특징 | 설치가 가장 적음 | 코드가 짧고 위에서 아래로 읽힘 |

```bash
pip install websocket-client truststore          # demo1
pip install requests websockets truststore       # demo2
```

## 실행

```bash
cp .env.example .env      # AppKey / SecretKey 입력
python nhplug_stock_demo1.py
```

앱키·앱시크릿은 포털에서 발급합니다 — 나무 [www.nhplug.com/intro](https://www.nhplug.com/intro) · N2 [www.n2plug.com/intro](https://www.n2plug.com/intro)

> ⚠️ 이 폴더의 `.env` 는 **INI 형식**(`[NHPLUG]` 섹션)으로, 저장소 루트의 `.env`(SDK용, `KEY=VALUE`)와 다릅니다.
> 각 예제가 **자기 폴더의 `.env`** 를 읽으므로 섞이지 않습니다.

`ACCT_NO` 는 파일 상단에 `"계좌번호입력"` 으로 비워 두었습니다. 실행하면 **3) 계좌 목록**이 출력되니 거기서 골라 넣으세요.

## 하는 일

```
1) .env 에서 AppKey/SecretKey 와 기존 토큰 읽기
2) 토큰이 유효하면 재사용, 아니면 POST /oauth2/token 으로 발급 후 .env 에 저장
3) POST /n2/acctinfo              계좌 목록
4) POST /krstock/inquiry/v1/balance  계좌 잔고
5) POST /krstock/quote/v1/currentPrice  현재가 (005930)
6) WebSocket 실시간 시세 구독 — mc(체결가 통합) · mb(호가 통합), 5초 수신 후 종료
```

## 예제가 이미 처리해 둔 함정

직접 짤 때 자주 틀리는 부분들입니다.

| 함정 | 예제의 처리 |
|---|---|
| **토큰 재발급** — 매 호출 재발급하면 보안 알림이 쌓입니다 | `.env` 에 만료시각을 저장해 **24시간 재사용** |
| **WebSocket 경로** — `/websocket` 이 빠지면 접속되지 않습니다 | `wss://api.nhplug.com:7070/websocket` |
| **TLS 검증 실패** — 서버가 중간 CA 를 보내지 않아 파이썬 기본 검증이 실패합니다 | `truststore` 로 **OS 인증서 저장소** 사용 (`CERT_NONE` 안 씀) |
| **연속조회 무한루프** — 같은 `cts` 를 다시 보내면 같은 페이지가 계속 옵니다 | `cts != previous_cts` 확인 후에만 다음 페이지 요청 |
| **사내 프록시** — 환경변수 때문에 `getaddrinfo failed` 가 납니다 | 프록시 환경변수를 무시하고 직접 연결 |
| **채널코드** — `oc` 는 KRX 전용이라 NXT 체결이 빠집니다 | **`mc`(통합)** 사용 |

## 직접 응용할 때 주의할 것

예제는 흐름을 보여주는 데 집중해서, 아래는 **일부러 넣지 않았습니다.** 실제 코드에는 필요합니다.

- **`rsp_cd`·`rsp_msg` 확인** — HTTP 200 이어도 업무 오류일 수 있습니다. 응답 내용을 보고 성공 여부를 판단하세요. 자세한 규약은 [llms.txt](https://www.nhplug.com/llms.txt) 참고.
- **호출 간격** — 짧은 시간에 많이 호출하면 `429`(호출 유량 초과)가 납니다. 자세한 한도는 [llms.txt](https://www.nhplug.com/llms.txt) 참고.
- **첫 WebSocket 메시지는 시세가 아닙니다** — 구독 등록 응답(ACK)이 먼저 옵니다.
  ```json
  {"header": {"tr_type":"1", "tr_cd":"mc", "rsp_cd":"00000", "rsp_msg":"정상처리되었습니다"},
   "body":   {"tr_key": ["005930"]}}
  ```
  데이터 푸시의 `header` 에는 `tr_type`·`rsp_cd` 가 없습니다. 이걸로 구분하세요.
- **실시간 등록은 세션당 10건** 까지입니다. 넘기면 서버가 **오류 메시지 없이** 연결을 끊습니다(close 1000 `"Bye"`).
  동시 세션은 앱키당 2개입니다.

**SDK(`pip install nhplug`)는 위 네 가지를 모두 자동으로 처리합니다.**

## 더 보기

- [실시간 채널 전체 목록](../../docs/realtime_channels.md) — 국내 21 · 해외 6 채널과 `tr_key` 대응표
- [SDK 로 같은 일 하기](../../README.md) — 위 6단계가 10줄 안쪽으로 줄어듭니다
- [명세 정본 llms.txt](https://www.nhplug.com/llms.txt) (N2: [n2plug.com/llms.txt](https://www.n2plug.com/llms.txt))
