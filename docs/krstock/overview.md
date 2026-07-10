# NH투자증권 Open API — 국내주식 (Domestic Stock) Overview

NH투자증권 Open API 의 **국내주식 (Domestic Stock)** 자산군은 주문, 계좌·자산 조회, 시세, 실시간 스트리밍을 제공합니다. (기준: API명세서 260703 / 나무 환경)

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

전체 목록·operationId 는 [README.md](https://www.nhplug.com/openapi-docs/krstock/README.md), 필드·스키마는 [openapi.json](https://www.nhplug.com/openapi-docs/krstock/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krstock/order/v1/cancel` | 주식주문(정정취소) 취소 |
| `POST /krstock/order/v1/cancel#dup-krstockOrderCancel` | 주식예약주문정정취소 |
| `POST /krstock/order/v1/cashBuy` | 주식주문(현금) 매수 |
| `POST /krstock/order/v1/cashSell` | 주식주문(현금) 매도 |
| `POST /krstock/order/v1/creditBuy` | 주식주문(신용) 매수 |
| `POST /krstock/order/v1/creditSell` | 주식주문(신용) 매도 |
| `POST /krstock/order/v1/modify` | 주식주문(정정취소) 정정 |
| `POST /krstock/order/v1/reservedOrder` | 주식예약주문 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krstock/TODO/op` | 주식정정취소가능주문조회 |
| `POST /krstock/inquiry/v1/assetStatus` | 투자계좌자산현황조회 |
| `POST /krstock/inquiry/v1/balance` | 주식잔고조회 |
| `POST /krstock/inquiry/v1/buyableQuantity` | 매수가능수량조회 |
| `POST /krstock/inquiry/v1/dailyOrderExecution` | 주식일별주문체결조회 |
| `POST /krstock/inquiry/v1/dailyPnl` | 실현손익일별합산조회 |
| `POST /krstock/inquiry/v1/integratedMargin` | 주식통합증거금 현황 |
| `POST /krstock/inquiry/v1/realizedPnl` | 주식잔고조회_실현손익 |
| `POST /krstock/inquiry/v1/reservedInquiry` | 주식예약주문조회 |
| `POST /krstock/inquiry/v1/rightsHeld` | 기간별계좌권리현황조회보유 |
| `POST /krstock/inquiry/v1/rightsScheduled` | 기간별계좌권리현황조회예정 |
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

`wss://api.nhplug.com:7070` 에 접속해 아래 메시지로 구독/해제합니다. `tr_type` 1=등록 · 2=해제. 인증은 message header 의 `token`(access token)만 사용.

```json
{ "header": { "token": "{access_token}", "tr_type": "1" },
  "body":   { "tr_cd": "<채널코드>", "tr_key": "<구독키>" } }
```

채널 목록:

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
| 국내주식 실시간호가통합 | `mb` | `code`(종목코드) |
| 국내주식 실시간체결가통합 | `mc` | `code`(종목코드) |
| 국내주식 실시간예상체결통합 | `ma` | `code`(종목코드) |
| 국내주식 실시간회원사통합 | `mg` | `code`(종목코드) |
| 국내주식 실시간프로그램매매통합 | `mn` | `code`(종목코드) |
| 국내주식 실시간호가NXT | `nb` | `code`(종목코드) |
| 국내주식 실시간체결가NXT | `nc` | `code`(종목코드) |
| 국내주식 실시간예상체결NXT | `na` | `code`(종목코드) |
| 국내주식 실시간회원사NXT | `ng` | `code`(종목코드) |
| 국내주식 실시간프로그램매매NXT | `nn` | `code`(종목코드) |
| 국내주식 실시간체결통보 | `d2` | `userid`(사용자ID) |
| 국내주식 실시간주문내역통보 | `d3` | `userid`(사용자ID) |

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

- 본 문서는 **국내주식 (Domestic Stock)** 자산군, API명세서 **260703** / **나무** 환경 기준입니다.
- 공통 에러 코드 표는 미제공, 처리 결과는 응답 `message` 봉투로 확인.
- 실시간 heartbeat·푸시 인코딩·통보 암호화 등 일부 규약은 미확정(TODO).
