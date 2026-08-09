"""접근 토큰 발급·캐시. NH 규약: POST /oauth2/token (쿼리파라미터, form-urlencoded).

토큰은 **24시간(expires_in=86400)** 유효하다. 재발급 1회 = 보안 알림 1건이므로
불필요한 재발급을 피해야 한다. 파이썬 스크립트는 실행할 때마다 새 프로세스라
메모리 캐시만으로는 매 실행 재발급되므로, **파일 캐시**로 프로세스 간 공유한다.

- 캐시 경로: ~/.nhplug/token-<해시>.json  (NHPLUG_TOKEN_CACHE_DIR 로 변경 가능)
- 해시 = sha256(앱키 + 인증URL) 앞 12자 → 브랜드(나무/N2)·계정별 분리. 앱키 원문은 저장하지 않음
- 파일 권한은 OS 기본값을 따른다(별도 chmod 없음). Windows·macOS·Linux 모두 동일 동작
- 끄기: NHPLUG_TOKEN_CACHE=0
- 재발급 조건은 **만료 또는 401(토큰 무효)** 뿐. 429(유량 초과)에는 재발급하지 않는다.
"""
import difflib
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

from .errors import NhplugError

# 프로세스 내 캐시(파일 캐시 앞단). scope 로 (앱키, 인증서버) 조합을 묶어
# 브랜드·키가 바뀌면 이전 토큰을 재사용하지 않는다.
_cache = {"token": None, "exp": 0.0, "scope": None}


def _host(url: str) -> str:
    return url.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0].lower()


def brand_of(url: str) -> str:
    """URL 이 어느 브랜드인지. 'nhplug'(나무) · 'n2plug' · 'unknown'."""
    host = _host(url)
    if host.endswith("nhplug.com"):
        return "nhplug"
    if host.endswith("n2plug.com"):
        return "n2plug"
    return "unknown"


def check_brand_consistency() -> str | None:
    """호출(BASE_URL)과 토큰(AUTH_URL)의 브랜드가 다르면 경고 문구를 돌려준다.

    나무 키를 N2 도메인에 쓰는(또는 그 반대) 설정 실수를 잡기 위한 것.
    두 파일(.env)에 나눠 적다가 한쪽만 바꾸면 조용히 어긋난다.
    """
    b_call, b_auth = brand_of(get_base_url()), brand_of(get_auth_url())
    if "unknown" in (b_call, b_auth) or b_call == b_auth:
        return None
    return (
        f"⚠️ 브랜드 불일치: 호출은 {b_call}({_host(get_base_url())}), "
        f"토큰은 {b_auth}({_host(get_auth_url())}) 입니다. "
        f"NHPLUG_BASE_URL·NHPLUG_AUTH_URL·NHPLUG_INSTRUMENTS_BASE 를 같은 브랜드로 맞추세요. "
        f"(설정 출처: nhplug.loaded_files())"
    )


# ---------------------------------------------------------------- 호스트 가드
# 🔒 앱키·시크릿이 나가는 URL 은 반드시 검증한다.
#    검증이 없으면 오타 한 글자로 자격증명이 엉뚱한 서버에 전송되거나,
#    모의투자로 알고 설정한 주소가 운영이라 실주문이 체결될 수 있다.
#    ⚠️ 호스트를 늘릴 때는 .env.example·README·MCP src/config.ts 도 함께 고칠 것.
ALLOWED_HOSTS = (
    "api.nhplug.com",      # 🔴 나무 운영 — 주문이 실제 체결됨
    "moapi.nhplug.com",    # 🟢 나무 모의투자
    "api.n2plug.com",      # 🔴 N2 운영 — 주문이 실제 체결됨
    "moapi.n2plug.com",    # 🟢 N2 모의투자
)
ALLOW_HOSTS_VAR = "NHPLUG_ALLOW_HOSTS"


def allowed_hosts() -> tuple[str, ...]:
    """허용 호스트 목록. 사내 검증 서버 등은 NHPLUG_ALLOW_HOSTS 에 쉼표로 추가한다."""
    extra = os.environ.get(ALLOW_HOSTS_VAR, "")
    return ALLOWED_HOSTS + tuple(h.strip().lower() for h in extra.split(",") if h.strip())


def _validate_url(url: str, var: str) -> str:
    """자격증명이 나가는 URL 을 검증하고 정규화한다(끝 슬래시 제거).

    포트는 검사하지 않는다 — 포트 오타는 접속 실패로 즉시 드러나지만,
    **호스트 오타는 자격증명이 그대로 전송된 뒤에야** 드러나기 때문이다.
    """
    u = (url or "").strip().rstrip("/")
    if not u:
        raise NhplugError(
            f"{var} 가 비어 있습니다. 예: https://api.nhplug.com:8443", category="config"
        )
    if not u.lower().startswith("https://"):
        raise NhplugError(
            f"{var} 는 https 여야 합니다 — 앱키·시크릿이 평문으로 전송됩니다: {u}",
            category="config",
        )
    if "/" in u.split("://", 1)[1]:
        raise NhplugError(
            f"{var} 에는 경로를 넣지 마세요(호스트까지만): {u}\n"
            f"  예: https://api.nhplug.com:8443",
            category="config",
        )
    host = _host(u)
    hosts = allowed_hosts()
    if host not in hosts:
        near = difflib.get_close_matches(host, hosts, n=1, cutoff=0.6)
        hint = f"\n  혹시 '{near[0]}' 인가요?" if near else ""
        raise NhplugError(
            f"{var} 의 호스트 '{host}' 는 허용되지 않습니다.{hint}\n"
            f"  허용: {', '.join(hosts)}\n"
            f"  사내 검증 서버라면 {ALLOW_HOSTS_VAR} 에 추가하세요 "
            f"(예: {ALLOW_HOSTS_VAR}=stg.example.com).",
            category="config",
        )
    return u


