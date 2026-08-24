"""실시간(WebSocket) 한도·포트 라우팅·URL 오프라인 테스트.

실제 접속은 하지 않는다 — `websocket.create_connection` 을 가짜로 바꿔
전송된 구독 메시지·세션 수·간격만 검증한다.

실행:  python tests/test_realtime_limits.py
"""
import json
import os
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("NHPLUG_APP_KEY", "test-key")
os.environ.setdefault("NHPLUG_APP_SECRET", "test-secret")

from nhplug import realtime                                        # noqa: E402
from nhplug.realtime import (MAX_KEYS_PER_SESSION, MAX_SESSIONS,   # noqa: E402
                             WS_PATH, is_overseas_channel, subscribe, ws_url)

FAILED = []


def check(cond, label, detail=""):
    print(f"  {'✅' if cond else '❌'} {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        FAILED.append(label)


class FakeWS:
    """가짜 WebSocket — 보낸 메시지를 기록하고 즉시 timeout 으로 끝난다."""
    live = 0
    peak = 0
    lock = threading.Lock()

    def __init__(self, url, log):
        self.url, self.log = url, log
        with FakeWS.lock:
            FakeWS.live += 1
            FakeWS.peak = max(FakeWS.peak, FakeWS.live)
        time.sleep(0.02)          # 동시성 관찰용 지연

    def send(self, raw):
        self.log.append(json.loads(raw))

    def recv(self):
        raise realtime._require_websocket().WebSocketTimeoutException()

    def close(self):
        with FakeWS.lock:
            FakeWS.live -= 1


def install():
    """가짜 커넥션 설치. (보낸메시지, 접속URL목록) 반환."""
    sent, urls = [], []
    ws_mod = realtime._require_websocket()
    orig = ws_mod.create_connection

    def fake(url, timeout=None, **kw):
        urls.append(url)
        return FakeWS(url, sent)

    ws_mod.create_connection = fake
    realtime.get_token = lambda force=False: "TOKEN"
    FakeWS.live = FakeWS.peak = 0
    return sent, urls, (ws_mod, orig)


def main():
    os.environ.pop("NHPLUG_WS_URL", None)
    os.environ["NHPLUG_BASE_URL"] = "https://api.nhplug.com:8443"

    print("═══ ① 접속 URL — /websocket 경로 ═══")
    check(ws_url() == f"wss://api.nhplug.com:7070{WS_PATH}", "국내 시세 7070 + 경로", ws_url())
    check(ws_url(tr_cd="RC") == f"wss://api.nhplug.com:7080{WS_PATH}", "해외 시세 7080", ws_url(tr_cd="RC"))

    print("\n═══ ② 🔴 통보 채널은 해외라도 7070 (WSS10006 방지) ═══")
    for cd in ("d0", "d1", "d2", "d3", "de", "dj", "dk", "dv", "dn"):
        u = ws_url(tr_cd=cd)
        check(":7070" in u, f"{cd} → 7070", u.split("//")[-1])
    check(is_overseas_channel("dk") is False, "dk 는 해외 '시세'가 아님")
    check(is_overseas_channel("RC") is True, "RC 는 해외 시세")

    print("\n═══ ③ 모의투자·override ═══")
    os.environ["NHPLUG_BASE_URL"] = "https://moapi.nhplug.com:8443"
    check(ws_url() == f"wss://moapi.nhplug.com:17070{WS_PATH}", "모의 국내 17070")
    check(ws_url(tr_cd="RC") == f"wss://moapi.nhplug.com:17070{WS_PATH}", "모의 해외도 17070")
    os.environ["NHPLUG_BASE_URL"] = "https://api.nhplug.com:8443"
    check(ws_url(overseas=True, tr_cd="mc") == f"wss://api.nhplug.com:7080{WS_PATH}",
          "overseas 명시가 tr_cd 보다 우선")
    os.environ["NHPLUG_WS_URL"] = "wss://api.nhplug.com:7070"
    check(ws_url() == f"wss://api.nhplug.com:7070{WS_PATH}", "WS_URL 에 경로 없으면 붙여줌")
    os.environ["NHPLUG_WS_URL"] = "wss://x.example.com:9/custom"
    check(ws_url() == "wss://x.example.com:9/custom", "경로가 있으면 그대로")
    os.environ.pop("NHPLUG_WS_URL")

    print("\n═══ ④ 기본 채널 mc (통합) ═══")
    sent, urls, (mod, orig) = install()
    subscribe(["005930"], lambda m: None, timeout=1)
    check(sent[0]["body"]["tr_cd"] == "mc", "기본 tr_cd=mc", sent[0]["body"]["tr_cd"])
    check(sent[0]["header"]["tr_type"] == "1", "등록 tr_type=1")
    check(sent[-1]["header"]["tr_type"] == "2", "종료 시 해제 tr_type=2 (등록 반납)")

    print("\n═══ ⑤ 세션당 10건 초과 → 자동 분할 ═══")
    sent, urls, _ = install()
    subscribe([f"{i:06d}" for i in range(25)], lambda m: None, timeout=1)
    check(len(urls) == 3, "25건 → 세션 3개(10+10+5)", f"{len(urls)}개")
    reg = [m for m in sent if m["header"]["tr_type"] == "1"]
    unreg = [m for m in sent if m["header"]["tr_type"] == "2"]
    check(len(reg) == 25, "등록 25건 전부 전송", f"{len(reg)}건")
    check(len(unreg) == 25, "해제도 25건", f"{len(unreg)}건")
    check(len({m["body"]["tr_key"] for m in reg}) == 25, "키 중복·누락 없음")

    print("\n═══ ⑥ 동시 세션 2 제한 (WSS10015 방지) ═══")
    check(FakeWS.peak <= MAX_SESSIONS, f"동시 접속 최대 {FakeWS.peak} ≤ {MAX_SESSIONS}")

    print("\n═══ ⑦ 구독 전송 속도 (WSS10010 방지) ═══")
    sent, urls, _ = install()
    t0 = time.monotonic()
    subscribe([f"{i:06d}" for i in range(10)], lambda m: None, timeout=1)
    dt = time.monotonic() - t0
    check(dt >= 10 * 2 / realtime.MAX_SUBSCRIBE_PER_SEC * 0.8,
          "등록10+해제10 = 20건이 초당 10건 미만으로 전송", f"{dt:.2f}s")

    print("\n═══ ⑧ 한도 가드 — 사용자가 올릴 수 없다 ═══")
    for var, ceiling in (("NHPLUG_WS_MAX_KEYS", MAX_KEYS_PER_SESSION),
                         ("NHPLUG_WS_MAX_SESSIONS", MAX_SESSIONS),
                         ("NHPLUG_WS_SUBSCRIBE_RATE", realtime.MAX_SUBSCRIBE_PER_SEC)):
        os.environ[var] = "999"
        check(realtime._limit(var) == ceiling, f"{var}=999 → {ceiling} 로 제한",
              str(realtime._limit(var)))
        lower = max(1, ceiling - 1)
        os.environ[var] = str(lower)
        check(realtime._limit(var) == lower, f"{var}={lower} (낮추는 건 허용)")
        os.environ.pop(var)

    # 세마포어가 import 시점에 고정되면 낮춘 값이 반영되지 않는다(실제로 그랬음).
    os.environ["NHPLUG_WS_MAX_SESSIONS"] = "1"
    sent, urls, _ = install()
    subscribe([f"{i:06d}" for i in range(25)], lambda m: None, timeout=1)
    check(FakeWS.peak == 1, "MAX_SESSIONS=1 로 낮추면 동시 접속 1", f"peak={FakeWS.peak}")
    os.environ.pop("NHPLUG_WS_MAX_SESSIONS")

    print("\n═══ ⑨ 통보 채널 — keys 를 비워도 구독된다 ═══")
    sent, urls, _ = install()
    subscribe([], lambda m: None, tr_cd="d2", timeout=1)
    reg = [m for m in sent if m["header"]["tr_type"] == "1"]
    check(len(reg) == 1, "빈 목록도 1건 전송", f"{len(reg)}건")
    check(reg[0]["body"] == {"tr_cd": "d2", "tr_key": ""}, "tr_key='' 로 전송", str(reg[0]["body"]))
    check(":7070" in urls[0], "d2 는 7070")

    print("\n═══ ⑨-2 구독 응답(ACK)은 시세로 세지 않는다 ═══")
    ack = {"header": {"tr_type": "1", "tr_cd": "mc", "rsp_cd": "00000",
                      "rsp_msg": "정상처리되었습니다"}, "body": {"tr_key": ["005930"]}}
    tick = {"header": {"tr_cd": "mc", "tr_key": "005930"}, "body": {"price": "231000"}}
    fail = {"header": {"tr_type": "1", "tr_cd": "mc", "rsp_cd": "WSS10015",
                       "rsp_msg": "세션 초과"}, "body": {}}
    check(realtime.is_ack(ack) is True, "등록 응답 → ACK")
    check(realtime.is_ack(fail) is True, "실패 응답 → ACK")
    check(realtime.is_ack(tick) is False, "시세 푸시 → ACK 아님")

    class AckWS(FakeWS):
        def __init__(self, url, log):
            super().__init__(url, log)
            self._q = [json.dumps(ack), json.dumps(tick), json.dumps(tick)]

        def recv(self):
            if self._q:
                return self._q.pop(0)
            raise realtime._require_websocket().WebSocketTimeoutException()

    ws_mod = realtime._require_websocket()
    sent = []
    ws_mod.create_connection = lambda url, timeout=None, **kw: AckWS(url, sent)
    got = []
    n = subscribe(["005930"], got.append, max_messages=2, timeout=1)
    check(n == 2, "max_messages=2 → 시세 2건 (ACK 제외)", f"{n}건")
    check(len(got) == 2, "콜백에도 시세만 전달", f"{len(got)}건")
    check(all(not realtime.is_ack(m) for m in got), "콜백에 ACK 안 섞임")

    got = []
    ws_mod.create_connection = lambda url, timeout=None, **kw: AckWS(url, sent)
    subscribe(["005930"], got.append, max_messages=2, timeout=1, include_ack=True)
    check(len(got) == 3, "include_ack=True 면 ACK 도 전달", f"{len(got)}건")

    class FailWS(AckWS):
        def __init__(self, url, log):
            FakeWS.__init__(self, url, log)
            self._q = [json.dumps(fail)]

    ws_mod.create_connection = lambda url, timeout=None, **kw: FailWS(url, sent)
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        subscribe(["005930"], lambda m: None, timeout=1)
    check("WSS10015" in buf.getvalue(), "구독 실패는 stderr 로 알림", buf.getvalue().strip()[:50])
    ws_mod.create_connection = lambda url, timeout=None, **kw: FakeWS(url, sent)

    print("\n═══ ⑩ TLS — truststore 있으면 사용, 없으면 기본 검증 ═══")
    ctx = realtime._ssl_context()
    try:
        import truststore  # noqa: F401
        check(ctx is not None, "truststore 설치됨 → OS 저장소 사용")
    except ImportError:
        check(ctx is None, "truststore 없음 → 기본 검증(예외 없이 진행)")
    src = Path(realtime.__file__).read_text(encoding="utf-8")
    check("cert_reqs" not in src, "🔒 cert_reqs 를 만지는 코드가 없다")
    code_lines = [l for l in src.splitlines()
                  if "CERT_NONE" in l and "제공하지 않는다" not in l]
    check(not code_lines, "🔒 CERT_NONE 은 '쓰지 않는다'는 설명에만 등장", str(code_lines[:1]))

    mod.create_connection = orig
    print("\n" + "─" * 60)
    if FAILED:
        print(f"❌ 실패 {len(FAILED)}건: {FAILED}")
        return 1
    print("전체 통과 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
