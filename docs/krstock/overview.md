# NH투자증권 Open API — 국내주식 (Domestic Stock) Overview

NH투자증권 Open API 의 **국내주식 (Domestic Stock)** 자산군. 주문·조회·시세·실시간 제공. (기준: API명세서 260721 / 나무 환경)

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

전체 목록은 [README.md](https://www.nhplug.com/openapi-docs/krstock/README.md), 필드·스키마는 [openapi.json](https://www.nhplug.com/openapi-docs/krstock/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krstock/order/v1/cancel` | 주식주문(정정취소) 정정 |
| `POST /krstock/order/v1/cashBuy` | 주식주문(현금) 매수 |
| `POST /krstock/order/v1/cashSell` | 주식주문(현금) 매수 |
| `POST /krstock/order/v1/creditBuy` | 주식주문(신용) 매수 |
| `POST /krstock/order/v1/creditSell` | 주식주문(신용) 매수 |
| `POST /krstock/order/v1/modify` | 주식주문(정정취소) 정정 |
| `POST /krstock/order/v1/reservedCancel` | 주식예약주문취소 |
| `POST /krstock/order/v1/reservedOrder` | 주식예약주문 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krstock/TODO/API_국내_주식_조회_정정취소` | 주식정정취소가능주문조회 |
| `POST /krstock/inquiry/v1/assetStatus` | 투자계좌자산현황조회 |
| `POST /krstock/inquiry/v1/balance` | 주식잔고조회 |
| `POST /krstock/inquiry/v1/buyableQuantity` | 매수가능수량조회 |
| `POST /krstock/inquiry/v1/dailyOrderExecution` | 주식일별주문체결조회 |
| `POST /krstock/inquiry/v1/dailyPnl` | 실현손익일별합산조회 |
| `POST /krstock/inquiry/v1/integratedMargin` | 주식통합증거금 현황 |
| `POST /krstock/inquiry/v1/realizedPnl` | 주식잔고조회_실현손익 |
| `POST /krstock/inquiry/v1/reservedInquiry` | 주식예약주문조회 |
| `POST /krstock/inquiry/v1/rightsHeld` | 기간별계좌권리현황조회보유 |
| `POST /krstock/inquiry/v1/rightsScheduled` | 기간별계좌권리현황조회보유 |
| `POST /krstock/inquiry/v1/sellableQuantity` | 매도가능수량조회 |
| `POST /krstock/inquiry/v1/tradingPnl` | 종목별실현손익현황조회 |

### 시세 (Market Data)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krstock/quote/v1/afterHoursCurrent` | 국내주식 시간외현재가 |
| `POST /krstock/quote/v1/afterHoursExpected` | 주식현재가 시간외시간별예상 |
| `POST /krstock/quote/v1/currentAfterHoursDaily` | 주식현재가 시간외일자별주가 |
| `POST /krstock/quote/v1/currentAfterHoursExecution` | 주식현재가 시간외시간별체결 |
| `POST /krstock/quote/v1/currentDaily` | 주식현재가 일자별 |
| `POST /krstock/quote/v1/currentExecution` | 주식현재가 체결 |
| `POST /krstock/quote/v1/currentInvestor` | 주식현재가 투자자 |
| `POST /krstock/quote/v1/currentPrice` | 주식현재가 시세 |
| `POST /krstock/quote/v1/etfComponents` | ETF 구성종목시세 |
| `POST /krstock/quote/v1/etfCurrent` | ETF/ETN 현재가 |
| `POST /krstock/quote/v1/period` | 국내주식기간별시세(일/주/월/년) |

### 실시간 (Realtime · WebSocket)

| 채널 | tr_cd | tr_key |
|---|---|---|
| 국내주식 실시간호가KRX | `ob` | `code`(종목코드) |
| 국내주식 실시간체결가KRX | `oc` | `code`(종목코드) |
| 국내주식 실시간예상체결KRX | `oa` | `code`(종목코드) |
| 국내주식 실시간회원사KRX | `t1` | `code`(종목코드) |
| 국내주식 실시간프로그램매매KRX | `t8` | `code`(종목코드) |
| 국내주식 시간외 실시간호가KRX | `e5` | `ecn_code`(종목코드) |
| 국내주식 시간외 실시간체결가KRX | `e2` | `ecn_code`(종목코드) |
| 국내주식 시간외 실시간예상체결KRX | `e4` | `ecn_code`(종목코드) |
| 국내주식 실시간호가KRX | `mb` | `code`(종목코드) |
| 국내주식 실시간체결가KRX | `mc` | `code`(종목코드) |
| 국내주식 실시간예상체결KRX | `ma` | `code`(종목코드) |
| 국내주식 실시간회원사KRX | `mg` | `code`(종목코드) |
| 국내주식 실시간프로그램매매KRX | `mn` | `code`(종목코드) |
| 국내주식 실시간호가KRX | `nb` | `code`(종목코드) |
| 국내주식 실시간체결가KRX | `nc` | `code`(종목코드) |
| 국내주식 실시간예상체결KRX | `na` | `code`(종목코드) |
| 국내주식 실시간회원사KRX | `ng` | `code`(종목코드) |
| 국내주식 실시간프로그램매매KRX | `nn` | `code`(종목코드) |
| 국내주식 실시간체결통보 | `d2` | `userid`(사용자ID) |
| 국내주식 실시간주문내역통보 | `d3` | `userid`(사용자ID) |
| 채권지수 실시간 체결가 | `uB` | `jisuid`(지수ID) |

---

## 시작하기

1. 포탈에서 `appkey`·`appsecretkey` 발급
2. `POST /oauth2/token` 으로 토큰 발급 (공통)
3. `POST /n2/acctinfo` 로 계좌번호(act_no) 확보 후 각 API 호출

---

## 비고

- **국내주식 (Domestic Stock)**, API명세서 **260721** / **나무** 기준. 공통 에러표 미제공(결과는 `message` 봉투). 실시간 연결/구독 한도·재연결 규약만 미확정.
