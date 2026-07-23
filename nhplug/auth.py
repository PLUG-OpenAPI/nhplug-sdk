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


def clear_token() -> None:
    """토큰 캐시를 비운다(다음 get_token 호출 시 강제 재발급). 토큰 무효(IGW40043) 응답 시 client 가 호출."""
    _cache["token"] = None
    _cache["exp"] = 0.0


def get_token(force: bool = False) -> str:
    """유효한 토큰이 캐시에 있으면 재사용, 없거나 force 면 재발급.

    토큰 발급 일시장애(IGW40054 등)에는 짧게 재시도한다.
    유효하지 않은 AppKey(IGW40031)는 즉시 실패한다.
    """
    now = time.time()
    if not force and _cache["token"] and _cache["exp"] > now + 30:
        return _cache["token"]

    app_key, app_sec = _keys()
    url = f"{get_auth_url()}/oauth2/token"
    params = {
        "appkey": app_key,
        "appsecretkey": app_sec,
        "grant_type": "client_credentials",
        "scope": "oob",
    }

    last = ""
    for attempt in range(3):
        try:
            res = requests.post(
                url, params=params,
                headers={"content-type": "application/x-www-form-urlencoded"}, timeout=10,
            )
        except requests.RequestException as e:
            last = f"네트워크 오류 — {e}"
            time.sleep(0.3 * (attempt + 1))
            continue

        if res.status_code == 200:
            data = res.json()
            token = data.get("access_token")
            if not token:
                raise RuntimeError(f"토큰 응답에 access_token 이 없습니다: {data}")
            _cache["token"] = token
            # expires_in(초)이 오면 사용, 없으면 24h. 무효 응답 시 client 자동 재발급이 안전망.
            _cache["exp"] = now + int(data.get("expires_in", 86400))
            return token

        last = f"HTTP {res.status_code} — {res.text[:300]}"
        # 일시장애면 재시도, 그 외(키 오류 등)는 즉시 실패
        if "IGW40054" in res.text and attempt < 2:
            time.sleep(0.4 * (attempt + 1))
            continue
        raise RuntimeError(f"토큰 발급 실패 (인증서버 {get_auth_url()}, 운영 전용): {last}")

    raise RuntimeError(f"토큰 발급 실패 (재시도 후에도): {last}")
