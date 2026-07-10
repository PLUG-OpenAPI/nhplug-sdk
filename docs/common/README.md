# NH투자증권 Open API — 공통 (Common: 인증·계좌) Endpoint Index

자산군과 무관한 **플랫폼 공통 API** 입니다. 모든 자산군 조회·주문의 선행 단계이므로 아래 순서로 사용합니다.

> 정본은 [openapi.json](https://www.nhplug.com/openapi-docs/common/openapi.json) 입니다.

## 인증 (Auth)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 접근 토큰 발급 | POST | `/oauth2/token` | commonAuthIssueToken |

- 파라미터는 **쿼리스트링**, Content-Type 은 `application/x-www-form-urlencoded`.
- 파라미터: `appkey`, `appsecretkey`, `grant_type=client_credentials`, `scope=oob`.
- 응답: `access_token` 등. 발급 토큰은 만료 전까지 재사용.

## 계좌 (Account)

| API Name | Method | URI | operationId |
|---|---|---|---|
| 계좌 목록 조회 | POST | `/n2/acctinfo` | commonAccountList |

- 헤더: `Authorization: Bearer {access_token}` + `x-client-id` + `x-client-secret`.
- 요청 바디: `{ "Input_0": {} }` (입력 없음).
- 응답: `Output_0[]` = `{ acct_no, acct_type }` 목록. `acct_no` 를 이후 잔고·주문 API 의 `act_no` 로 사용.

## 권장 호출 순서

1. `POST /oauth2/token` → access token 발급
2. `POST /n2/acctinfo` → 계좌번호(`acct_no`) 목록 확보
3. 확보한 계좌번호로 각 자산군의 잔고조회·주문 등 호출
