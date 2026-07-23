"""접근 토큰 발급·캐시. NH 규약: POST /oauth2/token (쿼리파라미터, form-urlencoded)."""
import os
import time
import requests

_cache = {"token": None, "exp": 0.0}


def get_base_url() -> str:
    """호출 대상 Base URL. 기본 운영(api). 교육·시뮬레이션은 moapi 로 설정."""
    return os.environ.get("NHPLUG_BASE_URL", "https://api.nhplug.com:8443")


def get_auth_url() -> str:
    """토큰(/oauth2/token)은 운영(api) 전용 — moapi 미제공. 호출 대상과 무관하게 항상 api."""
    return os.environ.get("NHPLUG_AUTH_URL", "https://api.nhplug.com:8443")


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
    url = f"{get_auth_url()}/oauth2/token"
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
