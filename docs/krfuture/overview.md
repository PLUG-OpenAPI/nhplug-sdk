# NH투자증권 Open API — 국내파생 (KR Derivatives) Overview

NH투자증권 Open API 의 **국내파생 (KR Derivatives)** 자산군은 주문, 계좌·자산 조회, 시세, 실시간 스트리밍을 제공합니다. (기준: API명세서 260703 최신 / 나무 환경)

---

## 환경 및 접속 정보

> ⚠️ 주소마다 용도가 다릅니다. **실주문은 실거래에서만 체결**됩니다. 개발·검증은 테스트/모의에서 먼저 하세요. 순서: 테스트/모의 → 검증 → 실거래.

API 포탈: `https://www.nhplug.com` (나무)

| 용도 | REST | WebSocket |
|---|---|---|
| 🟢 테스트 (실매매 전 검증) | `https://devapi.nhplug.com:8443` | `wss://devapi.nhplug.com:7070` |
| 🟢 모의투자 (교육이수) | `https://moapi.nhplug.com:8443` | `wss://moapi.nhplug.com:17070` |
| 🔴 실거래 (실제 주문) | `https://api.nhplug.com:8443` | `wss://api.nhplug.com:7070` |

> WS 포트: 국내 7070 · 해외 7080 · 모의 17070. N2 환경은 추후.

---

## 개요

### 인증

- REST: `Authorization: Bearer {access_token}` + `x-client-id` + `x-client-secret`
- WebSocket: 구독 메시지 `header.token` 에 access token (추가 헤더 없음)
- 토큰 발급: `POST /oauth2/token` (공통 API)

### 요청·응답 규약

REST 는 `POST` + `application/json`. 요청 `Input_0` / 응답 `Output_0`(배열) + `message` 봉투. 각 필드 설명(한글명·길이·코드값)은 openapi.json 의 description 참조.

---

## 기능 목록

