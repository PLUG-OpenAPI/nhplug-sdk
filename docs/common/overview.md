# NH투자증권 Open API — 공통 (Common: 인증·계좌) Overview

## 개요

이 문서는 특정 자산군(국내주식·해외주식·파생·채권·금현물)에 속하지 않는 **플랫폼 공통 API** 를 설명합니다. 두 API 로 구성됩니다.

1. **접근 토큰 발급** (`POST /oauth2/token`) — 앱키/앱시크릿으로 access token 을 발급받습니다.
2. **계좌 목록 조회** (`POST /n2/acctinfo`) — 자격증명에 연결된 보유 계좌번호 목록을 조회합니다.

이 두 API 는 모든 조회·주문의 **선행 단계**입니다. 자산군 API(잔고·주문 등)는 계좌번호(`act_no`)를 입력으로 요구하는데, 그 계좌번호를 얻는 경로가 바로 `/n2/acctinfo` 입니다.

## 인증 방식

- **토큰 발급**: `/oauth2/token` 에 쿼리 파라미터(`appkey`, `appsecretkey`, `grant_type=client_credentials`, `scope=oob`)로 요청. Content-Type 은 `application/x-www-form-urlencoded`.
- **이후 모든 REST 호출**: 헤더에 `Authorization: Bearer {access_token}` + `x-client-id`(앱키) + `x-client-secret`(앱시크릿).
- 발급한 토큰은 만료 전까지 재사용합니다(호출마다 재발급하지 않습니다).

## 봉투 규약

- `/n2/acctinfo` 는 다른 REST API 와 동일하게 요청 `Input_0` / 응답 `Output_0` 봉투를 사용합니다.
- 응답 공통 봉투: `rsp_cd`(응답코드, `00000`=정상), `rsp_msg`(응답메시지), `cust_no`(고객번호).
- `/oauth2/token` 은 예외적으로 봉투를 쓰지 않고 `access_token` 을 직접 반환합니다.

## 전형적 흐름

```
1) POST /oauth2/token           → access_token 획득
2) POST /n2/acctinfo            → Output_0[].acct_no 목록 획득
3) POST /krstock/inquiry/v1/balance (act_no = 위 acct_no)  → 잔고
   POST /krstock/order/v1/cashBuy   (act_no = 위 acct_no)  → 매수 주문
```

## 참고

- `acct_no`(계좌목록 응답) 와 `act_no`(잔고·주문 입력) 는 필드명이 다르지만 **값은 동일**합니다.
- 계좌구분코드 `acct_type` 의 코드값 정의는 포털 문서를 참조하세요.
