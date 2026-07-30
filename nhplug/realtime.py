"""실시간(WebSocket) 구독 — 접속 URL 유도 · 구독/해제 처리.

프로토콜 정본: 각 openapi.json 의 `x-realtime-channels.protocol` · llms.txt.

- 접속: `wss://api.nhplug.com:7070`(운영·국내) · `:7080`(해외) · `wss://moapi.nhplug.com:17070`(모의)
- 구독: `{"header":{"token":TOKEN,"tr_type":"1"},"body":{"tr_cd":"oc","tr_key":"005930"}}`
  `tr_type` 1=등록 2=해제. 채널코드(`tr_cd`)는 자산군 openapi.json 의 `x-realtime-channels` 참조.
- 푸시: `{"header":{tr_cd,tr_key},"body":{...}}` — JSON · heartbeat 불필요 · 암호화 없음
- 토큰: REST `/oauth2/token` 으로 발급(운영 전용). WS 는 `header.token` 으로만 전달하며
  `Authorization`·`x-client-*` 헤더는 쓰지 않는다.

사용:
    from nhplug.realtime import subscribe

    subscribe(["005930"], print, max_messages=5)              # 국내 체결가(oc)
    subscribe(["AAPL"], print, tr_cd="RC", overseas=True)     # 해외 체결가

의존성: `websocket-client`
"""
from __future__ import annotations

import json
import os
from typing import Callable, Iterable

from .auth import get_base_url, get_token

# 자산군별 WebSocket 포트 (모의투자는 국내·해외 공통 17070)
PORT_DOMESTIC = "7070"
PORT_OVERSEAS = "7080"
PORT_MOCK = "17070"


def _require_websocket():
    try:
        import websocket  # websocket-client
    except ImportError:  # pragma: no cover
        raise ImportError(
            "실시간 구독에는 websocket-client 가 필요합니다:  pip install websocket-client"
        )
    return websocket


def ws_url(overseas: bool = False) -> str:
    """실시간 WebSocket 접속 URL.

    `NHPLUG_WS_URL` 이 있으면 그 값을 그대로 쓰고, 없으면 호출 대상 호스트에서 유도한다.
    모의투자(moapi)는 국내·해외 공통 17070, 운영은 국내 7070 · 해외 7080.
    (나무·N2 브랜드는 호스트에 그대로 반영되므로 별도 설정이 필요 없다.)
    """
    explicit = os.environ.get("NHPLUG_WS_URL")
    if explicit:
        return explicit
    host = get_base_url().split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
    if host.startswith("moapi"):
        port = PORT_MOCK
    else:
        port = PORT_OVERSEAS if overseas else PORT_DOMESTIC
    return f"wss://{host}:{port}"


def subscribe(codes: Iterable[str], on_message: Callable[[dict], None], *,
              tr_cd: str = "oc", overseas: bool = False,
              max_messages: int | None = None, timeout: int = 30,
              url: str | None = None) -> int:
    """`codes` 를 실시간 구독하고 푸시마다 `on_message(dict)` 를 호출한다.

    Args:
        codes: 구독 키 목록(종목코드 등). `tr_key` 로 전달된다.
        on_message: 푸시 1건마다 호출되는 콜백.
        tr_cd: 채널 코드. 국내 체결가 `oc` · 호가 `ob` · 해외 체결가 `RC` 등.
        overseas: 해외 자산군이면 True (포트 7080).
        max_messages: 이 개수를 받으면 종료. None 이면 계속 수신.
        timeout: 이 시간(초) 동안 푸시가 없으면 종료.
        url: 접속 URL 을 직접 지정(테스트용). 없으면 `ws_url()`.

    Returns:
        수신한 푸시 개수. **장 마감 시간에는 0 이 정상**이다.

    종료 시 `tr_type=2` 로 구독을 해제한 뒤 연결을 닫는다.
    """
    websocket = _require_websocket()
    codes = list(codes)
    token = get_token()  # 운영(api)에서 발급 — 모의투자 호출이어도 동일
    ws = websocket.create_connection(url or ws_url(overseas=overseas), timeout=timeout)
    received = 0
    try:
        for code in codes:
            ws.send(json.dumps({"header": {"token": token, "tr_type": "1"},
                                "body": {"tr_cd": tr_cd, "tr_key": code}}))
        while True:
            try:
                raw = ws.recv()
            except websocket.WebSocketTimeoutException:
                break
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue  # 프로토콜 외 메시지는 무시
            on_message(msg)
            received += 1
            if max_messages is not None and received >= max_messages:
                break
    finally:
        try:  # 구독 해제(tr_type=2) 후 종료
            for code in codes:
                ws.send(json.dumps({"header": {"token": token, "tr_type": "2"},
                                    "body": {"tr_cd": tr_cd, "tr_key": code}}))
        except Exception:
            pass
        try:
            ws.close()
        except Exception:
            pass
    return received


# 이전 이름 호환 (snippets/krstock/realtime_execution 에서 쓰던 이름)
subscribe_execution = subscribe
