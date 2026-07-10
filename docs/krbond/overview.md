# NH투자증권 Open API — 국내채권 (KR Bond) Overview

NH투자증권 Open API 의 **국내채권 (KR Bond)** 자산군은 주문, 계좌·자산 조회, 시세, 실시간 스트리밍을 제공합니다. (기준: API명세서 260703 / 나무 환경)

---

## 환경 및 접속 정보

API 포탈: `https://www.nhplug.com` (나무)

| 구분 | URL (나무) |
|---|---|
| REST | `https://api.nhplug.com:8443` |
| 모의투자 REST | `https://moapi.nhplug.com:8443` |
| WebSocket | `wss://api.nhplug.com:7070` |
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

전체 목록·operationId 는 [README.md](https://www.nhplug.com/openapi-docs/krbond/README.md), 필드·스키마는 [openapi.json](https://www.nhplug.com/openapi-docs/krbond/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krbond/order/v1/bondBuy` | 장내채권 매수주문 |
| `POST /krbond/order/v1/bondCancel` | 장내채권 취소주문 |
| `POST /krbond/order/v1/bondModify` | 장내채권 정정주문 |
| `POST /krbond/order/v1/bondSell` | 장내채권 매도주문 |
| `POST /krbond/order/v1/bondSubstituteSell` | 장내채권 대용매도주문 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krbond/TODO/op` | 장내채권 정정취소가능주문 조회 |
| `POST /krbond/inquiry/v1/bondBalance` | 장내채권 잔고조회 |
| `POST /krbond/inquiry/v1/bondModifiableOrder` | 장내채권 주문체결내역 조회 |
| `POST /krbond/inquiry/v1/bondOrderableQuantity` | 장내채권 주문가능수량 조회 |
| `POST /krbond/inquiry/v1/bondSubstituteBalance` | 장내채권 대용잔고조회 |

### 시세 (Market Data)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krbond/quote/v1/bondCurrent` | 장내채권 현재가 |
| `POST /krbond/quote/v1/bondDaily` | 장내채권 일자별시세 |
| `POST /krbond/quote/v1/bondDetail` | 장내채권 상세정보 조회 |
| `POST /krbond/quote/v1/bondFairValue` | 장내채권 민간평간단가조회 |
| `POST /krbond/quote/v1/bondIssuance` | 장내채권 발행현황 |
| `POST /krbond/quote/v1/bondTradingStatus` | 장내채권 매매현황 |
| `POST /krbond/quote/v1/fairValueYield` | 채권 시가평가 수익률(민평) |
| `POST /krbond/quote/v1/inflationBond` | 물가연동채권물가계수일괄조회 |
| `POST /krbond/quote/v1/rateSpreadDailyYield` | 채권 금리 스프레드 일별 수익률 |
| `POST /krbond/quote/v1/smallBondIssuance` | 소액채권발행현황 |
| `POST /krbond/quote/v1/smallBondQuoteTrading` | 소액채권호가매매현황 |
| `POST /krbond/quote/v1/smallBondReportedYield` | 소액채권신고수익률 |
| `POST /krbond/quote/v1/smallBondTimeCurrent` | 소액채권시간대별현재가 |
| `POST /krbond/quote/v1/yieldComparisonByType` | 채권 유형별 수익률 비교 |
| `POST /krbond/quote/v1/yieldTrend` | 채권 수익률 추이 |

### 실시간 (Realtime · WebSocket)

`wss://api.nhplug.com:7070` 에 접속해 아래 메시지로 구독/해제합니다. `tr_type` 1=등록 · 2=해제. 인증은 message header 의 `token`(access token)만 사용.

```json
{ "header": { "token": "{access_token}", "tr_type": "1" },
  "body":   { "tr_cd": "<채널코드>", "tr_key": "<구독키>" } }
```

채널 목록:

| 채널 | tr_cd | tr_key |
|---|---|---|
| 장내채권 실시간 호가소액 | `c1` | `expcode`(표준채권코드) |
| 장내채권 실시간 호가전환 | `c3` | `expcode`(표준채권코드) |
| 장내채권 실시간 체결가소액 | `c2` | `expcode`(표준채권코드) |
| 장내채권 실시간 체결가전환 | `c4` | `expcode`(표준채권코드) |
| 장내채권 실시간 체결내역 통보 | `de` | `userid`(사용자ID) |
| 장내채권 실시간 주문내역 통보 | `d3` | `userid`(사용자ID) |
| 채권지수 실시간 체결가 | `uB` | `jisuid`(지수ID) |

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

- 본 문서는 **국내채권 (KR Bond)** 자산군, API명세서 **260703** / **나무** 환경 기준입니다.
- 공통 에러 코드 표는 미제공, 처리 결과는 응답 `message` 봉투로 확인.
- 실시간 heartbeat·푸시 인코딩·통보 암호화 등 일부 규약은 미확정(TODO).
