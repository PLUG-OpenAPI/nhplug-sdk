"""REST 호출 공용 래퍼: 헤더·Input_0 봉투·토큰 자동 처리."""
import json
import os
import requests

from .auth import get_token, get_base_url


def call(path: str, input_0: dict | None = None, cts: str | None = None, timeout: int = 10) -> dict:
    """POST {BASE_URL}{path} 로 {"Input_0": input_0} 를 전송하고 응답 JSON 을 반환."""
    app_key = os.environ.get("NHPLUG_APP_KEY") or os.environ.get("APP_KEY")
    app_sec = os.environ.get("NHPLUG_APP_SECRET") or os.environ.get("APP_SECRET")
    headers = {
        "x-client-id": app_key,
        "x-client-secret": app_sec,
        "authorization": f"Bearer {get_token()}",
        "content-type": "application/json; charset=UTF-8",
    }
    if cts:
        headers["cts"] = cts
    body = {"Input_0": input_0 or {}}
    res = requests.post(f"{get_base_url()}{path}", headers=headers, data=json.dumps(body), timeout=timeout)
    res.raise_for_status()
    return res.json()
