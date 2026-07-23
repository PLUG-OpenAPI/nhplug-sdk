# NH투자증권 Open API — 해외파생 (Global Derivatives) Overview

NH투자증권 Open API 의 **해외파생 (Global Derivatives)** 자산군. 주문·조회·시세·실시간 제공. (기준: API명세서 260721 / 나무 환경)

---

## 환경 및 접속 정보

> ⚠️ 주소마다 용도가 다릅니다. **실주문은 실거래에서만 체결**. 개발·검증은 테스트/모의 먼저. 순서: 테스트/모의 → 검증 → 실거래.

API 포탈: `https://www.nhplug.com` (나무)

| 용도 | REST |
|---|---|
| 🟢 테스트 (실매매 전 검증) | `https://devapi.nhplug.com:8443` |
| 🟢 모의투자 (교육이수) | `https://moapi.nhplug.com:8443` |
| 🔴 실거래 (실제 주문) | `https://api.nhplug.com:8443` |

> WebSocket: 테스트 `wss://devapi.nhplug.com:7080` / 모의 `wss://moapi.nhplug.com:17070` / 실거래 `wss://api.nhplug.com:7080`.

---

## 개요

### 인증

- REST: `Authorization: Bearer {access_token}` + `x-client-id` + `x-client-secret`
- WebSocket: 구독 메시지 `header.token` 에 access token
- 토큰 발급: `POST /oauth2/token` (공통 API)

### 요청·응답 규약

REST 는 `POST` + `application/json`. 요청 `Input_0` / 응답 `Output_0`(배열) + `message`. 필드 설명(한글명·길이·코드값)은 openapi.json 참조.

### 실시간(WebSocket)

구독 메시지 전송 후 서버가 **JSON** `{header,body}` 를 **비정기적으로** push. heartbeat 불필요, 암호화 없음. 채널별 실제 예시는 openapi.json 의 push_example.

---

## 기능 목록

전체 목록은 [README.md](https://www.nhplug.com/openapi-docs/gbfuture/README.md), 필드·스키마는 [openapi.json](https://www.nhplug.com/openapi-docs/gbfuture/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /gbfuture/order/v1/buy` | 해외선물옵션 주문 |
| `POST /gbfuture/order/v1/cancel` | 해외선물옵션 정정취소주문정정 |
| `POST /gbfuture/order/v1/modify` | 해외선물옵션 정정취소주문정정 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /gbfuture/TODO/API_해외_파생_조회_미체결내역` | 해외선물옵션 미체결내역조회(잔고) |
| `POST /gbfuture/inquiry/v1/deposit` | 해외선물옵션 예수금현황 |
| `POST /gbfuture/inquiry/v1/margin` | 해외선물옵션 증거금상세 |
| `POST /gbfuture/inquiry/v1/orderable` | 해외선물옵션 주문가능조회 |
| `POST /gbfuture/inquiry/v1/pnl` | 해외선물옵션 기간계좌손익 일별 |
| `POST /gbfuture/inquiry/v1/todayOrderHistory` | 해외선물옵션 당일주문내역조회 |

### 시세 (Market Data)

| 엔드포인트 | 설명 |
|------|------|
| `POST /gbfuture/quote/v1/current` | 해외선물종목현재가 |
| `POST /gbfuture/quote/v1/executionTrendDaily` | 해외선물 체결추이(일간) |
| `POST /gbfuture/quote/v1/executionTrendMonthly` | 해외선물 체결추이(월간) |
| `POST /gbfuture/quote/v1/executionTrendTick` | 해외선물 체결추이(틱) |
| `POST /gbfuture/quote/v1/executionTrendWeekly` | 해외선물 체결추이(주간) |
| `POST /gbfuture/quote/v1/marketOperationInfo` | 해외선물옵션 장운영시간 |
| `POST /gbfuture/quote/v1/minute` | 해외선물 분봉조회 |
| `POST /gbfuture/quote/v1/productInfo` | 해외선물 상품기본정보 |
| `POST /gbfuture/quote/v1/quote` | 해외선물 호가 |
| `POST /gbfuture/quote/v1/symbolDetail` | 해외선물종목상세 |

### 실시간 (Realtime · WebSocket)

| 채널 | tr_cd | tr_key |
|---|---|---|
| 해외선물옵션 실시간호가 | `FH` | `isym`(종목코드) |
| 해외선물옵션 지연호가 | `fh` | `isym`(종목코드) |
| 해외선물옵션 실시간체결가 | `FC` | `isym`(종목코드) |
| 해외선물옵션 지연체결가 | `fc` | `isym`(종목코드) |
| 해외선물옵션 실시간체결통보 | `dk` | `userid`(사용자ID) |
| 해외선물옵션 실시간주문내역통보 | `dj` | `userid`(사용자ID) |

---

## 시작하기

1. 포탈에서 `appkey`·`appsecretkey` 발급
2. `POST /oauth2/token` 으로 토큰 발급 (공통)
3. `POST /n2/acctinfo` 로 계좌번호(act_no) 확보 후 각 API 호출

---

## 비고

- **해외파생 (Global Derivatives)**, API명세서 **260721** / **나무** 기준. 공통 에러표 미제공(결과는 `message` 봉투). 실시간 연결/구독 한도·재연결 규약만 미확정.