전체 목록·operationId 는 [README.md](https://www.nhplug.com/openapi-docs/krfuture/README.md), 필드·스키마·설명은 [openapi.json](https://www.nhplug.com/openapi-docs/krfuture/openapi.json) 정본 참조.


### 주문 (Order)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krfuture/order/v1/day` | 선물옵션 주문주간 |
| `POST /krfuture/order/v1/dayCancel` | 선물옵션 정정취소주문주간취소 |
| `POST /krfuture/order/v1/dayModify` | 선물옵션 정정취소주문주간정정 |
| `POST /krfuture/order/v1/nightCancel` | 선물옵션 정정취소주문야간취소 |
| `POST /krfuture/order/v1/nightModify` | 선물옵션 정정취소주문야간정정 |
| `POST /krfuture/order/v1/nightNight` | 선물옵션 주문야간 |

### 조회 (Inquiry)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krfuture/inquiry/v1/balance` | 선물옵션 잔고현황 |
| `POST /krfuture/inquiry/v1/commission` | 선물옵션기간약정수수료일별 |
| `POST /krfuture/inquiry/v1/evalPnl` | 선물옵션 잔고평가손익내역 |
| `POST /krfuture/inquiry/v1/executionHistory` | 선물옵션 기준일체결내역 |
| `POST /krfuture/inquiry/v1/margin` | 선물옵션 증거금 상세 |
| `POST /krfuture/inquiry/v1/nightBalance` | (야간)선물옵션 잔고현황 |
| `POST /krfuture/inquiry/v1/nightMargin` | (야간)선물옵션 증거금 상세 |
| `POST /krfuture/inquiry/v1/nightOrderExecutionHistory` | (야간)선물옵션 주문체결 내역조회 |
| `POST /krfuture/inquiry/v1/nightOrderable` | (야간)선물옵션 주문가능 조회 |
| `POST /krfuture/inquiry/v1/orderExecutionHistory` | 선물옵션 주문체결내역조회 |
| `POST /krfuture/inquiry/v1/orderable` | 선물옵션 주문가능 |

### 시세 (Market Data)

| 엔드포인트 | 설명 |
|------|------|
| `POST /krfuture/quote/v1/daily` | 선물옵션 일자별 |
| `POST /krfuture/quote/v1/day` | 선물옵션 시세주간 |
| `POST /krfuture/quote/v1/dayPeriod` | 선물옵션기간별시세(일/주/월/년)주간 |
| `POST /krfuture/quote/v1/intradayExpectedTrend` | 선물옵션 변동거래량 |
| `POST /krfuture/quote/v1/night` | 선물옵션 시세야간 |
| `POST /krfuture/quote/v1/nightPeriod` | 선물옵션기간별시세(일/주/월/년)야간 |
| `POST /krfuture/quote/v1/timeProgramTrading` | 선물옵션 프로그램매매 |
| `POST /krfuture/quote/v1/tradingStatus` | 선물옵션 시간대별 투자자 매매현황 |

### 실시간 (Realtime · WebSocket)

`wss://api.nhplug.com:7070` 에 접속해 아래 메시지로 구독/해제합니다. `tr_type` 1=등록 · 2=해제. 인증은 message header 의 `token`(access token)만 사용.

```json
{ "header": { "token": "{access_token}", "tr_type": "1" },
  "body":   { "tr_cd": "<채널코드>", "tr_key": "<구독키>" } }
```

채널 목록:

| 채널 | tr_cd | tr_key |
|---|---|---|
| 지수선물 실시간호가KP200 | `f1` | `fuitem`(종목코드) |
| 지수선물 실시간호가KQ150 | `fH` | `fuitem`(종목코드) |
| 지수선물 실시간호가미니 | `hH` | `fuitem`(종목코드) |
| 지수선물 실시간체결가KP200 | `f8` | `fuitem`(종목코드) |
| 지수선물 실시간체결가KQ150 | `fC` | `fuitem`(종목코드) |
| 지수선물 실시간체결가미니 | `hC` | `fuitem`(종목코드) |
| 지수선물 실시간예상체결KP200 | `fE` | `fuitem`(종목코드) |
| 지수선물 실시간예상체결KQ150 | `fP` | `fuitem`(종목코드) |
| 지수선물 실시간예상체결미니 | `hE` | `fuitem`(종목코드) |
| 지수옵션 실시간호가KP200 | `o1` | `opitem`(종목코드) |
| 지수옵션 실시간호가KQ150 | `xH` | `opitem`(종목코드) |
| 지수옵션 실시간호가미니 | `rH` | `opitem`(종목코드) |
| 지수옵션 실시간체결가KP200 | `o2` | `opitem`(종목코드) |
| 지수옵션 실시간체결가KQ150 | `xC` | `opitem`(종목코드) |
| 지수옵션 실시간체결가미니 | `rC` | `opitem`(종목코드) |
| 지수옵션 실시간예상체결KP200 | `oE` | `opitem`(종목코드) |
| 지수옵션 실시간예상체결KQ150 | `xE` | `opitem`(종목코드) |
| 지수옵션 실시간예상체결미니 | `rE` | `opitem`(종목코드) |
| 상품선물 실시간호가 | `pH` | `fuitem`(종목코드) |
| 상품선물 실시간체결가 | `pC` | `fuitem`(종목코드) |
| 상품선물 실시간예상체결 | `pE` | `code`(종목코드) |
| 주식선물 실시간호가 | `vH` | `fuitem`(종목코드) |
| 주식선물 실시간체결가 | `vC` | `fuitem`(종목코드) |
| 주식선물 실시간예상체결 | `vE` | `expcode`(종목코드) |
| 주식옵션 실시간호가 | `v1` | `ojitem`(종목코드) |
| 주식옵션 실시간체결가 | `v2` | `ojitem`(종목코드) |
| 선물옵션 실시간체결통보 | `d2` | `userid`(사용자ID) |
| 선물옵션 실시간주문내역통보 | `d3` | `userid`(사용자ID) |
| KRX야간선물 실시간호가KP200 | `1a` | `fuitem`(종목코드) |
| KRX야간선물 실시간호가KQ150 | `2a` | `fuitem`(종목코드) |
| KRX야간선물 실시간호가미니 | `4a` | `fuitem`(종목코드) |
| KRX야간선물 실시간체결가KP200 | `1c` | `fuitem`(종목코드) |
| KRX야간선물 실시간체결가KQ150 | `2c` | `fuitem`(종목코드) |
| KRX야간선물 실시간체결가미니 | `4c` | `fuitem`(종목코드) |
| KRX야간선물 실시간예상체결KP200 | `1b` | `fuitem`(종목코드) |
| KRX야간선물 실시간예상체결KQ150 | `2b` | `fuitem`(종목코드) |
| KRX야간선물 실시간예상체결미니 | `4b` | `fuitem`(종목코드) |
| KRX야간옵션 실시간호가KP200 | `5a` | `opitem`(종목코드) |
| KRX야간옵션 실시간호가KQ150 | `7a` | `opitem`(종목코드) |
| KRX야간옵션 실시간호가미니 | `6a` | `opitem`(종목코드) |
| KRX야간옵션 실시간체결가KP200 | `5c` | `opitem`(종목코드) |
| KRX야간옵션 실시간체결가KQ150 | `7c` | `opitem`(종목코드) |
| KRX야간옵션 실시간체결가미니 | `6c` | `opitem`(종목코드) |
| KRX야간옵션 실시간예상체결KP200 | `5b` | `opitem`(종목코드) |
| KRX야간옵션 실시간예상체결KQ150 | `7b` | `opitem`(종목코드) |
| KRX야간옵션 실시간예상체결미니 | `6b` | `opitem`(종목코드) |
| KRX야간선물옵션 실시간체결통보 | `dv` | `userid`(사용자ID) |
| KRX야간선물옵션 실시간주문내역통보 | `dn` | `userid`(사용자ID) |

---

## 시작하기

1. 포탈(`https://www.nhplug.com`)에서 `appkey`·`appsecretkey` 발급
2. `POST /oauth2/token` 으로 access token 발급 (공통 API)
3. `POST /n2/acctinfo` 로 계좌번호(act_no) 확보 후 각 API 호출

---

## 비고

- 본 문서는 **국내파생 (KR Derivatives)** 자산군, API명세서 **260703 최신** / **나무** 환경 기준입니다.
- 공통 에러 코드 표는 미제공, 처리 결과는 응답 `message` 봉투로 확인.
- 실시간 heartbeat·푸시 인코딩·통보 암호화 등 일부 규약은 미확정(TODO).
