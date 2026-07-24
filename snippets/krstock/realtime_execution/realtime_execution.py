"""국내주식 실시간 체결가 구독 예제 (WebSocket).

프로토콜 정본: 각 openapi.json 의 x-realtime-channels.protocol · llms.txt.
- 접속: wss://api.nhplug.com:7070 (운영·국내) · wss://moapi.nhplug.com:17070 (모의)  ※ 해외는 7080
- 구독: {"header":{"token": ACCESS_TOKEN, "tr_type":"1"}, "body":{"tr_cd":"oc", "tr_key":"005930"}}
        tr_type 1=등록(구독) 2=해제. 국내주식 체결가(KRX)=oc, 호가=ob (자산군 README 참조). tr_key=종목코드.
- 푸시: {"header":{"tr_cd","tr_key"}, "body":{...필드...}}  (JSON, heartbeat 불필요, 암호화 없음)
- 토큰: REST /oauth2/token 으로 발급(운영 전용). WS 는 header.token 으로만 전달(x-client 헤더 없음).
"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import get_token, get_base_url

try:
    import websocket  # pip install websocket-client
except ImportError:  # pragma: no cover
    raise SystemExit("websocket-client 가 필요합니다:  pip install websocket-client")


def ws_url() -> str:
    """국내 실시간 WebSocket URL. NHPLUG_WS_URL 이 있으면 그 값, 없으면 호출 대상 호스트에서 유도.
    moapi=17070, 그 외(api)=7070. (나무·N2 브랜드는 호스트에서 자동 반영)"""
    explicit = os.environ.get("NHPLUG_WS_URL")
    if explicit:
        return explicit
    host = get_base_url().split("://", 1)[1].split(":", 1)[0]  # 예: api.nhplug.com / moapi.n2plug.com
    port = "17070" if host.startswith("moapi") else "7070"
    return f"wss://{host}:{port}"


def subscribe_execution(codes, on_message, tr_cd: str = "oc",
                        max_messages: int | None = None, timeout: int = 30) -> int:
    """codes(종목코드 리스트)의 실시간 체결가(기본 tr_cd='oc')를 구독하고 push 마다 on_message(dict) 호출.

    max_messages 개를 받으면 종료(None 이면 계속). timeout(초) 동안 push 가 없으면 종료.
    반환: 수신한 push 개수. (장 마감 시에는 0 이 정상)
    """
    token = get_token()  # 운영(api)에서 발급
    ws = websocket.create_connection(ws_url(), timeout=timeout)
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
                continue
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
        ws.close()
    return received


if __name__ == "__main__":
    # 삼성전자(005930) 실시간 체결가 5건 출력 후 종료
    subscribe_execution(["005930"], lambda m: print(m), max_messages=5)
