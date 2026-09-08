"""REST 호출 공용 래퍼: 헤더·Input_0 봉투·토큰·업무성공(rsp_cd) 판정·연속조회·유량 제어.

🔴 업무오류 판정: **HTTP 200 ≠ 업무 성공.** 그리고 **rsp_cd 만으로는 판정할 수 없다** —
**같은 rsp_cd 값이 API 에 따라 정상일 수도 오류일 수도 있다.** 판정은 **rsp_msg 내용이 우선**이며
규약 정본은 도메인 llms.txt 다.

아래 is_success() 는 라이브에서 관찰된 코드 목록 + "완료" 메시지로 하는 **1차 판정**이며 전수가 아니다.
호출자가 직접 확인해야 하는 중요한 처리에서는 raise_on_error=False 로 원본을 받아 rsp_msg 를 본다.
⚠️ 판정 기준(rsp_msg 우선 규칙)이 llms.txt 에 확정되면 이 함수를 그에 맞춰 교체할 것.

연속조회(cts): `cts`·`cts_flag` 는 **응답 헤더**로 내려온다. `call()` 은 기본적으로 본문만
돌려주므로 헤더가 필요하면 `want_meta=True` 를 쓰거나, 전체 순회는 `paginate()` 를 쓴다.

유량: 실측 한도가 초당 5회 수준이라 **기본 4회/초로 자동 스로틀**한다(NHPLUG_RATE_LIMIT).
"""
import json
import os
import re
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass, field as dc_field

import requests

from .auth import get_token, get_base_url, clear_token
from .errors import NhplugError

_INVALID_TOKEN_RE = re.compile(r"유효하지\s*않은\s*token", re.IGNORECASE)

#: 라이브에서 **정상 응답으로 관찰된** rsp_cd — 판정 기준이 아니라 참고용 표본이다.
#:   00000 현재가·계좌목록 / 00166 잔고·자산현황·손익 / 00221 매수가능수량 / 13578 조회 내역 없음(빈 결과)
#: ⚠️ 같은 코드가 다른 API 에서는 오류를 뜻할 수 있다. 전수 목록이 아니며 앞으로도 될 수 없다.
#: 필요 시 NHPLUG_SUCCESS_CODES=... 로 1차 판정 기준을 바꿀 수 있다.
DEFAULT_SUCCESS_CODES = ("00000", "00166", "00221", "13578")

#: 성공 메시지 안전망. NH 성공 응답은 일관되게 "…완료되었습니다" 형태다.
#: allowlist 에 없는 미지의 정상코드를 실패로 오판하지 않기 위한 2차 방어.
_SUCCESS_MSG_RE = re.compile(r"완료")


def success_codes() -> set[str]:
    env = os.environ.get("NHPLUG_SUCCESS_CODES")
    if env:
        return {c.strip() for c in env.split(",") if c.strip()}
    return set(DEFAULT_SUCCESS_CODES)


def is_success(rsp_cd: str | None, rsp_msg: str | None = None) -> bool:
    """업무 성공 **1차 판정**. 관찰된 코드 목록에 있거나 메시지에 '완료'가 있으면 성공으로 본다.

    🔴 이것은 전수 판정이 아니다. rsp_cd 는 API 마다 의미가 달라 단독 기준이 될 수 없고,
       정확한 판정은 rsp_msg 내용을 봐야 한다(규약 정본: 도메인 llms.txt).
    """
    if rsp_cd is None:
        return True  # 봉투에 rsp_cd 가 없는 응답(토큰 등)은 판정 대상 아님
    if str(rsp_cd) in success_codes():
        return True
    return bool(rsp_msg and _SUCCESS_MSG_RE.search(rsp_msg))


# ---------------------------------------------------------------- 유량 스로틀
#: 실측 한도는 **초당 5회** 수준(초과 시 429 / IGW42902). 여유를 두고 기본 4회로 제한한다.
DEFAULT_RATE_LIMIT = 4.0
#: 사용자가 실측 한도를 넘겨 설정하지 못하도록 하는 상한. 넘기면 이 값으로 깎는다.
MAX_RATE_LIMIT = 5.0
RATE_LIMIT_VAR = "NHPLUG_RATE_LIMIT"

_rate_lock = threading.Lock()
_rate_calls: deque[float] = deque()   # 최근 1초 창 안의 호출 시각
_rate_warned = False


