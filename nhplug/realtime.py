"""실시간(WebSocket) 구독 — 접속 URL 유도 · 서버 한도 준수 · 구독/해제 처리.

프로토콜 정본: 각 자산군 `openapi.json` 의 `x-realtime-channels` · llms.txt.

- 접속: `wss://<host>:<포트>/websocket`  ← **경로 `/websocket` 이 필수**다.
  ⚠️ 명세의 `x-realtime-channels.endpoint` 에는 경로가 빠져 있으나(`wss://…:7070`),
     같은 블록 `protocol.connection` 이 "URI 는 /websocket" 이라고 명시한다. 후자가 맞다.
- 포트: **시세**는 국내 7070 · 해외 7080 / **통보**(체결·주문내역)는 국내·해외 **모두 7070**.
  모의투자는 국내·해외 공통 17070.  해외파생 통보(dk·dj)를 7080 으로 보내면 WSS10006.
  ⚠️ 해외 시세는 **해외주식(RH·rh·RC·rc) + 해외파생(FH·fh·FC·fc) 8종 전부** 7080 이다.
- 구독: `{"header":{"token":TOKEN,"tr_type":"1"},"body":{"tr_cd":"mc","tr_key":"005930"}}`
  `tr_type` 1=등록 2=해제. 채널코드(`tr_cd`)는 자산군 openapi.json 참조.
- 푸시: `{"header":{tr_cd,tr_key},"body":{...}}` — JSON · heartbeat 불필요 · 암호화 없음
- 토큰: REST `/oauth2/token` 으로 발급(운영 전용). WS 는 `header.token` 으로만 전달하며
  `Authorization`·`x-client-*` 헤더는 쓰지 않는다.

서버 한도 — 초과 시 조용히 끊기거나 오류가 난다. 아래 MAX_* 상수가 자동으로 지킨다.
    MAX_SESSIONS           앱키당 동시 세션    초과 시 WSS10015
    MAX_KEYS_PER_SESSION   세션당 실시간 등록  초과 시 close code 1000 "Bye" (오류 메시지 없음)
    MAX_SUBSCRIBE_PER_SEC  구독 전송 속도      초과 시 WSS10010
⚠️ **숫자는 상수 정의에만 둔다.** 여기에 옮겨 적으면 두 곳이 어긋난다.

사용:
    from nhplug.realtime import subscribe

    subscribe(["005930"], print, max_messages=5)               # 국내 체결가 통합(mc)
    subscribe(["005930", "000660"], print, tr_cd="mb")         # 국내 호가 통합
    subscribe([], print, tr_cd="d2")                           # 체결통보(tr_key 불필요)

의존성: `websocket-client` · (선택) `truststore` — Windows TLS 검증용
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import threading
import time
from typing import Callable, Iterable
from urllib.parse import urlsplit

from .auth import get_base_url, get_token

# ---------------------------------------------------------------- 접속 주소
#: 접속 URI 경로. 빠지면 서버가 핸드셰이크를 거부하거나 구독을 무시한다.
WS_PATH = "/websocket"

#: 자산군별 WebSocket 포트 (모의투자는 국내·해외 공통 17070)
PORT_DOMESTIC = "7070"
PORT_OVERSEAS = "7080"
PORT_MOCK = "17070"

#: 해외 **시세** 채널 — 7080 을 쓴다. 해외주식(gbstock) 4종 + 해외파생(gbfuture) 4종.
#:   gbstock  RH 호가 · rh 지연호가(아시아) · RC 체결가 · rc 지연체결가   (tr_key = gicz15)
#:   gbfuture FH 호가 · fh 지연호가        · FC 체결가 · fc 지연체결가   (tr_key = isym)
#:
#: 🔴 **대소문자를 절대 정규화하지 말 것**(`.lower()`·`.upper()` 금지).
#:    국내파생 지수옵션 **미니**가 `rH`(호가)·`rC`(체결가)·`rE`(예상체결)인데
#:    해외주식 지연채널 `rh`·`rc` 와 **대소문자만 다르다.** 소문자로 바꾸면
#:    국내파생 미니옵션 구독이 해외 포트(7080)로 새어 나가 조용히 실패한다.
OVERSEAS_QUOTE_CHANNELS = frozenset({
    "RH", "rh", "RC", "rc",          # 해외주식
    "FH", "fh", "FC", "fc",          # 해외파생
})

#: **통보** 채널(체결·주문내역) — 국내·해외 구분 없이 **모두 7070**.
#:   해외파생 dk·dj 를 7080 으로 보내면 WSS10006 이 난다.
NOTICE_CHANNELS = frozenset({"d0", "d1", "d2", "d3", "de", "dj", "dk", "dv", "dn"})

# ---------------------------------------------------------------- 서버 한도
# 🔴 **이 세 줄이 한도의 유일한 정본이다.** 다른 파일·주석에 숫자를 옮겨 적지 말 것.
#    사람이 읽는 표는 docs/realtime_channels.md 한 곳뿐이고,
#    scripts/check_consistency.py 가 이 상수와 그 표를 대조한다.
#    (한때 같은 숫자가 9개 파일 13곳에 흩어져 있었다.)

#: 앱키당 동시 WebSocket 세션. 초과 시 WSS10015.
MAX_SESSIONS = 2
#: 세션 하나가 등록할 수 있는 실시간 건수. 초과 시 close code 1000 "Bye"(오류 메시지 없음).
#: 명세 260911 기준 30 (x-rate-limits.websocket "채널당 최대 30건").
MAX_KEYS_PER_SESSION = 30
#: 구독 메시지 전송 속도(초당). 초과 시 WSS10010. ⚠️ 위 등록 한도와 다른 값이다.
MAX_SUBSCRIBE_PER_SEC = 10

#: 구독 응답(WS_ACK)의 정상 코드. **REST 의 rsp_cd 체계와 별개**다
#: (REST 업무오류 판정은 nhplug/client.py 참조 — rsp_msg 우선).
WS_ACK_OK = "00000"

#: 위 한도는 서버가 강제하는 값이라 **사용자가 올릴 수 없다.** 환경변수로 낮추는 것만 허용한다.
_LIMIT_VARS = {
    "NHPLUG_WS_MAX_SESSIONS": ("MAX_SESSIONS", MAX_SESSIONS),
    "NHPLUG_WS_MAX_KEYS": ("MAX_KEYS_PER_SESSION", MAX_KEYS_PER_SESSION),
    "NHPLUG_WS_SUBSCRIBE_RATE": ("MAX_SUBSCRIBE_PER_SEC", MAX_SUBSCRIBE_PER_SEC),
}
_limit_warned: set[str] = set()


def _limit(var: str) -> int:
    """환경변수로 조정된 한도. **상한은 서버 실측값이며 넘길 수 없다.**"""
    _, ceiling = _LIMIT_VARS[var]
    raw = (os.environ.get(var) or "").strip()
    if not raw:
        return ceiling
    try:
        v = int(raw)
    except ValueError:
        return ceiling
    if v < 1:
        return 1
    if v > ceiling:
        if var not in _limit_warned:
            print(f"⚠️ {var}={v} 는 서버 한도({ceiling})를 넘습니다. {ceiling} 로 제한합니다.",
                  file=sys.stderr)
            _limit_warned.add(var)
        return ceiling
    return v


#: 앱키당 동시 세션 제한. 여러 스레드에서 subscribe 해도 한도를 넘지 않는다.
#: ⚠️ 세마포어를 import 시점에 고정하면 NHPLUG_WS_MAX_SESSIONS 로 낮춰도 반영되지 않는다.
#:    한도가 바뀌면 다시 만든다(구독 시작 시점의 값을 쓴다).
_slots_lock = threading.Lock()
_slots: dict = {"n": None, "sem": None}


def _session_semaphore() -> threading.BoundedSemaphore:
    n = _limit("NHPLUG_WS_MAX_SESSIONS")
    with _slots_lock:
        if _slots["n"] != n:
            _slots["n"], _slots["sem"] = n, threading.BoundedSemaphore(n)
        return _slots["sem"]


_send_lock = threading.Lock()
_last_send = [0.0]


def _throttle_send() -> None:
    """구독 메시지 전송 간격 — 초당 MAX_SUBSCRIBE_PER_SEC 미만으로 유지(WSS10010 방지)."""
    gap = 1.0 / _limit("NHPLUG_WS_SUBSCRIBE_RATE")
    with _send_lock:
        wait = _last_send[0] + gap - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_send[0] = time.monotonic()


def _require_websocket():
    try:
        import websocket  # websocket-client
    except ImportError:  # pragma: no cover
        raise ImportError(
            "실시간 구독에는 websocket-client 가 필요합니다:  pip install websocket-client"
        )
    return websocket


def _ssl_context() -> ssl.SSLContext | None:
    """TLS 검증 컨텍스트.

    실거래 WebSocket(:7070/:7080)은 서버가 **중간 CA 를 보내지 않아** 파이썬 기본
    OpenSSL 검증이 실패한다(curl·schannel 은 OS 저장소로 자동 보완돼 성공).
    `truststore` 가 설치돼 있으면 **OS 인증서 저장소**를 써서 이 문제를 피한다.

        pip install "nhplug[tls]"      # 또는  pip install truststore

    ⚠️ 검증을 끄는 방법(CERT_NONE)은 제공하지 않는다. 중간자 공격에 그대로 노출된다.
    """
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        return None


def is_overseas_channel(tr_cd: str | None) -> bool:
    """해외 **시세** 채널인가(포트 7080) — 해외주식 4종 + 해외파생 4종.

    통보 채널은 해외라도 7070 이므로 False.
    ⚠️ 대소문자를 구분한다. `rC`(국내파생 미니옵션)는 False, `rc`(해외주식 지연)는 True.
    """
    return tr_cd in OVERSEAS_QUOTE_CHANNELS


def ws_url(overseas: bool | None = None, tr_cd: str | None = None) -> str:
    """실시간 WebSocket 접속 URL (`/websocket` 포함).

    포트 결정:
        모의투자(moapi)      → 17070 (국내·해외 공통)
        해외 **시세** 채널    → 7080   (해외주식 RH·rh·RC·rc / 해외파생 FH·fh·FC·fc)
        그 외 — 국내 시세 + **모든 통보 채널** → 7070

    `overseas` 를 명시하면 그 값이 우선하고, 생략하면 `tr_cd` 로 판별한다.
    `NHPLUG_WS_URL` 이 있으면 그 값을 쓴다(경로가 없으면 `/websocket` 을 붙여 준다).
    """
    explicit = os.environ.get("NHPLUG_WS_URL")
    if explicit:
        e = explicit.strip().rstrip("/")
        return e if urlsplit(e).path else e + WS_PATH

    host = get_base_url().split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
    if host.startswith("moapi"):
        port = PORT_MOCK
    else:
        if overseas is None:
            overseas = is_overseas_channel(tr_cd)
        port = PORT_OVERSEAS if overseas else PORT_DOMESTIC
    return f"wss://{host}:{port}{WS_PATH}"


def _chunks(items: list[str], size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def is_ack(msg: dict) -> bool:
    """구독 등록/해제 **응답**인가(시세 데이터가 아님).

    실측 응답:
        {"header": {"tr_type":"1", "tr_cd":"mc", "rsp_cd":"00000", "rsp_msg":"정상처리되었습니다"},
         "body":   {"tr_key": ["005930"]}}

    데이터 푸시의 header 에는 `tr_type`·`rsp_cd` 가 없다(`tr_cd`·`tr_key` 뿐).
    """
    h = msg.get("header") if isinstance(msg, dict) else None
    return isinstance(h, dict) and ("tr_type" in h or "rsp_cd" in h)


def _run_session(keys: list[str], on_message, *, tr_cd: str, url: str,
                 max_messages: int | None, timeout: int, stop: threading.Event,
                 include_ack: bool = False) -> int:
    """세션 하나 — 최대 MAX_KEYS_PER_SESSION 건을 등록하고 푸시를 받는다."""
    websocket = _require_websocket()
    token = get_token()          # 운영(api)에서 발급 — 모의투자 호출이어도 동일
    ctx = _ssl_context()
    opts = {"sslopt": {"context": ctx}} if ctx else {}

    with _session_semaphore():   # 동시 세션 2개 초과 금지(WSS10015)
        ws = websocket.create_connection(url, timeout=timeout, **opts)
        received = 0
        try:
            for k in keys:
                _throttle_send()          # MAX_SUBSCRIBE_PER_SEC 미만(WSS10010)
                ws.send(json.dumps({"header": {"token": token, "tr_type": "1"},
                                    "body": {"tr_cd": tr_cd, "tr_key": k}}))
            while not stop.is_set():
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException:
                    break
                except websocket.WebSocketConnectionClosedException:
                    break                 # 등록 초과 시 서버가 close 1000 "Bye" 로 끊는다
                if not raw:
                    continue
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue              # 프로토콜 외 메시지는 무시

                if is_ack(msg):
                    # 구독 등록/해제 응답. 데이터가 아니므로 **세지 않는다** —
                    # 세면 max_messages=1 일 때 시세를 한 건도 못 받고 끝난다.
                    h = msg.get("header", {})
                    code = str(h.get("rsp_cd") or "")
                    if code and code != WS_ACK_OK:
                        # 등록 실패(WSS10015 세션초과 · WSS10010 전송과다 · WSS10006 포트오류 등)는
                        # 여기서만 드러난다. 조용히 넘기면 원인을 못 찾는다.
                        print(f"⚠️ 구독 실패 [{tr_cd}] {code} {h.get('rsp_msg') or ''}",
                              file=sys.stderr)
                    if include_ack:
                        on_message(msg)
                    continue

                on_message(msg)
                received += 1
                if max_messages is not None and received >= max_messages:
                    break
        finally:
            try:                          # 등록을 반납해야 다음 세션이 자리를 쓴다
                for k in keys:
                    _throttle_send()
                    ws.send(json.dumps({"header": {"token": token, "tr_type": "2"},
                                        "body": {"tr_cd": tr_cd, "tr_key": k}}))
            except Exception:
                pass
            try:
                ws.close()
            except Exception:
                pass
        return received


def subscribe(keys: Iterable[str], on_message: Callable[[dict], None], *,
              tr_cd: str = "mc", overseas: bool | None = None,
              max_messages: int | None = None, timeout: int = 30,
              url: str | None = None, include_ack: bool = False) -> int:
    """`keys` 를 실시간 구독하고 푸시마다 `on_message(dict)` 를 호출한다.

    서버 한도를 자동으로 지킨다.
      - 등록이 `MAX_KEYS_PER_SESSION` 을 넘으면 그만큼씩 나눠 **여러 세션**으로 처리한다.
      - 동시 세션은 `MAX_SESSIONS` 를 넘지 않는다(초과분은 앞 세션이 끝나면 이어서 실행).
      - 구독 전송은 `MAX_SUBSCRIBE_PER_SEC` 미만으로 제한한다.
      - 종료 시 `tr_type=2` 로 **등록을 반납**한다.

    Args:
        keys: 구독 키 목록. `tr_key` 로 전달된다.
            ⚠️ **채널마다 넣는 값이 다르다 — 전부 종목코드가 아니다.**
            국내주식 시세 `code`(6자리) · 시간외 `ecn_code` ·
            **통보(d0·d1·d2·d3·de·dj·dk·dv·dn) `userid`** 이거나 빈 값 ·
            **해외주식 시세 `gicz15`**(GIC 15자리 — 티커 아님) ·
            **해외파생 시세 `isym`** · 국내파생 `fuitem`/`opitem`/`ojitem` ·
            채권 `expcode` · 금현물 `shcode` · 채권지수 `jisuid`.
            정본은 자산군 `openapi.json` 의 `x-realtime-channels`.
            비워 두면(`[]`) `tr_key=""` 로 한 번 구독한다(통보 채널용).
        on_message: 푸시 1건마다 호출되는 콜백.
        tr_cd: 채널 코드. 기본 `mc`(국내 체결가 **통합** = KRX+NXT).
            KRX 전용은 `oc`, NXT 전용은 `nc`. 호가는 `mb`/`ob`/`nb`.
        overseas: 포트를 강제 지정(True=7080). 생략하면 `tr_cd` 로 자동 판별한다.
        max_messages: 세션당 이 개수를 받으면 종료. None 이면 계속 수신.
        timeout: 이 시간(초) 동안 푸시가 없으면 종료.
        url: 접속 URL 직접 지정(테스트용). 없으면 `ws_url()`.
        include_ack: True 면 구독 등록/해제 **응답**도 콜백에 넘긴다(기본 False).
            응답은 시세가 아니므로 `max_messages` 에 세지 않는다.
            등록이 실패하면(`rsp_cd != WS_ACK_OK`) 기본값에서도 stderr 로 알린다.

    Returns:
        수신한 **시세 푸시** 개수(구독 응답은 제외). **장 마감 시간에는 0 이 정상**이다.
        통보 채널은 **실제 주문이 발생할 때만** 내려온다.
    """
    keys = [str(k) for k in keys] or [""]        # 통보 채널은 tr_key 가 빈 값
    target = url or ws_url(overseas=overseas, tr_cd=tr_cd)
    groups = list(_chunks(keys, _limit("NHPLUG_WS_MAX_KEYS")))
    stop = threading.Event()

    if len(groups) == 1:
        return _run_session(groups[0], on_message, tr_cd=tr_cd, url=target,
                            max_messages=max_messages, timeout=timeout, stop=stop,
                            include_ack=include_ack)

    # 한도를 넘으면 여러 세션으로 나눈다. 동시 실행 수는 세마포어가 MAX_SESSIONS 로 묶는다.
    lock = threading.Lock()
    total = [0]

    def worker(group: list[str]) -> None:
        n = _run_session(group, on_message, tr_cd=tr_cd, url=target,
                         max_messages=max_messages, timeout=timeout, stop=stop,
                         include_ack=include_ack)
        with lock:
            total[0] += n

    threads = [threading.Thread(target=worker, args=(g,), daemon=True) for g in groups]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return total[0]


# 이전 이름 호환 (snippets/krstock/realtime_execution 에서 쓰던 이름)
subscribe_execution = subscribe
