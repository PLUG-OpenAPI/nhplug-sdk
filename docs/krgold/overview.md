# NH투자증권 Open API — 국내금현물 (KR Gold) Overview

NH투자증권 Open API 의 **국내금현물 (KR Gold)** 자산군은 주문, 계좌·자산 조회, 시세, 실시간 스트리밍을 제공합니다. (기준: API명세서 260703 최신 / 나무 환경)

---

## 환경 및 접속 정보

> ⚠️ 주소마다 용도가 다릅니다. **실주문은 실거래에서만 체결**됩니다. 개발·검증은 테스트/모의에서 먼저 하세요. 순서: 테스트/모의 → 검증 → 실거래.

API 포탈: `https://www.nhplug.com` (나무)

| 용도 | REST | WebSocket |
|---|---|---|
| 🟢 테스트 (실매매 전 검증) | `https://devapi.nhplug.com:8443` | `wss://devapi.nhplug.com:7070` |
| 🟢 모의투자 (교육이수) | `https://moapi.nhplug.com:8443` | `wss://moapi.nhplug.com:17070` |
| 🔴 실거래 (실제 주문) | `https://api.nhplug.com:8443` | `wss://api.nhplug.com:7070` |

> WS 포트: 국내 7070 · 해외 7080 · 모의 17070. N2 환경은 추후.

---

## 개요

### 인증

- REST: `Authorization: Bearer {access_token}` + `x-client-id` + `x-client-secret`
- WebSocket: 구독 메시지 `header.token` 에 access token (추가 헤더 없음)
- 토큰 발급: `POST /oauth2/token` (공통 API)

### 요청·응답 규약

REST 는 `POST` + `application/json`. 요청 `Input_0` / 응답 `Output_0`(배열) + `message` 봉투. 각 필드 설명(한글명·길이·코드값)은 openapi.json 의 description 참조.

---

## 기능 목록

전체 목록·operationId 는 [README.md](https://www.nhplug.com/openapi-docs/krgold/README.md), 필드·스키마·설명은 [openapi.json](https://www.nhplug.com/openapi-docs/krgold/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krgold/order/v1/goldBuy` | 금현물 매수주문 |
| `POST /krgold/order/v1/goldCancel` | 금현물 취소주문 |
| `POST /krgold/order/v1/goldModify` | 금현물 정정주문 |
| `POST /krgold/order/v1/goldSell` | 금현물 매도주문 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krgold/inquiry/v1/goldDepositAndBalance` | 금현물 예수금및잔고 |
| `POST /krgold/inquiry/v1/goldExecution` | 금현물 주문체결조회 |
| `POST /krgold/inquiry/v1/goldOrderableQuantity` | 금현물 주문가능수량조회 |

### 시세 (Market Data)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krgold/TODO/API_국내_금현물_시세_괴리율` | 금현물 괴리율 |
| `POST /krgold/quote/v1/goldCurrent` | 금현물 현재가 |
| `POST /krgold/quote/v1/goldDailyInvestorTrade` | 금현물 일별투자매매현황 |
| `POST /krgold/quote/v1/goldDailyTrend` | 금현물 일별추이 |
| `POST /krgold/quote/v1/goldVolatilityTrade` | 금현물 변동거래 |

### 실시간 (Realtime · WebSocket)

`wss://api.nhplug.com:7070` 에 접속해 아래 메시지로 구독/해제합니다. `tr_type` 1=등록 · 2=해제. 인증은 message header 의 `token`(access token)만 사용.

```json
{ "header": { "token": "{access_token}", "tr_type": "1" },
  "body":   { "tr_cd": "<채널코드>", "tr_key": "<구독키>" } }
```

채널 목록:

| 채널 | tr_cd | tr_key |
|---|---|---|
| 금현물 실시간 호가 | `g5` | `shcode`(종목코드) |
| 금현물 실시간 체결가 | `g4` | `shcode`(종목코드) |
| 금현물 실시간 예상체결가 | `gE` | `shcode`(종목코드) |
| 금현물 실시간 체결내역 통보 | `de` | `userid`(사용자ID) |
| 금현물 실시간 주문내역 통보 | `d3` | `userid`(사용자ID) |

---

## 시작하기

1. 포탈(`https://www.nhplug.com`)에서 `appkey`·`appsecretkey` 발급
2. `POST /oauth2/token` 으로 access token 발급 (공통 API)
3. `POST /n2/acctinfo` 로 계좌번호(act_no) 확보 후 각 API 호출

---

## 비고

- 본 문서는 **국내금현물 (KR Gold)** 자산군, API명세서 **260703 최신** / **나무** 환경 기준입니다.
- 공통 에러 코드 표는 미제공, 처리 결과는 응답 `message` 봉투로 확인.
- 실시간 heartbeat·푸시 인코딩·통보 암호화 등 일부 규약은 미확정(TODO).