def get_base_url() -> str:
    """호출 대상 Base URL. 기본 운영(api). 교육·시뮬레이션은 moapi 로 설정.

    허용 호스트가 아니면 **호출 전에** NhplugError(category='config') 로 막는다.
    """
    return _validate_url(
        os.environ.get("NHPLUG_BASE_URL", "https://api.nhplug.com:8443"), "NHPLUG_BASE_URL"
    )


def get_auth_url() -> str:
    """토큰(/oauth2/token)은 운영(api) 전용 — moapi 미제공. 호출 대상과 무관하게 항상 api."""
    return _validate_url(
        os.environ.get("NHPLUG_AUTH_URL", "https://api.nhplug.com:8443"), "NHPLUG_AUTH_URL"
    )


def _cache_scope() -> str:
    """토큰이 유효한 범위 = (앱키, 인증서버). 값 자체는 남기지 않고 해시만 쓴다."""
    app_key, _ = _keys()
    return hashlib.sha256(f"{app_key}|{get_auth_url()}".encode("utf-8")).hexdigest()[:16]


def _keys():
    app_key = os.environ.get("NHPLUG_APP_KEY") or os.environ.get("APP_KEY")
    app_sec = os.environ.get("NHPLUG_APP_SECRET") or os.environ.get("APP_SECRET")
    if not app_key or not app_sec:
        raise NhplugError(
            "NHPLUG_APP_KEY / NHPLUG_APP_SECRET(또는 APP_KEY/APP_SECRET) 환경변수가 필요합니다.",
            category="auth",
        )
    return app_key, app_sec


# ---------------------------------------------------------------- 파일 캐시

def _cache_enabled() -> bool:
    return os.environ.get("NHPLUG_TOKEN_CACHE", "1").strip().lower() not in ("0", "false", "no")


def cache_path() -> Path:
    """토큰 캐시 파일 경로(디버깅·문서용으로 공개)."""
    base = os.environ.get("NHPLUG_TOKEN_CACHE_DIR")
    d = Path(base) if base else Path.home() / ".nhplug"
    app_key, _ = _keys()
    key = hashlib.sha256(f"{app_key}|{get_auth_url()}".encode("utf-8")).hexdigest()[:12]
    return d / f"token-{key}.json"


def _read_file_cache():
    if not _cache_enabled():
        return None
    try:
        data = json.loads(cache_path().read_text(encoding="utf-8"))
        token, exp = data.get("token"), float(data.get("exp", 0))
        if token and exp > time.time() + 60:
            return token, exp
    except Exception:
        pass  # 캐시 없음/손상/권한 → 무시하고 새로 발급
    return None


def _write_file_cache(token: str, exp: float) -> None:
    if not _cache_enabled():
        return
    try:
        p = cache_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps({"token": token, "exp": exp}), encoding="utf-8")
        os.replace(tmp, p)  # 원자적 교체(동시 실행 안전) — Windows·macOS·Linux 공통
    except Exception:
        pass  # 캐시 실패는 치명적이지 않음 — 메모리 캐시로 계속 동작


def clear_token() -> None:
    """토큰 캐시(메모리+파일)를 비운다. 401/IGW40043 응답 시 client 가 호출."""
    _cache["token"] = None
    _cache["exp"] = 0.0
    try:
        if _cache_enabled():
            cache_path().unlink(missing_ok=True)
    except Exception:
        pass


# ---------------------------------------------------------------- 토큰 발급

def get_token(force: bool = False) -> str:
    """유효한 토큰이 있으면 재사용, 없거나 force 면 재발급.

    조회 순서: 메모리 캐시 → 파일 캐시 → 신규 발급.
    force=True 는 **401(토큰 무효)** 일 때만 사용한다. 429 재시도에는 쓰지 않는다.
    """
    now = time.time()
    # 🔒 메모리 캐시는 (앱키, 인증서버) 조합에 묶는다.
    #    한 프로세스에서 브랜드(나무↔N2)나 키를 바꿔도 이전 토큰이 재사용되지 않도록.
    scope = _cache_scope()
    if _cache["scope"] != scope:
        _cache["token"], _cache["exp"], _cache["scope"] = None, 0.0, scope

    if not force:
        if _cache["token"] and _cache["exp"] > now + 30:
            return _cache["token"]
        cached = _read_file_cache()
        if cached:
            _cache["token"], _cache["exp"] = cached
            return _cache["token"]

    app_key, app_sec = _keys()
    warn = check_brand_consistency()
    if warn:  # 잘못된 브랜드 조합으로 키가 나가기 전에 알린다
        print(warn, file=sys.stderr)
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
                raise NhplugError(f"토큰 응답에 access_token 이 없습니다: {data}",
                                  category="auth", status=200, raw=data)
            exp = now + int(data.get("expires_in", 86400))  # 기본 24h
            _cache["token"], _cache["exp"] = token, exp
            _write_file_cache(token, exp)
            return token

        last = f"HTTP {res.status_code} — {res.text[:300]}"
        # 인증 서버 일시장애(IGW40054)만 짧게 재시도. 키 오류 등은 즉시 실패.
        if "IGW40054" in res.text and attempt < 2:
            time.sleep(0.4 * (attempt + 1))
            continue
        raise NhplugError(f"토큰 발급 실패 (인증서버 {get_auth_url()}, 운영 전용): {last}",
                          category="auth", status=res.status_code, raw=res.text)

    raise NhplugError(f"토큰 발급 실패 (재시도 후에도): {last}", category="auth")
