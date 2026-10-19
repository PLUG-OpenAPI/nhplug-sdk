# standalone — 단독 실행 예제

NH Open API 호출 흐름을 이해하기 위한 **가장 단순한 예제**입니다. 파일 하나로 실행됩니다.
토큰 발급 → 계좌 목록 → 잔고 → 실시간 시세 등록 → (수신 중) 현재가 조회 → 실시간 해제 순서로 호출합니다.

| | [`nhplug_stock_demo1.py`](nhplug_stock_demo1.py) | [`nhplug_stock_demo2.py`](nhplug_stock_demo2.py) |
|---|---|---|
| REST | `urllib` (표준 라이브러리) | `requests` |
| WebSocket | `websocket-client` | `websockets` (async) |
| 설치 | `pip install websocket-client` | `pip install requests websockets` |

## 실행

```bash
cp .env.example .env      # AppKey / SecretKey 입력
python nhplug_stock_demo1.py
```

- 앱키·앱시크릿 발급: 나무 [www.nhplug.com/intro](https://www.nhplug.com/intro) · N2 [www.n2plug.com/intro](https://www.n2plug.com/intro)
- 파일 상단 `ACCT_NO` 에 계좌번호를 넣으세요. 넣기 전이면 잔고 조회는 실패하지만, 먼저 출력되는 계좌 목록에서 골라 넣으면 됩니다.

## 알아 둘 것

- **토큰은 24시간 유효합니다.** 예제는 `.env` 에 저장해 재사용합니다. 매번 발급하면 보안 알림이 쌓입니다.
- **WebSocket 주소에 `/websocket` 경로가 필요합니다.** 호스트:포트만으로는 접속되지 않습니다.
- **실시간 수신 중에도 REST 호출이 됩니다.** 두 연결은 서로 독립입니다.
- 실시간 채널 목록과 서버 한도(동시 세션 수 · 세션당 등록 건수): [docs/realtime_channels.md](../../docs/realtime_channels.md)
- API 명세 정본: [llms.txt](https://www.nhplug.com/llms.txt) (N2: [n2plug.com/llms.txt](https://www.n2plug.com/llms.txt))