def rate_limit() -> float:
    """초당 허용 호출 수. `NHPLUG_RATE_LIMIT` 로 조정하며 0 이면 스로틀을 끈다.

    ⚠️ 끄거나 상한을 넘기면 429(IGW42902)가 난다. 상한 초과 값은 MAX_RATE_LIMIT 로 깎는다.
    """
    global _rate_warned
    raw = (os.environ.get(RATE_LIMIT_VAR) or "").strip()
    if not raw:
        return DEFAULT_RATE_LIMIT
    try:
        v = float(raw)
    except ValueError:
        return DEFAULT_RATE_LIMIT
    if v <= 0:
        return 0.0                      # 명시적으로 끔(테스트·오프라인용)
    if v > MAX_RATE_LIMIT:
        if not _rate_warned:
            print(f"⚠️ {RATE_LIMIT_VAR}={v} 는 실측 한도(초당 {MAX_RATE_LIMIT:g}회)를 넘습니다. "
                  f"{MAX_RATE_LIMIT:g} 로 제한합니다.", file=sys.stderr)
            _rate_warned = True
        return MAX_RATE_LIMIT
    return v


def _throttle() -> None:
    """슬라이딩 1초 창. 창 안의 호출이 한도에 닿으면 가장 오래된 호출이 빠질 때까지 잔다."""
    limit = rate_limit()
    if limit <= 0:
        return
    while True:
        with _rate_lock:
            now = time.monotonic()
            while _rate_calls and now - _rate_calls[0] >= 1.0:
                _rate_calls.popleft()
            if len(_rate_calls) < limit:
                _rate_calls.append(now)
                return
            wait = 1.0 - (now - _rate_calls[0])
        time.sleep(max(wait, 0.001))


def _is_invalid_token(status: int, text: str) -> bool:
    """토큰 무효 신호만 좁게 판별(재발급 대상). 일반 400(IGW40024 등)·429 는 제외."""
    if status == 401:
        return True
    return "IGW40043" in text or bool(_INVALID_TOKEN_RE.search(text))


def _retry_after_ms(res) -> int | None:
    v = res.headers.get("Retry-After")
    if not v:
        return None
    try:
        return int(float(v) * 1000)
    except ValueError:
        return None


def _parse(res):
    """응답을 dict 로 파싱(실패 시 원문 문자열)."""
    try:
        return res.json()
    except Exception:
        return res.text


# ---------------------------------------------------------------- 연속조회(cts)
#: `cts_flag` 헤더가 없을 때 "다음 페이지가 있다"로 보는 업무코드(실측).
CONTINUE_CODES = ("00165", "00218")

#: 응답 **본문**의 연속조회키 필드명. 자산군마다 자릿수가 달라 접미 숫자가 붙는다.
#:   실측 확인: ctsz16(gbstock 기간별) · ctsz18(해외 체결추이) · ctsz20(국내 체결) · ctsz30(기간별)
#: ⚠️ 헤더(cts)와 본문(ctsz*) 중 어느 쪽으로 오는지는 API 마다 다르다 —
#:    명세는 본문, 실측은 헤더였다. **둘 다 본다.**
_CTS_BODY_RE = re.compile(r"^cts(?:z\d+)?$", re.IGNORECASE)


def _body_cts(data) -> str | None:
    """응답 본문의 `Output_*` 안에서 연속조회키(`ctsz16`·`ctsz30` 등)를 찾는다."""
    if not isinstance(data, dict):
        return None
    found = None
    for key, block in data.items():
        if not key.startswith("Output"):
            continue
        for row in (block if isinstance(block, list) else [block]):
            if not isinstance(row, dict):
                continue
            for k, v in row.items():
                if _CTS_BODY_RE.match(k) and str(v or "").strip():
                    found = str(v).strip()      # 뒤쪽 레코드 값이 최신
    return found


