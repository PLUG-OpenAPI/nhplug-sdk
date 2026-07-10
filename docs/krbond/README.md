# NH투자증권 Open API — 국내채권 (KR Bond) Endpoint Index

All REST URIs relative to `https://api.nhplug.com:8443` (운영 나무) · Method 는 모두 `POST` · 요청 `Input_0` / 응답 `Output_0`+`message`. (기준: 260703 / 나무)

> 정본은 [openapi.json](https://www.nhplug.com/openapi-docs/krbond/openapi.json) 입니다.


## 주문 (Order)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 장내채권 매수주문 | POST | `/krbond/order/v1/bondBuy` | krbondOrderBondBuy |
| 장내채권 취소주문 | POST | `/krbond/order/v1/bondCancel` | krbondOrderBondCancel |
| 장내채권 정정주문 | POST | `/krbond/order/v1/bondModify` | krbondOrderBondModify |
| 장내채권 매도주문 | POST | `/krbond/order/v1/bondSell` | krbondOrderBondSell |
| 장내채권 대용매도주문 | POST | `/krbond/order/v1/bondSubstituteSell` | krbondOrderBondSubstituteSell |

## 조회 (Inquiry)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 장내채권 정정취소가능주문 조회 | POST | `/krbond/TODO/op` | krbondTODOOp |
| 장내채권 잔고조회 | POST | `/krbond/inquiry/v1/bondBalance` | krbondInquiryBondBalance |
| 장내채권 주문체결내역 조회 | POST | `/krbond/inquiry/v1/bondModifiableOrder` | krbondInquiryBondModifiableOrder |
| 장내채권 주문가능수량 조회 | POST | `/krbond/inquiry/v1/bondOrderableQuantity` | krbondInquiryBondOrderableQuantity |
| 장내채권 대용잔고조회 | POST | `/krbond/inquiry/v1/bondSubstituteBalance` | krbondInquiryBondSubstituteBalance |

## 시세 (Market Data)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 장내채권 현재가 | POST | `/krbond/quote/v1/bondCurrent` | krbondQuoteBondCurrent |
| 장내채권 일자별시세 | POST | `/krbond/quote/v1/bondDaily` | krbondQuoteBondDaily |
| 장내채권 상세정보 조회 | POST | `/krbond/quote/v1/bondDetail` | krbondQuoteBondDetail |
| 장내채권 민간평간단가조회 | POST | `/krbond/quote/v1/bondFairValue` | krbondQuoteBondFairValue |
| 장내채권 발행현황 | POST | `/krbond/quote/v1/bondIssuance` | krbondQuoteBondIssuance |
| 장내채권 매매현황 | POST | `/krbond/quote/v1/bondTradingStatus` | krbondQuoteBondTradingStatus |
| 채권 시가평가 수익률(민평) | POST | `/krbond/quote/v1/fairValueYield` | krbondQuoteFairValueYield |
| 물가연동채권물가계수일괄조회 | POST | `/krbond/quote/v1/inflationBond` | krbondQuoteInflationBond |
| 채권 금리 스프레드 일별 수익률 | POST | `/krbond/quote/v1/rateSpreadDailyYield` | krbondQuoteRateSpreadDailyYield |
| 소액채권발행현황 | POST | `/krbond/quote/v1/smallBondIssuance` | krbondQuoteSmallBondIssuance |
| 소액채권호가매매현황 | POST | `/krbond/quote/v1/smallBondQuoteTrading` | krbondQuoteSmallBondQuoteTrading |
| 소액채권신고수익률 | POST | `/krbond/quote/v1/smallBondReportedYield` | krbondQuoteSmallBondReportedYield |
| 소액채권시간대별현재가 | POST | `/krbond/quote/v1/smallBondTimeCurrent` | krbondQuoteSmallBondTimeCurrent |
| 채권 유형별 수익률 비교 | POST | `/krbond/quote/v1/yieldComparisonByType` | krbondQuoteYieldComparisonByType |
| 채권 수익률 추이 | POST | `/krbond/quote/v1/yieldTrend` | krbondQuoteYieldTrend |

## 실시간 (Realtime, WebSocket)

운영 나무 Endpoint: `wss://api.nhplug.com:7070` · 구독 메시지·인증은 [openapi.json](https://www.nhplug.com/openapi-docs/krbond/openapi.json) 의 `x-realtime-channels.protocol` 참조.

| 채널 | tr_cd | tr_key | 응답 필드 수 |
|---|---|---|---|
| 장내채권 실시간 호가소액 | `c1` | `expcode`(표준채권코드) | 35 |
| 장내채권 실시간 호가전환 | `c3` | `expcode`(표준채권코드) | 34 |
| 장내채권 실시간 체결가소액 | `c2` | `expcode`(표준채권코드) | 15 |
| 장내채권 실시간 체결가전환 | `c4` | `expcode`(표준채권코드) | 14 |
| 장내채권 실시간 체결내역 통보 | `de` | `userid`(사용자ID) | 12 |
| 장내채권 실시간 주문내역 통보 | `d3` | `userid`(사용자ID) | 24 |
| 채권지수 실시간 체결가 | `uB` | `jisuid`(지수ID) | 36 |
