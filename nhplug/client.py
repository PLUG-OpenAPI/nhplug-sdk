"""REST 호출 공용 래퍼: 헤더·Input_0 봉투·토큰·업무성공(rsp_cd) 판정.

핵심 규약: **HTTP 200 ≠ 업무 성공.** 응답 봉투의 `rsp_cd` 가 성공 코드가 아니면 실패다.
성공 코드는 기본 00000·00166 이며 NHPLUG_SUCCESS_CODES 로 확장할 수 있다.
"""
import json
import os
import re

import requests

from .auth import get_token, get_base_url, clear_token
from .errors import NhplugError

_INVALID_TOKEN_RE = re.compile(r"유효하지\s*않은\s*token", re.IGNORECASE)

#: 업무 성공으로 간주하는 rsp_cd. 필요 시 NHPLUG_SUCCESS_CODES=00000,00166,XXXXX 로 확장.
DEFAULT_SUCCESS_CODES = ("00000", "00166")


def success_codes() -> set[str]:
    env = os.environ.get("NHPLUG_SUCCESS_CODES")
    if env:
        return {c.strip() for c in env.split(",") if c.strip()}
    return set(DEFAULT_SUCCESS_CODES)


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


def call(path: str, input_0: dict | None = None, cts: str | None = None,
         timeout: int = 10, raise_on_error: bool = True) -> dict:
    """POST {BASE_URL}{path} 로 {"Input_0": input_0} 전송 후 응답 JSON 반환.

    - 토큰이 무효(401/IGW40043)면 1회 재발급 후 재시도한다.
    - 429(유량 초과)는 **자동 재시도하지 않고** rate_limit 오류로 올린다(코드·retry_after 보존).
    - HTTP 200 이어도 rsp_cd 가 성공 코드가 아니면 NhplugError(category="business").
    - raise_on_error=False 면 예외 없이 서버 원본 응답을 그대로 돌려준다(구버전 호환).
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
        return data

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
        if rsp_cd is not None and str(rsp_cd) not in success_codes():
            raise NhplugError(
                data.get("rsp_msg") or "업무 오류",
                category="business", code=str(rsp_cd), status=200, path=path,
                environment=get_base_url(), raw=data,
            )
    return data
