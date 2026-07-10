# NH투자증권 Open API — 해외파생 (Global Derivatives) Overview

NH투자증권 Open API 의 **해외파생 (Global Derivatives)** 자산군은 주문, 계좌·자산 조회, 시세, 실시간 스트리밍을 제공합니다. (기준: API명세서 260703 / 나무 환경)

---

## 환경 및 접속 정보

API 포탈: `https://www.nhplug.com` (나무)

| 구분 | URL (나무) |
|---|---|
| REST | `https://api.nhplug.com:8443` |
| 모의투자 REST | `https://moapi.nhplug.com:8443` |
| WebSocket | `wss://api.nhplug.com:7080` |
| 모의투자 WebSocket | `wss://moapi.nhplug.com:17070` |

> WS 포트: 국내 7070 · 해외 7080 · 모의 17070. N2 환경은 추후.

---

## 개요

### 인증

- REST: `Authorization: Bearer {access_token}` + `x-client-id` + `x-client-secret`
- WebSocket: 구독 메시지 `header.token` 에 access token (추가 헤더 없음)
- 토큰 발급: `POST /oauth2/token` (공통 API)

### 요청·응답 규약

REST 는 `POST` + `application/json`. 요청 `Input_0` / 응답 `Output_0`(배열) + `message` 봉투. 모든 필드에 한글명·영문명 병기.

---

## 기능 목록

전체 목록·operationId 는 [README.md](https://www.nhplug.com/openapi-docs/gbfuture/README.md), 필드·스키마는 [openapi.json](https://www.nhplug.com/openapi-docs/gbfuture/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /gbfuture/order/v1/buy` | 해외선물옵션 주문 |
| `POST /gbfuture/order/v1/cancel` | 해외선물옵션 정정취소주문취소 |
| `POST /gbfuture/order/v1/modify` | 해외선물옵션 정정취소주문정정 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /gbfuture/TODO/op` | 해외선물옵션 미체결내역조회(잔고) |
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

`wss://api.nhplug.com:7080` 에 접속해 아래 메시지로 구독/해제합니다. `tr_type` 1=등록 · 2=해제. 인증은 message header 의 `token`(access token)만 사용.

```json
{ "header": { "token": "{access_token}", "tr_type": "1" },
  "body":   { "tr_cd": "<채널코드>", "tr_key": "<구독키>" } }
```

채널 목록:

| 채널 | tr_cd | tr_key |
|---|---|---|
| 해외선물옵션 실시간호가 | `FH` | `isym`(내부종목코드) |
| 해외선물옵션 지연호가 | `fh` | `isym`(내부종목코드) |
| 해외선물옵션 실시간체결가 | `FC` | `isym`(내부종목코드) |
| 해외선물옵션 지연체결가 | `fc` | `isym`(내부종목코드) |
| 해외선물옵션 실시간체결통보 | `dk` | `userid`(사용자ID) |
| 해외선물옵션 실시간주문내역통보 | `dj` | `userid`(사용자ID) |

---

## 시작하기

1. 포탈(`https://www.nhplug.com`)에서 `appkey`·`appsecretkey` 발급
2. `POST /oauth2/token` 으로 access token 발급 (공통 API)
3. `POST /n2/acctinfo` 로 계좌번호(act_no) 확보 후 각 API 호출

---

## 페이지네이션 (연속조회)

목록성 조회 API 는 요청 헤더 `cts` 로 연속조회를 제어합니다. 첫 조회는 비우고, 응답 연속키를 다음 요청 `cts` 헤더에 세팅.

---

## 비고

- 본 문서는 **해외파생 (Global Derivatives)** 자산군, API명세서 **260703** / **나무** 환경 기준입니다.
- 공통 에러 코드 표는 미제공, 처리 결과는 응답 `message` 봉투로 확인.
- 실시간 heartbeat·푸시 인코딩·통보 암호화 등 일부 규약은 미확정(TODO).
