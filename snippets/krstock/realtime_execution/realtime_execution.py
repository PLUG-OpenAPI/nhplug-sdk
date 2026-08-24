"""국내주식 실시간 체결가 구독 예제 (WebSocket).

    from nhplug.realtime import subscribe, ws_url

    subscribe(["005930"], print, max_messages=5)            # 체결가 통합(mc) — 기본
    subscribe(["005930"], print, tr_cd="mb")                # 호가 통합
    subscribe(["005930"], print, tr_cd="oc")                # KRX 전용 체결가
    subscribe([], print, tr_cd="d2")                        # 체결통보(주문 발생 시에만)

프로토콜 정본: 자산군 openapi.json 의 x-realtime-channels
- 접속: wss://api.nhplug.com:7070/websocket   ← **경로 /websocket 필수**
        해외 '시세'만 7080 · 통보는 해외라도 7070 · 모의투자 17070
- 구독: {"header":{"token":TOKEN,"tr_type":"1"},"body":{"tr_cd":"mc","tr_key":"005930"}}
- 푸시: {"header":{tr_cd,tr_key},"body":{...}}  (JSON, heartbeat 불필요, 암호화 없음)

⚠️ 채널코드는 시장별로 갈린다 — 통합 mc / KRX oc / NXT nc.
   REST 의 market_cd 파라미터와 달리 **코드 자체가 다르다.** oc 를 쓰면 NXT 체결이 빠진다.

서버 한도는 SDK 가 자동으로 지킨다(10건/세션 · 동시 2세션 · 초당 10건).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from nhplug.realtime import subscribe, ws_url  # noqa: E402,F401

# 예전 이름 호환
subscribe_execution = subscribe


if __name__ == "__main__":
    print("접속:", ws_url())
    n = subscribe(["005930"], lambda m: print(m), max_messages=5)
    print(f"수신 {n}건")
