"""연속조회(cts)·유량 스로틀 오프라인 테스트.

네트워크를 타지 않는다 — `requests.post` 를 가짜 응답으로 바꿔 검증한다.
실행:  python tests/test_pagination_throttle.py
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("NHPLUG_APP_KEY", "test-key")
os.environ.setdefault("NHPLUG_APP_SECRET", "test-secret")

from nhplug import client                                    # noqa: E402
from nhplug.client import Meta, call, paginate, rate_limit   # noqa: E402

FAILED = []


def check(cond, label, detail=""):
    print(f"  {'✅' if cond else '❌'} {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        FAILED.append(label)


class FakeRes:
    ok = True
    status_code = 200

    def __init__(self, body, headers=None):
        self._body, self.headers, self.text = body, headers or {}, str(body)

    def json(self):
        return self._body


def install(pages):
    """pages = [(body, headers), ...] 를 순서대로 돌려주는 가짜 서버."""
    state = {"i": 0, "sent": []}

    def fake_post(url, headers=None, data=None, timeout=None):
        state["sent"].append(headers or {})
        body, hdrs = pages[min(state["i"], len(pages) - 1)]
        state["i"] += 1
        return FakeRes(body, hdrs)

    client.requests.post = fake_post
    client.get_token = lambda force=False: "TOKEN"
    return state


OK = {"rsp_cd": "00000", "rsp_msg": "조회가 완료되었습니다."}


def main():
    os.environ["NHPLUG_RATE_LIMIT"] = "0"          # 스로틀은 뒤에서 따로 본다
    print("═══ ① want_meta — 헤더가 살아 오는가 ═══")
    install([({**OK, "Output_0": [1]}, {"cts": "AAA001", "cts_flag": "Y"})])
    data, meta = call("/x", {}, want_meta=True)
    check(isinstance(meta, Meta), "Meta 반환")
    check(meta.cts == "AAA001", "cts 파싱", meta.cts)
    check(meta.cts_flag == "Y", "cts_flag 파싱", meta.cts_flag)
    check(meta.has_next is True, "has_next=True")
    check(data.get("Output_0") == [1], "본문은 그대로")

    print("\n═══ ② 기존 반환형이 깨지지 않는가 ═══")
    install([({**OK, "Output_0": [1]}, {"cts": "A", "cts_flag": "Y"})])
    check(isinstance(call("/x", {}), dict), "want_meta 없으면 dict 그대로")

    print("\n═══ ③ 종료 판정 4종 ═══")
    cases = [
        ("cts_flag=N → 종료",        {"cts": "A", "cts_flag": "N"}, "00000", False),
        ("cts_flag=Y → 계속",        {"cts": "A", "cts_flag": "Y"}, "00000", True),
        ("헤더 없음+00165 → 계속",    {"cts": "A"},                  "00165", True),
        ("헤더 없음+00218 → 계속",    {"cts": "A"},                  "00218", True),
        ("헤더 없음+00000 → 종료",    {"cts": "A"},                  "00000", False),
        ("cts 없음 → 종료",           {"cts_flag": "Y"},             "00000", False),
    ]
    for label, hdrs, code, expect in cases:
        install([({**OK, "rsp_cd": code}, hdrs)])
        _, m = call("/x", {}, want_meta=True)
        check(m.has_next is expect, label, f"has_next={m.has_next}")

    print("\n═══ ④ paginate — 정상 3페이지 ═══")
    install([
        ({**OK, "Output_0": ["p1"]}, {"cts": "K001", "cts_flag": "Y"}),
        ({**OK, "Output_0": ["p2"]}, {"cts": "K002", "cts_flag": "Y"}),
        ({**OK, "Output_0": ["p3"]}, {"cts": "K003", "cts_flag": "N"}),
    ])
    rows = [r for pg in paginate("/x", {}) for r in pg["Output_0"]]
    check(rows == ["p1", "p2", "p3"], "3페이지 전부 순회", str(rows))

    print("\n═══ ⑤ 🔴 cts 가 안 바뀌면 중단 (무한루프 방지) ═══")
    st = install([({**OK, "Output_0": ["x"]}, {"cts": "SAME", "cts_flag": "Y"})])
    n = sum(1 for _ in paginate("/x", {}))
    check(n == 2, "같은 cts 를 받으면 2페이지에서 멈춤", f"{n}페이지")
    check(len(st["sent"]) == 2, "요청도 2회만", f"{len(st['sent'])}회")

    print("\n═══ ⑥ 끝 2~3자만 다른 cts 는 계속 진행 ═══")
    install([
        ({**OK, "Output_0": ["a"]}, {"cts": "20260809000000001", "cts_flag": "Y"}),
        ({**OK, "Output_0": ["b"]}, {"cts": "20260809000000002", "cts_flag": "Y"}),
        ({**OK, "Output_0": ["c"]}, {"cts": "20260809000000003", "cts_flag": "N"}),
    ])
    check(sum(1 for _ in paginate("/x", {})) == 3, "전체 문자열 비교라 3페이지 진행")

    print("\n═══ ⑥-2 본문 ctsz* 폴백 (명세는 본문, 실측은 헤더 — 둘 다 지원) ═══")
    install([({**OK, "Output_0": [{"a": 1, "ctsz30": "B001"}]}, {})])
    _, m = call("/x", {}, want_meta=True)
    check(m.cts == "B001", "본문 ctsz30 을 cts 로 인식", str(m.cts))
    check(m.cts_source == "body", "출처 표기", str(m.cts_source))
    check(m.has_next is True, "cts_flag 없어도 본문 키가 있으면 계속")

    install([({**OK, "Output_0": [{"ctsz16": "H1"}]}, {"cts": "HDR1", "cts_flag": "Y"})])
    _, m = call("/x", {}, want_meta=True)
    check(m.cts == "HDR1" and m.cts_source == "header", "헤더가 있으면 헤더 우선", str(m.cts))

    install([
        ({**OK, "Output_0": [{"ctsz20": "P1"}]}, {}),
        ({**OK, "Output_0": [{"ctsz20": "P2"}]}, {}),
        ({**OK, "Output_0": [{"ctsz20": ""}]},   {}),      # 빈 키 = 마지막
    ])
    check(sum(1 for _ in paginate("/x", {})) == 3, "본문 키로 3페이지 순회 후 종료")

    install([({**OK, "Output_0": [{"ctsz20": "SAME"}]}, {})])
    check(sum(1 for _ in paginate("/x", {})) == 2, "본문 키도 동일하면 2페이지에서 중단")

    print("\n═══ ⑦ max_pages ═══")
    install([({**OK, "Output_0": ["y"]}, {"cts": "K%03d" % i, "cts_flag": "Y"}) for i in range(50)])
    check(sum(1 for _ in paginate("/x", {}, max_pages=5)) == 5, "max_pages=5 에서 멈춤")

    print("\n═══ ⑧ 다음 요청에 cts·cts_flag 가 실리는가 ═══")
    st = install([
        ({**OK}, {"cts": "FIRST", "cts_flag": "Y"}),
        ({**OK}, {"cts": "SECOND", "cts_flag": "N"}),
    ])
    list(paginate("/x", {}))
    h2 = {k.lower(): v for k, v in st["sent"][1].items()}
    check(h2.get("cts") == "FIRST", "2번째 요청 헤더 cts", h2.get("cts"))
    check(h2.get("cts_flag") == "Y", "2번째 요청 헤더 cts_flag", h2.get("cts_flag"))
    check("cts" not in {k.lower() for k in st["sent"][0]}, "1번째 요청엔 cts 없음")

    print("\n═══ ⑨ 스로틀 ═══")
    for var, expect, label in [("", 4.0, "기본 4/s"), ("2", 2.0, "설정 2/s"),
                               ("9", 5.0, "상한 초과 → 5 로 제한"), ("0", 0.0, "0 이면 끔")]:
        os.environ.pop("NHPLUG_RATE_LIMIT", None)
        if var:
            os.environ["NHPLUG_RATE_LIMIT"] = var
        check(rate_limit() == expect, label, f"{rate_limit()}")

    os.environ["NHPLUG_RATE_LIMIT"] = "4"
    client._rate_calls.clear()
    install([({**OK}, {})])
    t0 = time.monotonic()
    for _ in range(6):
        call("/x", {})
    dt = time.monotonic() - t0
    check(dt >= 0.9, "4/s 제한 → 6회에 1초 이상 소요", f"{dt:.2f}s")

    os.environ["NHPLUG_RATE_LIMIT"] = "0"
    client._rate_calls.clear()
    t0 = time.monotonic()
    for _ in range(20):
        call("/x", {})
    check(time.monotonic() - t0 < 0.5, "끄면 지연 없음")

    print("\n" + "─" * 60)
    if FAILED:
        print(f"❌ 실패 {len(FAILED)}건: {FAILED}")
        return 1
    print("전체 통과 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
