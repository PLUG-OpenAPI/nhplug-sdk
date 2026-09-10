"""업무 판정 제거 회귀 테스트 (0.4.0).

🔴 지키려는 규칙은 하나다.

    HTTP 200      → 응답 본문을 **그대로** 반환. 예외 없음.
    HTTP 200 아님 → NhplugError. 본문은 .raw 에 원문 그대로.

같은 rsp_cd 값이 API 마다 정상일 수도 오류일 수도 있어 SDK 가 판정하면 반드시 오판한다.
이 테스트는 **제거한 판정이 되살아나는 것**을 막는다(실제로 두 번 되살아났다).

네트워크를 타지 않는다 — `requests.post` 를 가짜 응답으로 바꿔 검증한다.
실행:  python tests/test_no_judgment.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("NHPLUG_APP_KEY", "test-key")
os.environ.setdefault("NHPLUG_APP_SECRET", "test-secret")
os.environ["NHPLUG_RATE_LIMIT"] = "0"          # 스로틀 끄고 판정만 본다

import nhplug                                   # noqa: E402
from nhplug import client                       # noqa: E402
from nhplug.client import call, status_of       # noqa: E402
from nhplug.errors import NhplugError           # noqa: E402

FAILED = []


def check(cond, label, detail=""):
    print(f"  {'✅' if cond else '❌'} {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        FAILED.append(label)


class FakeRes:
    def __init__(self, body, status=200, headers=None):
        self._body = body
        self.status_code = status
        self.ok = 200 <= status < 300
        self.headers = headers or {}
        self.text = str(body)

    def json(self):
        return self._body


def install(body, status=200, headers=None):
    client.requests.post = lambda *a, **k: FakeRes(body, status, headers)
    client.get_token = lambda force=False: "TOKEN"


def main():
    # ── ① HTTP 200 이면 무슨 rsp_cd 가 와도 예외가 나지 않는다 ────────────────
    print("═══ ① HTTP 200 → 예외 없음 (rsp_cd 가 무엇이든) ═══")
    cases = [
        ("00000", "조회가 완료되었습니다."),
        ("13578", "조회할 내역이 없습니다."),
        ("99999", "종목코드 항목을 입력하세요."),      # 예전엔 예외였다
        ("00007", "처리중 오류가 발생했습니다."),      # 예전엔 예외였다
        ("XXXXX", ""),                                # 미지의 코드 + 빈 메시지
    ]
    for cd, msg in cases:
        body = {"rsp_cd": cd, "rsp_msg": msg, "Output_0": {"v": 1}}
        install(body)
        try:
            data = call("/x", {})
            check(data == body, f"rsp_cd={cd} → 본문 그대로 반환", repr(msg)[:30])
        except NhplugError as e:
            check(False, f"rsp_cd={cd} → 예외가 나면 안 됨", f"{e.category} {e.code}")

    # ── ② 응답을 손대지 않는다 ────────────────────────────────────────────
    print("\n═══ ② 응답 본문을 가공하지 않는다 ═══")
    body = {"rsp_cd": "00166", "rsp_msg": "정상처리되었습니다",
            "Output_0": {"a": 1}, "Output_1": [{"b": 2}], "cust_no": "X"}
    install(body)
    data = call("/x", {})
    check(data is not None and data == body, "키·값이 그대로", str(sorted(data))[:60])
    check(data.get("rsp_cd") == "00166", "rsp_cd 보존")
    check(data.get("rsp_msg") == "정상처리되었습니다", "rsp_msg 보존")

    # ── ③ status_of 는 꺼내 줄 뿐 판정하지 않는다 ─────────────────────────
    print("\n═══ ③ status_of — 꺼내기만 한다 ═══")
    check(status_of(body) == ("00166", "정상처리되었습니다"), "튜플로 반환")
    check(status_of({"rsp_cd": 13578}) == ("13578", None), "숫자 rsp_cd 도 문자열로")
    check(status_of({}) == (None, None), "봉투 없으면 (None, None)")
    check(status_of(None) == (None, None), "dict 아니면 (None, None)")
    check(status_of([1, 2]) == (None, None), "리스트도 (None, None)")

    # ── ④ HTTP 200 아님 → 오류. 본문은 raw 에 원문 그대로 ──────────────────
    print("\n═══ ④ HTTP 200 아님 → 오류 (본문은 raw 에 원문) ═══")
    err = {"rsp_cd": "IGW40024", "rsp_msg": "필수 항목이 누락되었습니다."}
    install(err, status=400)
    try:
        call("/x", {})
        check(False, "400 이면 예외가 나야 한다")
    except NhplugError as e:
        check(e.status == 400, "status 보존", str(e.status))
        check(e.raw == err, "raw 에 본문 원문")
        check(e.message == "필수 항목이 누락되었습니다.", "rsp_msg 를 메시지로", e.message)
        check(e.category == "http", "category=http", e.category)

    # ── ⑤ 게이트웨이 오류 서식(error_code/error_description)도 살린다 ──────
    print("\n═══ ⑤ 게이트웨이 서식 — 메시지를 잃지 않는다 ═══")
    gw = {"error_description": "유효하지 않은 AppKey입니다.", "error_code": "IGW40031"}
    install(gw, status=403)
    try:
        call("/x", {})
        check(False, "403 이면 예외가 나야 한다")
    except NhplugError as e:
        check(e.code == "IGW40031", "error_code 를 code 로", str(e.code))
        check(e.message == "유효하지 않은 AppKey입니다.", "error_description 을 메시지로", e.message)
        check(e.raw == gw, "raw 에 본문 원문")

    # ── ⑥ 알 수 없는 서식이어도 본문을 잃지 않는다 ────────────────────────
    print("\n═══ ⑥ 알 수 없는 서식 — 본문을 통째로 남긴다 ═══")
    odd = {"detail": "무언가 잘못됨", "trace": "abc"}
    install(odd, status=500)
    try:
        call("/x", {})
        check(False, "500 이면 예외가 나야 한다")
    except NhplugError as e:
        check("무언가 잘못됨" in (e.message or ""), "본문이 메시지에 포함", (e.message or "")[:40])
        check(e.raw == odd, "raw 에 본문 원문")

    # ── ⑦ 429 는 유량으로 분류하고 retry_after 를 보존한다 ────────────────
    print("\n═══ ⑦ 429 — 유량 분류 + retry_after 보존 ═══")
    install({"rsp_cd": "IGW42902", "rsp_msg": "호출 한도 초과"}, status=429,
            headers={"Retry-After": "2"})
    try:
        call("/x", {})
        check(False, "429 이면 예외가 나야 한다")
    except NhplugError as e:
        check(e.category == "rate_limit", "category=rate_limit", e.category)
        check(e.retry_after_ms == 2000, "retry_after 보존", str(e.retry_after_ms))
        check(e.retryable is True, "retryable=True")

    # ── ⑧ 제거된 판정 API 가 되살아나지 않았는지 ──────────────────────────
    print("\n═══ ⑧ 🔴 제거한 판정이 되살아나지 않았는가 ═══")
    for name in ("is_success", "success_codes", "DEFAULT_SUCCESS_CODES"):
        check(not hasattr(client, name), f"client.{name} 없음")
        check(not hasattr(nhplug, name), f"nhplug.{name} 없음")
    check("status_of" in nhplug.__all__, "status_of 는 공개 API")

    src = Path(client.__file__).read_text(encoding="utf-8")
    for token in ("00166", "00221", "13578", "NHPLUG_SUCCESS_CODES", 'category="business"'):
        check(token not in src, f"client.py 에 '{token}' 없음")

    errs = Path(nhplug.errors.__file__).read_text(encoding="utf-8")
    check('category: str = "business"' not in errs, "errors.py 기본 category 가 business 아님")

    print("\n" + "─" * 60)
    if FAILED:
        print(f"실패 {len(FAILED)}건: " + " · ".join(FAILED))
        sys.exit(1)
    print("전체 통과 ✅")


if __name__ == "__main__":
    main()
