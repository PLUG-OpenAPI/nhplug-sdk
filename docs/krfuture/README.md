# NH투자증권 Open API — 국내파생 (KR Derivatives) Endpoint Index

All REST URIs relative to 테스트 `https://devapi.nhplug.com:8443` · Method 모두 `POST` · 요청 `Input_0` / 응답 `Output_0`+`message`. (기준: 260721 / 나무)

> 정본은 [openapi.json](https://www.nhplug.com/openapi-docs/krfuture/openapi.json). ⚠️ 실주문은 실거래(api...) 에서만 체결 — 개발은 테스트/모의 우선.


## 주문 (Order)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 선물옵션 주문주간 | POST | `/krfuture/order/v1/day` | krfutureOrderDay |
| 선물옵션 정정취소주문주간정정 | POST | `/krfuture/order/v1/dayCancel` | krfutureOrderDayCancel |
| 선물옵션 정정취소주문주간정정 | POST | `/krfuture/order/v1/dayModify` | krfutureOrderDayModify |
| 선물옵션 주문주간 | POST | `/krfuture/order/v1/night` | krfutureOrderNight |
| 선물옵션 정정취소주문주간정정 | POST | `/krfuture/order/v1/nightCancel` | krfutureOrderNightCancel |
| 선물옵션 정정취소주문주간정정 | POST | `/krfuture/order/v1/nightModify` | krfutureOrderNightModify |

## 조회 (Inquiry)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 선물옵션 잔고현황 | POST | `/krfuture/inquiry/v1/balance` | krfutureInquiryBalance |
| 선물옵션기간약정수수료일별 | POST | `/krfuture/inquiry/v1/commission` | krfutureInquiryCommission |
| 선물옵션 잔고평가손익내역 | POST | `/krfuture/inquiry/v1/evalPnl` | krfutureInquiryEvalPnl |
| 선물옵션 기준일체결내역 | POST | `/krfuture/inquiry/v1/executionHistory` | krfutureInquiryExecutionHistory |
| 선물옵션 증거금 상세 | POST | `/krfuture/inquiry/v1/margin` | krfutureInquiryMargin |
| (야간)선물옵션 잔고현황 | POST | `/krfuture/inquiry/v1/nightBalance` | krfutureInquiryNightBalance |
| (야간)선물옵션 증거금 상세 | POST | `/krfuture/inquiry/v1/nightMargin` | krfutureInquiryNightMargin |
| (야간)선물옵션 주문체결 내역조회 | POST | `/krfuture/inquiry/v1/nightOrderExecutionHistory` | krfutureInquiryNightOrderExecutionHistory |
| (야간)선물옵션 주문가능 조회 | POST | `/krfuture/inquiry/v1/nightOrderable` | krfutureInquiryNightOrderable |
| 선물옵션 주문체결내역조회 | POST | `/krfuture/inquiry/v1/orderExecutionHistory` | krfutureInquiryOrderExecutionHistory |
| 선물옵션 주문가능 | POST | `/krfuture/inquiry/v1/orderable` | krfutureInquiryOrderable |

## 시세 (Market Data)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 선물옵션 일자별 | POST | `/krfuture/quote/v1/daily` | krfutureQuoteDaily |
| 선물옵션 시세주간 | POST | `/krfuture/quote/v1/day` | krfutureQuoteDay |
| 선물옵션기간별시세(일/주/월/년)주간 | POST | `/krfuture/quote/v1/dayPeriod` | krfutureQuoteDayPeriod |
| 선물옵션 변동거래량 | POST | `/krfuture/quote/v1/intradayExpectedTrend` | krfutureQuoteIntradayExpectedTrend |
| 선물옵션 시세주간 | POST | `/krfuture/quote/v1/night` | krfutureQuoteNight |
| 선물옵션기간별시세(일/주/월/년)주간 | POST | `/krfuture/quote/v1/nightPeriod` | krfutureQuoteNightPeriod |
| 선물옵션 프로그램매매 | POST | `/krfuture/quote/v1/timeProgramTrading` | krfutureQuoteTimeProgramTrading |
| 선물옵션 시간대별 투자자 매매현황 | POST | `/krfuture/quote/v1/tradingStatus` | krfutureQuoteTradingStatus |

## 실시간 (Realtime, WebSocket)

테스트 Endpoint: `wss://devapi.nhplug.com:7070` · 구독·인증·푸시 규약은 [openapi.json](https://www.nhplug.com/openapi-docs/krfuture/openapi.json) 의 `x-realtime-channels.protocol` 참조.

| 채널 | tr_cd | tr_key | 응답 필드 수 |
|---|---|---|---|
| 지수선물 실시간호가KP200 | `f1` | `fuitem`(종목코드) | 36 |
| 지수선물 실시간호가KP200 | `fH` | `fuitem`(종목코드) | 36 |
| 지수선물 실시간호가KP200 | `hH` | `fuitem`(종목코드) | 36 |
| 지수선물 실시간체결가KP200 | `f8` | `fuitem`(종목코드) | 29 |
| 지수선물 실시간체결가KP200 | `fC` | `fuitem`(종목코드) | 29 |
| 지수선물 실시간체결가KP200 | `hC` | `fuitem`(종목코드) | 29 |
| 지수선물 실시간예상체결KP200 | `fE` | `fuitem`(종목코드) | 8 |
| 지수선물 실시간예상체결KP200 | `fP` | `fuitem`(종목코드) | 8 |
| 지수선물 실시간예상체결KP200 | `hE` | `fuitem`(종목코드) | 8 |
| 지수옵션 실시간호가KP200 | `o1` | `opitem`(종목코드) | 36 |
| 지수옵션 실시간호가KP200 | `xH` | `opitem`(종목코드) | 36 |
| 지수옵션 실시간호가KP200 | `rH` | `opitem`(종목코드) | 36 |
| 지수옵션 실시간체결가KP200 | `o2` | `opitem`(종목코드) | 53 |
| 지수옵션 실시간체결가KP200 | `xC` | `opitem`(종목코드) | 53 |
| 지수옵션 실시간체결가KP200 | `rC` | `opitem`(종목코드) | 53 |
| 지수옵션 실시간예상체결KP200 | `oE` | `opitem`(종목코드) | 8 |
| 지수옵션 실시간예상체결KP200 | `xE` | `opitem`(종목코드) | 8 |
| 지수옵션 실시간예상체결KP200 | `rE` | `opitem`(종목코드) | 8 |
| 상품선물 실시간호가 | `pH` | `fuitem`(종목코드) | 36 |
| 상품선물 실시간체결가 | `pC` | `fuitem`(종목코드) | 54 |
| 상품선물 실시간예상체결 | `pE` | `code`(종목코드) | 4 |
| 주식선물 실시간호가 | `vH` | `fuitem`(종목코드) | 66 |
| 주식선물 실시간체결가 | `vC` | `fuitem`(종목코드) | 85 |
| 주식선물 실시간예상체결 | `vE` | `expcode`(종목코드) | 8 |
| 주식옵션 실시간호가 | `v1` | `ojitem`(종목코드) | 72 |
| 주식옵션 실시간체결가 | `v2` | `ojitem`(종목코드) | 21 |
| 선물옵션 실시간체결통보 | `d2` | `userid`(사용자ID) | 21 |
| 선물옵션 실시간주문내역통보 | `d3` | `userid`(사용자ID) | 24 |
| KRX야간선물 실시간호가KP200 | `1a` | `fuitem`(종목코드) | 36 |
| KRX야간선물 실시간호가KP200 | `2a` | `fuitem`(종목코드) | 36 |
| KRX야간선물 실시간호가KP200 | `4a` | `fuitem`(종목코드) | 36 |
| KRX야간선물 실시간체결가KP200 | `1c` | `fuitem`(종목코드) | 31 |
| KRX야간선물 실시간체결가KP200 | `2c` | `fuitem`(종목코드) | 31 |
| KRX야간선물 실시간체결가KP200 | `4c` | `fuitem`(종목코드) | 31 |
| KRX야간선물 실시간예상체결KP200 | `1b` | `fuitem`(종목코드) | 8 |
| KRX야간선물 실시간예상체결KP200 | `2b` | `fuitem`(종목코드) | 8 |
| KRX야간선물 실시간예상체결KP200 | `4b` | `fuitem`(종목코드) | 8 |
| KRX야간옵션 실시간호가KP200 | `5a` | `opitem`(종목코드) | 36 |
| KRX야간옵션 실시간호가KP200 | `7a` | `opitem`(종목코드) | 36 |
| KRX야간옵션 실시간호가KP200 | `6a` | `opitem`(종목코드) | 36 |
| KRX야간옵션 실시간체결가KP200 | `5c` | `opitem`(종목코드) | 55 |
| KRX야간옵션 실시간체결가KP200 | `7c` | `opitem`(종목코드) | 55 |
| KRX야간옵션 실시간체결가KP200 | `6c` | `opitem`(종목코드) | 55 |
| KRX야간옵션 실시간예상체결KP200 | `5b` | `opitem`(종목코드) | 8 |
| KRX야간옵션 실시간예상체결KP200 | `7b` | `opitem`(종목코드) | 8 |
| KRX야간옵션 실시간예상체결KP200 | `6b` | `opitem`(종목코드) | 8 |
| KRX야간선물옵션 실시간체결통보 | `dv` | `userid`(사용자ID) | 21 |
| KRX야간선물옵션 실시간주문내역통보 | `dn` | `userid`(사용자ID) | 24 |
