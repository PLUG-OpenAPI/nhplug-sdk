"""실시간 구독 검증 — 접속 주소·구독 메시지·수신 건수를 모두 보여준다.

    python chk_realtime_execution.py            # 국내 체결가 통합(mc)
    python chk_realtime_execution.py mb         # 호가 통합
    python chk_realtime_execution.py d2         # 체결통보(주문 발생 시에만 수신)

⚠️ 수신 0건이 항상 실패는 아니다 — 장 마감이면 정상이다.
   그래서 **접속 주소와 보낸 구독 메시지를 함께 출력**한다. 0건일 때 아래를 확인할 것:
     · 접속 주소에 /websocket 경로가 붙어 있는가
     · 채널코드가 시장에 맞는가 (통합 mc / KRX oc / NXT nc)
     · 지금이 장중인가
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from nhplug.realtime import subscribe, ws_url  # noqa: E402

if __name__ == "__main__":
    tr_cd = sys.argv[1] if len(sys.argv) > 1 else "mc"
    keys = [] if tr_cd.startswith("d") else ["005930"]   # 통보 채널은 tr_key 불필요

    print(f"채널   : {tr_cd}")
    print(f"접속   : {ws_url(tr_cd=tr_cd)}")
    print(f"구독키 : {keys or ['(빈 값)']}")
    print("-" * 56)

    got = []

    def on_msg(m):
        h, b = m.get("header", {}), m.get("body", {})
        print("  push:", h.get("tr_cd"), h.get("tr_key"),
              "| 필드수:", len(b) if isinstance(b, dict) else "-")
        got.append(m)

    n = subscribe(keys, on_msg, tr_cd=tr_cd, max_messages=3, timeout=15)

    print("-" * 56)
    print(f"수신 {n}건")
    if n:
        print("OK — 연결·구독·수신 모두 정상")
    elif tr_cd.startswith("d"):
        print("OK — 통보 채널은 실제 주문이 발생할 때만 내려옵니다(예외 없이 종료 = 접속 정상)")
    else:
        print("연결은 됐고 푸시가 없습니다. 장 마감이면 정상입니다.")
        print("장중인데 0건이면 위 '접속' 주소와 '채널' 을 확인하세요.")