@dataclass
class Meta:
    """응답 부가정보. 연속조회 키는 **응답 헤더 또는 본문**으로 내려온다.

    Attributes:
        cts:        다음 페이지 요청에 그대로 실어 보낼 연속조회 키.
        cts_flag:   "Y"=다음 페이지 있음 / "N"=마지막. 내려오지 않는 API 도 있다.
        cts_source: 키를 어디서 찾았는지 — "header" · "body" · None.
        status:     HTTP 상태코드.
        rsp_cd:     업무 코드.
        rsp_msg:    업무 메시지.
        headers:    응답 헤더 전체(소문자 키).
    """
    cts: str | None = None
    cts_flag: str | None = None
    cts_source: str | None = None
    status: int | None = None
    rsp_cd: str | None = None
    rsp_msg: str | None = None
    headers: dict = dc_field(default_factory=dict)

    @property
    def has_next(self) -> bool:
        """다음 페이지가 있는지. `paginate()` 가 쓰는 판정과 동일하다.

        - `cts` 가 비어 있으면 더 보낼 키가 없으므로 끝.
        - `cts_flag` 가 "N" 이면 끝, "Y" 면 계속.
        - `cts_flag` 가 없을 때:
            · 키를 **본문**에서 찾았으면 계속(본문 연속키는 값이 있으면 다음이 있다는 뜻).
            · 키가 **헤더**로 왔으면 `rsp_cd` 가 CONTINUE_CODES 일 때만 계속.

        ⚠️ 여기서는 "직전 cts 와 같은지"를 알 수 없다. 무한루프 방지는 `paginate()` 가 한다.
        """
        if not self.cts:
            return False
        flag = (self.cts_flag or "").strip().upper()
        if flag == "N":
            return False
        if flag == "Y":
            return True
        if self.cts_source == "body":
            return True
        return str(self.rsp_cd) in CONTINUE_CODES


def _meta_of(res, data) -> Meta:
    h = {k.lower(): v for k, v in getattr(res, "headers", {}).items()}
    cts = (h.get("cts") or "").strip() or None
    source = "header" if cts else None
    if not cts:                       # 헤더에 없으면 본문 ctsz* 로 폴백
        cts = _body_cts(data)
        source = "body" if cts else None
    return Meta(
        cts=cts,
        cts_flag=(h.get("cts_flag") or "").strip() or None,
        cts_source=source,
        status=getattr(res, "status_code", None),
        rsp_cd=str(data.get("rsp_cd")) if isinstance(data, dict) and data.get("rsp_cd") is not None else None,
        rsp_msg=data.get("rsp_msg") if isinstance(data, dict) else None,
        headers=h,
    )


