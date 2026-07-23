# NH투자증권 Open API — 국내채권 (KR Bond) Overview

NH투자증권 Open API 의 **국내채권 (KR Bond)** 자산군. 주문·조회·시세·실시간 제공. (기준: API명세서 260721 / 나무 환경)

---

## 환경 및 접속 정보

> ⚠️ 주소마다 용도가 다릅니다. **실주문은 실거래에서만 체결**. 개발·검증은 테스트/모의 먼저. 순서: 테스트/모의 → 검증 → 실거래.

API 포탈: `https://www.nhplug.com` (나무)

| 용도 | REST |
|---|---|
| 🟢 테스트 (실매매 전 검증) | `https://devapi.nhplug.com:8443` |
| 🟢 모의투자 (교육이수) | `https://moapi.nhplug.com:8443` |
| 🔴 실거래 (실제 주문) | `https://api.nhplug.com:8443` |

> WebSocket: 테스트 `wss://devapi.nhplug.com:7070` / 모의 `wss://moapi.nhplug.com:17070` / 실거래 `wss://api.nhplug.com:7070`.

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

전체 목록은 [README.md](https://www.nhplug.com/openapi-docs/krbond/README.md), 필드·스키마는 [openapi.json](https://www.nhplug.com/openapi-docs/krbond/openapi.json) 정본 참조.


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
| `POST /krbond/TODO/API_국내_채권_조회_정정취소가능주문` | 장내채권 정정취소가능주문 조회 |
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

| 채널 | tr_cd | tr_key |
|---|---|---|
| 장내채권 실시간 호가소액 | `c1` | `expcode`(종목코드) |
| 장내채권 실시간 호가소액 | `c3` | `expcode`(표준채권코드) |
| 장내채권 실시간 체결가소액 | `c2` | `expcode`(종목코드) |
| 장내채권 실시간 체결가소액 | `c4` | `expcode`(표준채권코드) |
| 장내채권 실시간 체결내역 통보 | `de` | `userid`(사용자ID) |
| 장내채권 실시간 주문내역 통보 | `d3` | `userid`(사용자ID) |

---

## 시작하기

1. 포탈에서 `appkey`·`appsecretkey` 발급
2. `POST /oauth2/token` 으로 토큰 발급 (공통)
3. `POST /n2/acctinfo` 로 계좌번호(act_no) 확보 후 각 API 호출

---

## 비고

- **국내채권 (KR Bond)**, API명세서 **260721** / **나무** 기준. 공통 에러표 미제공(결과는 `message` 봉투). 실시간 연결/구독 한도·재연결 규약만 미확정.
