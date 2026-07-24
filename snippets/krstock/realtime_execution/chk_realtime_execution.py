from realtime_execution import subscribe_execution

if __name__ == "__main__":
    got = []

    def on_msg(m):
        h = m.get("header", {})
        b = m.get("body", {})
        print("  push:", h.get("tr_cd"), h.get("tr_key"),
              "| 필드수:", len(b) if isinstance(b, dict) else "-")
        got.append(m)

    print("실시간 체결가 구독(005930) — 장중이면 push 수신, 장마감/시간외면 timeout 후 종료")
    n = subscribe_execution(["005930"], on_msg, max_messages=3, timeout=15)
    # 연결·구독이 성공하면 장 마감(수신 0)이어도 OK. 예외 없이 여기 도달하면 정상.
    print(f"수신 {n}건")
    print("OK")