def call(path: str, input_0: dict | None = None, cts: str | None = None,
         timeout: int = 10, raise_on_error: bool = True,
         cts_flag: str | None = None, want_meta: bool = False):
    """POST {BASE_URL}{path} 로 {"Input_0": input_0} 전송 후 응답 JSON 반환.

    - 토큰이 무효(401/IGW40043)면 1회 재발급 후 재시도한다.
    - 429(유량 초과)는 **자동 재시도하지 않고** rate_limit 오류로 올린다(코드·retry_after 보존).
      호출 전 자동 스로틀(기본 초당 4회)이 걸리므로 정상 사용에서는 잘 나지 않는다.
    - HTTP 200 이어도 업무 오류면 NhplugError(category="business"). **1차 판정이며 전수가 아니다** —
      rsp_cd 는 API 마다 의미가 다르므로 중요한 처리는 rsp_msg 를 직접 확인한다.
    - raise_on_error=False 면 예외 없이 서버 원본 응답을 그대로 돌려준다(구버전 호환).

    Args:
        cts: 연속조회 키. **직전 응답의 `Meta.cts`** 를 그대로 넣는다.
        cts_flag: 직전 응답의 `Meta.cts_flag`. 서버가 요구하는 API 를 위해 함께 보낸다.
        want_meta: True 면 `(data, Meta)` 튜플을 반환한다. 기본 False 라 기존 코드는 그대로 동작.

    Returns:
        `want_meta=False`(기본) → 응답 본문(dict)
        `want_meta=True`       → `(본문, Meta)` — `Meta.cts`·`Meta.cts_flag`·`Meta.has_next`
    """
    app_key = os.environ.get("NHPLUG_APP_KEY") or os.environ.get("APP_KEY")
    app_sec = os.environ.get("NHPLUG_APP_SECRET") or os.environ.get("APP_SECRET")
    url = f"{get_base_url()}{path}"
    body = json.dumps({"Input_0": input_0 or {}})

    force_token = False  # 401 일 때만 True. 429 등 다른 오류에는 절대 재발급하지 않는다.
    res = None
    for attempt in range(2):
        headers = {
            "x-client-id": app_key,
            "x-client-secret": app_sec,
            "authorization": f"Bearer {get_token(force=force_token)}",
            "content-type": "application/json; charset=UTF-8",
        }
        if cts:
            headers["cts"] = cts
        if cts_flag:
            headers["cts_flag"] = cts_flag

        _throttle()   # 슬라이딩 1초 창. 재시도(토큰 재발급)도 한 건으로 센다.
        try:
            res = requests.post(url, headers=headers, data=body, timeout=timeout)
        except requests.RequestException as e:
            if raise_on_error:
                raise NhplugError(f"네트워크 오류: {e}", category="network",
                                  path=path, environment=get_base_url(), retryable=True) from e
            raise

        if res.ok:
            break
        # 토큰 무효면 캐시 비우고 1회만 재발급 재시도
        if attempt == 0 and _is_invalid_token(res.status_code, res.text):
            clear_token()
            force_token = True
            continue
        break

    data = _parse(res)
    if not raise_on_error:
        return (data, _meta_of(res, data)) if want_meta else data

    # ---- HTTP 오류 ----
    if not res.ok:
        rsp_cd = data.get("rsp_cd") if isinstance(data, dict) else None
        rsp_msg = data.get("rsp_msg") if isinstance(data, dict) else None
        if res.status_code == 429:
            raise NhplugError(
                rsp_msg or "호출 유량을 초과했습니다. 호출 간격을 늘리세요.",
                category="rate_limit", code=rsp_cd or "IGW42902", status=429, path=path,
                retryable=True, retry_after_ms=_retry_after_ms(res),
                environment=get_base_url(), raw=data,
            )
        if _is_invalid_token(res.status_code, res.text):
            raise NhplugError(rsp_msg or "인증 실패(토큰 무효).", category="auth",
                              code=rsp_cd, status=res.status_code, path=path,
                              environment=get_base_url(), raw=data)
        raise NhplugError(rsp_msg or f"HTTP {res.status_code}", category="http",
                          code=rsp_cd, status=res.status_code, path=path,
                          environment=get_base_url(), raw=data)

    # ---- HTTP 200 이지만 업무 오류(rsp_cd) ----
    if isinstance(data, dict):
        rsp_cd = data.get("rsp_cd")
        if not is_success(rsp_cd, data.get("rsp_msg")):
            raise NhplugError(
                data.get("rsp_msg") or "업무 오류",
                category="business", code=str(rsp_cd), status=200, path=path,
                environment=get_base_url(), raw=data,
            )
    return (data, _meta_of(res, data)) if want_meta else data


def paginate(path: str, input_0: dict | None = None, *, max_pages: int | None = None,
             timeout: int = 10, want_meta: bool = False):
    """연속조회를 끝까지 순회하는 제너레이터. 페이지마다 응답 본문을 내보낸다.

    종료 판정(실측 기준):
      - `cts_flag == "N"`  → 종료
      - `cts_flag == "Y"`  → 계속
      - `cts_flag` 헤더가 없고 `rsp_cd` 가 00165·00218 → 계속
      - `cts` 가 비면 종료
      - 🔴 **`cts` 가 직전과 같으면 즉시 종료** — 서버가 진행하지 않는 것이므로 무한루프가 된다.
        정상 연속조회는 매번 바뀌지만 **끝 2~3자만 다른 경우**가 있어 전체 문자열로 비교한다.

    Args:
        max_pages: 이 페이지 수만큼만 가져온다. None 이면 끝까지.
        want_meta: True 면 `(본문, Meta)` 튜플을 내보낸다.

    사용:
        for page in paginate("/krstock/…", {"act_no": "…"}, max_pages=20):
            for row in page.get("Output_0", []):
                ...

    호출 간격은 `call()` 의 자동 스로틀(기본 초당 4회)이 처리하므로 따로 sleep 하지 않아도 된다.
    """
    cts = cts_flag = None
    seen: set[str] = set()
    page = 0
    while True:
        data, meta = call(path, input_0, cts=cts, cts_flag=cts_flag,
                          timeout=timeout, want_meta=True)
        yield (data, meta) if want_meta else data
        page += 1
        if max_pages is not None and page >= max_pages:
            return
        if not meta.has_next:
            return
        # 🔴 무한루프 방지 — 같은 키를 다시 보내면 서버가 같은 페이지를 계속 준다.
        if meta.cts in seen:
            return
        seen.add(meta.cts)
        cts, cts_flag = meta.cts, meta.cts_flag
