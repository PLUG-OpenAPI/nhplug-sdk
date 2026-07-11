# NH투자증권 Open API — 국내금현물 (KR Gold) Endpoint Index

All REST URIs relative to `https://api.nhplug.com:8443` (운영 나무) · Method 는 모두 `POST` · 요청 `Input_0` / 응답 `Output_0`+`message`. (기준: 260703 최신 / 나무)

> 정본은 [openapi.json](https://www.nhplug.com/openapi-docs/krgold/openapi.json) 입니다.


## 주문 (Order)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 금현물 매수주문 | POST | `/krgold/order/v1/goldBuy` | krgoldOrderGoldBuy |
| 금현물 취소주문 | POST | `/krgold/order/v1/goldCancel` | krgoldOrderGoldCancel |
| 금현물 정정주문 | POST | `/krgold/order/v1/goldModify` | krgoldOrderGoldModify |
| 금현물 매도주문 | POST | `/krgold/order/v1/goldSell` | krgoldOrderGoldSell |

## 조회 (Inquiry)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 금현물 예수금및잔고 | POST | `/krgold/inquiry/v1/goldDepositAndBalance` | krgoldInquiryGoldDepositAndBalance |
| 금현물 주문체결조회 | POST | `/krgold/inquiry/v1/goldExecution` | krgoldInquiryGoldExecution |
| 금현물 주문가능수량조회 | POST | `/krgold/inquiry/v1/goldOrderableQuantity` | krgoldInquiryGoldOrderableQuantity |

## 시세 (Market Data)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 금현물 괴리율 | POST | `/krgold/TODO/API_국내_금현물_시세_괴리율` | krgoldTODOAPI_국내_금현물_시세_괴리율 |
| 금현물 현재가 | POST | `/krgold/quote/v1/goldCurrent` | krgoldQuoteGoldCurrent |
| 금현물 일별투자매매현황 | POST | `/krgold/quote/v1/goldDailyInvestorTrade` | krgoldQuoteGoldDailyInvestorTrade |
| 금현물 일별추이 | POST | `/krgold/quote/v1/goldDailyTrend` | krgoldQuoteGoldDailyTrend |
| 금현물 변동거래 | POST | `/krgold/quote/v1/goldVolatilityTrade` | krgoldQuoteGoldVolatilityTrade |

## 실시간 (Realtime, WebSocket)

운영 나무 Endpoint: `wss://api.nhplug.com:7070` · 구독 메시지·인증은 [openapi.json](https://www.nhplug.com/openapi-docs/krgold/openapi.json) 의 `x-realtime-channels.protocol` 참조.

| 채널 | tr_cd | tr_key | 응답 필드 수 |
|---|---|---|---|
| 금현물 실시간 호가 | `g5` | `shcode`(종목코드) | 65 |
| 금현물 실시간 체결가 | `g4` | `shcode`(종목코드) | 13 |
| 금현물 실시간 예상체결가 | `gE` | `shcode`(종목코드) | 8 |
| 금현물 실시간 체결내역 통보 | `de` | `userid`(사용자ID) | 12 |
| 금현물 실시간 주문내역 통보 | `d3` | `userid`(사용자ID) | 24 |
