"""접근 토큰 발급·캐시. NH 규약: POST /oauth2/token (쿼리파라미터, form-urlencoded)."""
import os
import time
import requests

_cache = {"token": None, "exp": 0.0}


def get_base_url() -> str:
    return os.environ.get("NHPLUG_BASE_URL", "https://devapi.nhplug.com:8443")


def _keys():
    app_key = os.environ.get("NHPLUG_APP_KEY") or os.environ.get("APP_KEY")
    app_sec = os.environ.get("NHPLUG_APP_SECRET") or os.environ.get("APP_SECRET")
    if not app_key or not app_sec:
        raise RuntimeError("NHPLUG_APP_KEY / NHPLUG_APP_SECRET(또는 APP_KEY/APP_SECRET) 환경변수가 필요합니다.")
    return app_key, app_sec


def get_token() -> str:
    """유효한 토큰이 캐시에 있으면 재사용, 없으면 발급."""
    now = time.time()
    if _cache["token"] and _cache["exp"] > now + 30:
        return _cache["token"]
    app_key, app_sec = _keys()
    url = f"{get_base_url()}/oauth2/token"
    params = {
        "appkey": app_key,
        "appsecretkey": app_sec,
        "grant_type": "client_credentials",
        "scope": "oob",
    }
    res = requests.post(url, params=params,
                        headers={"content-type": "application/x-www-form-urlencoded"}, timeout=10)
    res.raise_for_status()
    data = res.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"토큰 응답에 access_token 이 없습니다: {data}")
    _cache["token"] = token
    _cache["exp"] = now + int(data.get("expires_in", 600))
    return token
