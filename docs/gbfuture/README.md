# NH투자증권 Open API — 해외파생 (Global Derivatives) Endpoint Index

All REST URIs relative to `https://api.nhplug.com:8443` (운영 나무) · Method 는 모두 `POST` · 요청 `Input_0` / 응답 `Output_0`+`message`. (기준: 260703 / 나무)

> 정본은 [openapi.json](https://www.nhplug.com/openapi-docs/gbfuture/openapi.json) 입니다.


## 주문 (Order)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 해외선물옵션 주문 | POST | `/gbfuture/order/v1/buy` | gbfutureOrderBuy |
| 해외선물옵션 정정취소주문취소 | POST | `/gbfuture/order/v1/cancel` | gbfutureOrderCancel |
| 해외선물옵션 정정취소주문정정 | POST | `/gbfuture/order/v1/modify` | gbfutureOrderModify |

## 조회 (Inquiry)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 해외선물옵션 미체결내역조회(잔고) | POST | `/gbfuture/TODO/op` | gbfutureTODOOp |
| 해외선물옵션 예수금현황 | POST | `/gbfuture/inquiry/v1/deposit` | gbfutureInquiryDeposit |
| 해외선물옵션 증거금상세 | POST | `/gbfuture/inquiry/v1/margin` | gbfutureInquiryMargin |
| 해외선물옵션 주문가능조회 | POST | `/gbfuture/inquiry/v1/orderable` | gbfutureInquiryOrderable |
| 해외선물옵션 기간계좌손익 일별 | POST | `/gbfuture/inquiry/v1/pnl` | gbfutureInquiryPnl |
| 해외선물옵션 당일주문내역조회 | POST | `/gbfuture/inquiry/v1/todayOrderHistory` | gbfutureInquiryTodayOrderHistory |

## 시세 (Market Data)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 해외선물종목현재가 | POST | `/gbfuture/quote/v1/current` | gbfutureQuoteCurrent |
| 해외선물 체결추이(일간) | POST | `/gbfuture/quote/v1/executionTrendDaily` | gbfutureQuoteExecutionTrendDaily |
| 해외선물 체결추이(월간) | POST | `/gbfuture/quote/v1/executionTrendMonthly` | gbfutureQuoteExecutionTrendMonthly |
| 해외선물 체결추이(틱) | POST | `/gbfuture/quote/v1/executionTrendTick` | gbfutureQuoteExecutionTrendTick |
| 해외선물 체결추이(주간) | POST | `/gbfuture/quote/v1/executionTrendWeekly` | gbfutureQuoteExecutionTrendWeekly |
| 해외선물옵션 장운영시간 | POST | `/gbfuture/quote/v1/marketOperationInfo` | gbfutureQuoteMarketOperationInfo |
| 해외선물 분봉조회 | POST | `/gbfuture/quote/v1/minute` | gbfutureQuoteMinute |
| 해외선물 상품기본정보 | POST | `/gbfuture/quote/v1/productInfo` | gbfutureQuoteProductInfo |
| 해외선물 호가 | POST | `/gbfuture/quote/v1/quote` | gbfutureQuoteQuote |
| 해외선물종목상세 | POST | `/gbfuture/quote/v1/symbolDetail` | gbfutureQuoteSymbolDetail |

## 실시간 (Realtime, WebSocket)

운영 나무 Endpoint: `wss://api.nhplug.com:7080` · 구독 메시지·인증은 [openapi.json](https://www.nhplug.com/openapi-docs/gbfuture/openapi.json) 의 `x-realtime-channels.protocol` 참조.

| 채널 | tr_cd | tr_key | 응답 필드 수 |
|---|---|---|---|
| 해외선물옵션 실시간호가 | `FH` | `isym`(내부종목코드) | 39 |
| 해외선물옵션 지연호가 | `fh` | `isym`(내부종목코드) | 39 |
| 해외선물옵션 실시간체결가 | `FC` | `isym`(내부종목코드) | 15 |
| 해외선물옵션 지연체결가 | `fc` | `isym`(내부종목코드) | 15 |
| 해외선물옵션 실시간체결통보 | `dk` | `userid`(사용자ID) | 20 |
| 해외선물옵션 실시간주문내역통보 | `dj` | `userid`(사용자ID) | 25 |
