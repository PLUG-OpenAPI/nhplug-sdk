"""국내주식 실시간 체결가 구독 예제 (WebSocket).

구현은 라이브러리(`nhplug.realtime`)에 있습니다. 이 파일은 사용 예시입니다.

    from nhplug.realtime import subscribe, ws_url

    subscribe(["005930"], print, max_messages=5)          # 국내 체결가(tr_cd="oc")
    subscribe(["005930"], print, tr_cd="ob")              # 국내 호가
    subscribe(["AAPL"], print, tr_cd="RC", overseas=True) # 해외 체결가(포트 7080)

프로토콜 정본: 각 openapi.json 의 x-realtime-channels.protocol · llms.txt.
- 접속: wss://api.nhplug.com:7070(운영·국내) · :7080(해외) · wss://moapi.nhplug.com:17070(모의)
- 구독: {"header":{"token":TOKEN,"tr_type":"1"},"body":{"tr_cd":"oc","tr_key":"005930"}}
- 푸시: {"header":{tr_cd,tr_key},"body":{...}}  (JSON, heartbeat 불필요, 암호화 없음)
- 토큰: REST /oauth2/token 으로 발급(운영 전용). WS 는 header.token 으로만 전달.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug.realtime import subscribe, ws_url  # noqa: E402,F401

# 이전 예제와의 호환 (같은 이름으로 계속 import 가능)
subscribe_execution = subscribe


if __name__ == "__main__":
    print("접속:", ws_url())
    # 삼성전자(005930) 실시간 체결가 5건 출력 후 종료 (장 마감 시 0건이 정상)
    n = subscribe(["005930"], lambda m: print(m), max_messages=5)
    print(f"수신 {n}건")
