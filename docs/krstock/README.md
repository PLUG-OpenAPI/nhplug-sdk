# NH투자증권 Open API — 국내주식 (Domestic Stock) Endpoint Index

All REST URIs relative to 테스트 `https://devapi.nhplug.com:8443` · Method 모두 `POST` · 요청 `Input_0` / 응답 `Output_0`+`message`. (기준: 260721 / 나무)

> 정본은 [openapi.json](https://www.nhplug.com/openapi-docs/krstock/openapi.json). ⚠️ 실주문은 실거래(api...) 에서만 체결 — 개발은 테스트/모의 우선.


## 주문 (Order)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 주식주문(정정취소) 정정 | POST | `/krstock/order/v1/cancel` | krstockOrderCancel |
| 주식주문(현금) 매수 | POST | `/krstock/order/v1/cashBuy` | krstockOrderCashBuy |
| 주식주문(현금) 매수 | POST | `/krstock/order/v1/cashSell` | krstockOrderCashSell |
| 주식주문(신용) 매수 | POST | `/krstock/order/v1/creditBuy` | krstockOrderCreditBuy |
| 주식주문(신용) 매수 | POST | `/krstock/order/v1/creditSell` | krstockOrderCreditSell |
| 주식주문(정정취소) 정정 | POST | `/krstock/order/v1/modify` | krstockOrderModify |
| 주식예약주문취소 | POST | `/krstock/order/v1/reservedCancel` | krstockOrderReservedCancel |
| 주식예약주문 | POST | `/krstock/order/v1/reservedOrder` | krstockOrderReservedOrder |

## 조회 (Inquiry)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 주식정정취소가능주문조회 | POST | `/krstock/TODO/API_국내_주식_조회_정정취소` | krstockTODOAPI_국내_주식_조회_정정취소 |
| 투자계좌자산현황조회 | POST | `/krstock/inquiry/v1/assetStatus` | krstockInquiryAssetStatus |
| 주식잔고조회 | POST | `/krstock/inquiry/v1/balance` | krstockInquiryBalance |
| 매수가능수량조회 | POST | `/krstock/inquiry/v1/buyableQuantity` | krstockInquiryBuyableQuantity |
| 주식일별주문체결조회 | POST | `/krstock/inquiry/v1/dailyOrderExecution` | krstockInquiryDailyOrderExecution |
| 실현손익일별합산조회 | POST | `/krstock/inquiry/v1/dailyPnl` | krstockInquiryDailyPnl |
| 주식통합증거금 현황 | POST | `/krstock/inquiry/v1/integratedMargin` | krstockInquiryIntegratedMargin |
| 주식잔고조회_실현손익 | POST | `/krstock/inquiry/v1/realizedPnl` | krstockInquiryRealizedPnl |
| 주식예약주문조회 | POST | `/krstock/inquiry/v1/reservedInquiry` | krstockInquiryReservedInquiry |
| 기간별계좌권리현황조회보유 | POST | `/krstock/inquiry/v1/rightsHeld` | krstockInquiryRightsHeld |
| 기간별계좌권리현황조회보유 | POST | `/krstock/inquiry/v1/rightsScheduled` | krstockInquiryRightsScheduled |
| 매도가능수량조회 | POST | `/krstock/inquiry/v1/sellableQuantity` | krstockInquirySellableQuantity |
| 종목별실현손익현황조회 | POST | `/krstock/inquiry/v1/tradingPnl` | krstockInquiryTradingPnl |

## 시세 (Market Data)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 국내주식 시간외현재가 | POST | `/krstock/quote/v1/afterHoursCurrent` | krstockQuoteAfterHoursCurrent |
| 주식현재가 시간외시간별예상 | POST | `/krstock/quote/v1/afterHoursExpected` | krstockQuoteAfterHoursExpected |
| 주식현재가 시간외일자별주가 | POST | `/krstock/quote/v1/currentAfterHoursDaily` | krstockQuoteCurrentAfterHoursDaily |
| 주식현재가 시간외시간별체결 | POST | `/krstock/quote/v1/currentAfterHoursExecution` | krstockQuoteCurrentAfterHoursExecution |
| 주식현재가 일자별 | POST | `/krstock/quote/v1/currentDaily` | krstockQuoteCurrentDaily |
| 주식현재가 체결 | POST | `/krstock/quote/v1/currentExecution` | krstockQuoteCurrentExecution |
| 주식현재가 투자자 | POST | `/krstock/quote/v1/currentInvestor` | krstockQuoteCurrentInvestor |
| 주식현재가 시세 | POST | `/krstock/quote/v1/currentPrice` | krstockQuoteCurrentPrice |
| ETF 구성종목시세 | POST | `/krstock/quote/v1/etfComponents` | krstockQuoteEtfComponents |
| ETF/ETN 현재가 | POST | `/krstock/quote/v1/etfCurrent` | krstockQuoteEtfCurrent |
| 국내주식기간별시세(일/주/월/년) | POST | `/krstock/quote/v1/period` | krstockQuotePeriod |

## 실시간 (Realtime, WebSocket)

테스트 Endpoint: `wss://devapi.nhplug.com:7070` · 구독·인증·푸시 규약은 [openapi.json](https://www.nhplug.com/openapi-docs/krstock/openapi.json) 의 `x-realtime-channels.protocol` 참조.

| 채널 | tr_cd | tr_key | 응답 필드 수 |
|---|---|---|---|
| 국내주식 실시간호가KRX | `ob` | `code`(종목코드) | 49 |
| 국내주식 실시간체결가KRX | `oc` | `code`(종목코드) | 24 |
| 국내주식 실시간예상체결KRX | `oa` | `code`(종목코드) | 16 |
| 국내주식 실시간회원사KRX | `t1` | `code`(종목코드) | 72 |
| 국내주식 실시간프로그램매매KRX | `t8` | `code`(종목코드) | 30 |
| 국내주식 시간외 실시간호가KRX | `e5` | `ecn_code`(종목코드) | 49 |
| 국내주식 시간외 실시간체결가KRX | `e2` | `ecn_code`(종목코드) | 17 |
| 국내주식 시간외 실시간예상체결KRX | `e4` | `ecn_code`(종목코드) | 12 |
| 국내주식 실시간호가KRX | `mb` | `code`(종목코드) | 52 |
| 국내주식 실시간체결가KRX | `mc` | `code`(종목코드) | 24 |
| 국내주식 실시간예상체결KRX | `ma` | `code`(종목코드) | 19 |
| 국내주식 실시간회원사KRX | `mg` | `code`(종목코드) | 72 |
| 국내주식 실시간프로그램매매KRX | `mn` | `code`(종목코드) | 30 |
| 국내주식 실시간호가KRX | `nb` | `code`(종목코드) | 49 |
| 국내주식 실시간체결가KRX | `nc` | `code`(종목코드) | 24 |
| 국내주식 실시간예상체결KRX | `na` | `code`(종목코드) | 16 |
| 국내주식 실시간회원사KRX | `ng` | `code`(종목코드) | 72 |
| 국내주식 실시간프로그램매매KRX | `nn` | `code`(종목코드) | 30 |
| 국내주식 실시간체결통보 | `d2` | `userid`(사용자ID) | 21 |
| 국내주식 실시간주문내역통보 | `d3` | `userid`(사용자ID) | 24 |
| 채권지수 실시간 체결가 | `uB` | `jisuid`(지수ID) | 36 |
