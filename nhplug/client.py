"""REST 호출 공용 래퍼: 헤더·Input_0 봉투·토큰 자동 처리."""
import json
import os
import re
import requests

from .auth import get_token, get_base_url, clear_token

_INVALID_TOKEN_RE = re.compile(r"유효하지\s*않은\s*token", re.IGNORECASE)


def _is_invalid_token(status: int, text: str) -> bool:
    """토큰 무효 신호만 좁게 판별(재발급 후 재시도 대상). 일반 400(IGW40024 등)은 제외."""
    if status == 401:
        return True
    return "IGW40043" in text or bool(_INVALID_TOKEN_RE.search(text))


def call(path: str, input_0: dict | None = None, cts: str | None = None, timeout: int = 10) -> dict:
    """POST {BASE_URL}{path} 로 {"Input_0": input_0} 를 전송하고 응답 JSON 을 반환.

    토큰이 무효(IGW40043/401)면 재발급 후 1회 재시도한다.
    """
    app_key = os.environ.get("NHPLUG_APP_KEY") or os.environ.get("APP_KEY")
    app_sec = os.environ.get("NHPLUG_APP_SECRET") or os.environ.get("APP_SECRET")
    url = f"{get_base_url()}{path}"
    body = json.dumps({"Input_0": input_0 or {}})

    res = None
    for attempt in range(2):
        headers = {
            "x-client-id": app_key,
            "x-client-secret": app_sec,
            "authorization": f"Bearer {get_token(force=attempt == 1)}",
            "content-type": "application/json; charset=UTF-8",
        }
        if cts:
            headers["cts"] = cts

        res = requests.post(url, headers=headers, data=body, timeout=timeout)
        if res.ok:
            return res.json()

        # 토큰 무효면 캐시 비우고 1회 재시도, 그 외 오류는 즉시 중단
        if attempt == 0 and _is_invalid_token(res.status_code, res.text):
            clear_token()
            continue
        break

    res.raise_for_status()
    return res.json()
