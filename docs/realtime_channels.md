# 실시간(WebSocket) 채널 목록

> 정본은 자산군 `openapi.json` 의 `x-realtime-channels` 입니다.
> 나무 [`www.nhplug.com/openapi-docs/<자산>/openapi.json`](https://www.nhplug.com/llms.txt) · N2 `www.n2plug.com/…`
> 이 문서는 그중 **국내주식·해외주식** 채널을 옮겨 놓은 것입니다. 값이 다르면 명세가 맞습니다.

## 접속

```
wss://<host>:<포트>/websocket
```

**경로 `/websocket` 이 필수**입니다.

| 대상 | 포트 |
|---|---|
| 국내 시세 (주식·파생·채권·금현물) | `7070` |
| **해외주식 시세** (`RH`·`rh`·`RC`·`rc`) | `7080` |
| **해외파생 시세** (`FH`·`fh`·`FC`·`fc`) | `7080` |
| **통보** (`d0`·`d1`·`d2`·`d3`·`de`·`dj`·`dk`·`dv`·`dn`) | **`7070`** — 국내·해외 공통 |
| 모의투자 | `17070` — 국내·해외 공통 |

> 해외파생 통보(`dk`·`dj`)를 7080 으로 보내면 **`WSS10006`** 이 납니다.

> 🔴 **대소문자를 구분합니다.** 해외주식 지연 `rh`·`rc`(7080) 와 국내파생 지수옵션 **미니** `rH`·`rC`·`rE`(7070) 는 대소문자만 다릅니다. `tr_cd` 를 정규화하면 국내파생 구독이 해외 포트로 새어 나갑니다.
>
> 해외파생 채널표는 이 문서 범위 밖입니다 — [gbfuture openapi.json](https://www.nhplug.com/openapi-docs/gbfuture/openapi.json) 의 `x-realtime-channels` 를 보세요(`tr_key` 는 `isym`).

## 구독 / 해제

```json
{"header": {"token": "<access_token>", "tr_type": "1"},
 "body":   {"tr_cd": "mc", "tr_key": "005930"}}
```

`tr_type` — `1` 등록 · `2` 해제. 토큰은 `header.token` 으로만 보냅니다(`Authorization`·`x-client-*` 미사용).

## 서버 한도

| 항목 | 한도 | 초과 시 |
|---|---|---|
| 앱키당 동시 세션 | **2** | `WSS10015` |
| 세션당 실시간 등록 | **10** | close code 1000 `"Bye"` — 오류 메시지 없이 끊김 |
| 구독 전송 | **초당 10건** | `WSS10010` |

`nhplug.realtime.subscribe()` 가 자동으로 지킵니다.

---

## 국내주식 (21채널)

### 체결가·호가 — 시장별로 코드가 다릅니다

REST 는 `market_cd` 파라미터로 시장을 고르지만 **실시간은 채널코드 자체가 갈립니다.**

| REST `market_cd` | 체결가 | 호가 | 예상체결 | 회원사 | 프로그램매매 |
|---|---|---|---|---|---|
| `KRX` | `oc` | `ob` | `oa` | `t1` | `t8` |
| `NXT` | `nc` | `nb` | `na` | `ng` | `nn` |
| **`UNT` 통합** | **`mc`** | `mb` | `ma` | `mg` | `mn` |

`oc` 를 쓰면 **NXT 체결이 오지 않습니다.** 오류 없이 데이터만 덜 옵니다.

### 전체

| `tr_cd` | 채널 | `tr_key` |
|---|---|---|
| `mc` | 국내주식 실시간체결가 **통합** | `code` |
| `mb` | 국내주식 실시간호가 통합 | `code` |
| `ma` | 국내주식 실시간예상체결 통합 | `code` |
| `mg` | 국내주식 실시간회원사 통합 | `code` |
| `mn` | 국내주식 실시간프로그램매매 통합 | `code` |
| `oc` | 국내주식 실시간체결가 KRX | `code` |
| `ob` | 국내주식 실시간호가 KRX | `code` |
| `oa` | 국내주식 실시간예상체결 KRX | `code` |
| `t1` | 국내주식 실시간회원사 KRX | `code` |
| `t8` | 국내주식 실시간프로그램매매 KRX | `code` |
| `nc` | 국내주식 실시간체결가 NXT | `code` |
| `nb` | 국내주식 실시간호가 NXT | `code` |
| `na` | 국내주식 실시간예상체결 NXT | `code` |
| `ng` | 국내주식 실시간회원사 NXT | `code` |
| `nn` | 국내주식 실시간프로그램매매 NXT | `code` |
| `e2` | 국내주식 **시간외** 실시간체결가 | `ecn_code` |
| `e5` | 국내주식 시간외 실시간호가 | `ecn_code` |
| `e4` | 국내주식 시간외 실시간예상체결 | `ecn_code` |
| `d2` | 국내주식 실시간 **체결통보** | `userid` |
| `d3` | 국내주식 실시간 **주문내역통보** | `userid` |
| `uB` | 채권지수 실시간 체결가 | `jisuid` |

```python
from nhplug.realtime import subscribe

subscribe(["005930", "000660"], print, max_messages=10)   # 체결가 통합
subscribe(["005930"], print, tr_cd="mb")                  # 호가 통합
subscribe(["005930"], print, tr_cd="e2")                  # 시간외 (tr_key 는 ecn_code)
```

## 해외주식 (6채널)

| `tr_cd` | 채널 | `tr_key` |
|---|---|---|
| `RC` | 해외주식 실시간체결가 | **`gicz15`** |
| `RH` | 해외주식 실시간호가 | **`gicz15`** |
| `rc` | 해외주식 지연체결가 | **`gicz15`** |
| `rh` | 해외주식 지연호가(아시아) | **`gicz15`** |
| `d0` | 해외주식 실시간 **체결통보** | `userid` |
| `d1` | 해외주식 실시간 **주문내역통보** | `userid` |

> ⚠️ **해외 시세의 `tr_key` 는 티커가 아니라 GIC 15자리**입니다.
> REST 해외(`gbstock`)는 `iem_cd` 에 티커(`AAPL`)를 쓰지만 실시간은 다릅니다.
> 값은 명세의 `x-realtime-channels.channels[].tr_key` 정의를 확인하세요.

```python
subscribe(["<gicz15>"], print, tr_cd="RC")   # 포트 7080 자동
subscribe([], print, tr_cd="d0")             # 통보 — 포트 7070 자동
```

## `tr_key` 정리 — 전부 종목코드가 아닙니다

**11종**입니다. 이 문서는 국내주식·해외주식만 다루지만, 표는 **전 자산군**을 담았습니다
(`tr_key` 를 잘못 넣는 것이 실시간에서 가장 흔한 실패이고, 자산군을 옮길 때 특히 자주 틀립니다).

| `tr_key` | 넣는 값 | 쓰는 채널 |
|---|---|---|
| `code` | 종목코드 6자리 | 국내주식 시세 전부 · 상품선물 예상체결 `pE` |
| `ecn_code` | 시간외 코드 | 국내주식 시간외 `e5`·`e2`·`e4` |
| `userid` | 사용자ID 또는 **빈 값** | **통보 9종** `d0`·`d1`·`d2`·`d3`·`de`·`dj`·`dk`·`dv`·`dn` |
| `gicz15` | **GIC 15자리 — 티커 아님** | 해외**주식** 시세 `RH`·`rh`·`RC`·`rc` |
| `isym` | 해외파생 종목코드 | 해외**파생** 시세 `FH`·`fh`·`FC`·`fc` |
| `fuitem` | 선물 종목코드 | 국내 지수선물·상품선물·주식선물 (주·야간) |
| `opitem` | 지수옵션 종목코드 | 국내 지수옵션 (주·야간) |
| `ojitem` | **주식**옵션 종목코드 | 국내 주식옵션 `v1`·`v2` |
| `expcode` | 표준코드 | 장내채권 `c1`~`c4` · 주식선물 예상체결 `vE` |
| `shcode` | 금현물 종목코드 | 금현물 `g5`·`g4`·`gE` |
| `jisuid` | 지수ID | 채권지수 `uB` |

> 정본은 자산군 `openapi.json` 의 `x-realtime-channels.channels[].tr_key` 입니다.
> 국내파생·채권·금현물·해외파생 채널 목록은 각 자산군 문서를 보세요 —
> [krfuture](https://www.nhplug.com/openapi-docs/krfuture/README.md) ·
> [gbfuture](https://www.nhplug.com/openapi-docs/gbfuture/README.md) ·
> [krbond](https://www.nhplug.com/openapi-docs/krbond/README.md) ·
> [krgold](https://www.nhplug.com/openapi-docs/krgold/README.md)

## 구독 응답(ACK)

구독 직후 서버가 **등록 결과**를 한 번 보냅니다. 시세가 아닙니다.

```json
{"header": {"tr_type":"1", "tr_cd":"mc", "rsp_cd":"00000", "rsp_msg":"정상처리되었습니다"},
 "body":   {"tr_key": ["005930"]}}
```

데이터 푸시의 `header` 에는 `tr_type`·`rsp_cd` 가 **없습니다**(`tr_cd`·`tr_key` 뿐). SDK 는 이걸로 구분합니다.

- ACK 는 `max_messages` 에 **세지 않습니다** — 세면 `max_messages=1` 일 때 시세를 못 받습니다.
- 등록 실패(`rsp_cd != "00000"`)는 **stderr 로 알립니다**. `WSS10015`·`WSS10010`·`WSS10006` 은 여기서만 드러납니다.
- 응답까지 콜백으로 받으려면 `subscribe(..., include_ack=True)`.

## ⚠️ 통보 채널은 조용한 게 정상입니다

`d0`·`d1`·`d2`·`d3` 는 **실제 주문이 발생할 때만** 내려옵니다.
구독 후 아무것도 안 와도 연결이 잘못된 것이 아닙니다.

시세 채널도 **장 마감 시간에는 0건**이 정상입니다.

```bash
python snippets/krstock/realtime_execution/chk_realtime_execution.py       # mc
python snippets/krstock/realtime_execution/chk_realtime_execution.py d2    # 체결통보
```

접속 주소와 보낸 구독 메시지를 함께 출력하므로, 0건일 때 무엇을 확인해야 하는지 알 수 있습니다.
