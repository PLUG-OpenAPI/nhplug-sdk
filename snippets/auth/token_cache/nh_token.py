"""
NH투자증권 Open API — Access Token 전역 캐시 모듈
=================================================

📌 이 파일은 **SDK 를 쓰지 않고 직접 개발하시는 분**을 위한 참고 구현입니다.
   `pip install nhplug` 을 쓰시면 아래 내용이 이미 들어 있어 직접 작성할 필요가 없습니다.
       from nhplug import call
       call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})

   정본: https://github.com/PLUG-OpenAPI/nhplug-sdk/blob/main/snippets/auth/token_cache/nh_token.py

⚠️ 왜 필요한가
  토큰은 **재발급을 요청할 때마다 새로 발급**되고, 그때마다 알림톡이 발송됩니다.
  스크립트는 실행할 때마다 새 프로세스라, 메모리에만 담아두면 **매 실행마다 재발급**됩니다.
  → 파일에 저장해 두고 24시간 동안 재사용하면 알림톡이 하루 1건으로 줄어듭니다.

✅ 이 모듈이 하는 일
  1. 발급받은 토큰을 token_cache.json 에 저장
  2. 만료 전이면 파일에서 읽어 재사용 (프로세스가 바뀌어도 유지)
  3. 만료됐거나 401(토큰 무효)일 때만 재발급
  4. 429(호출 한도 초과)에는 **재발급하지 않음** ← 알림톡 폭증의 가장 흔한 원인

사용법
  pip install requests

  # .env 또는 환경변수에 앱키·시크릿을 넣고
  from nh_token import get_token, api_post

  data = api_post("/krstock/quote/v1/currentPrice",
                  {"iem_cd": "005930", "market_cd": "KRX"})
  print(data["Output_0"]["stck_prpr"])

문의: apisupport@nhsec.com
"""
import json
import os
import time
from pathlib import Path

import requests

# ─────────────────────────────────────────────────────────────
# 설정 — 앱키·시크릿은 코드에 넣지 말고 환경변수로 관리하세요
# ─────────────────────────────────────────────────────────────
APP_KEY = os.environ.get("NHPLUG_APP_KEY", "")
APP_SECRET = os.environ.get("NHPLUG_APP_SECRET", "")

# 나무(Namuh) 고객: nhplug.com   ·   N2 고객: n2plug.com  (아래 두 줄을 모두 교체)
BASE_URL = os.environ.get("NHPLUG_BASE_URL", "https://api.nhplug.com:8443")   # 호출 대상
AUTH_URL = os.environ.get("NHPLUG_AUTH_URL", "https://api.nhplug.com:8443")   # 토큰 발급

# ⚠️ 토큰 발급은 운영(api) 전용입니다. 모의투자(moapi)로 호출하더라도
#    AUTH_URL 은 api 로 두어야 합니다.

CACHE_FILE = Path(os.environ.get("NHPLUG_TOKEN_CACHE",
                                 Path.home() / ".nhplug" / "token_cache.json"))
EXPIRE_MARGIN = 60          # 만료 60초 전에는 미리 재발급 (경계 오류 방지)
TIMEOUT = 10

_memory = {"token": None, "exp": 0.0}   # 같은 프로세스 안에서는 파일도 안 읽음


# ─────────────────────────────────────────────────────────────
# 파일 캐시
# ─────────────────────────────────────────────────────────────
def _read_cache():
    """저장된 토큰이 아직 유효하면 (토큰, 만료시각) 을 돌려준다."""
    try:
        d = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if d.get("base") != AUTH_URL or d.get("key") != APP_KEY[:8]:
            return None                       # 브랜드·계정이 바뀌면 재사용 금지
        if float(d["exp"]) > time.time() + EXPIRE_MARGIN:
            return d["token"], float(d["exp"])
    except Exception:
        pass                                  # 파일 없음·손상 → 새로 발급
    return None


def _write_cache(token: str, exp: float) -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps({
            "token": token, "exp": exp,
            "base": AUTH_URL, "key": APP_KEY[:8],   # 식별용 앞 8자리만
        }), encoding="utf-8")
        os.replace(tmp, CACHE_FILE)           # 원자적 교체 — 동시 실행 안전
    except Exception:
        pass                                  # 캐시 실패는 치명적이지 않음


# ─────────────────────────────────────────────────────────────
# 토큰 발급
# ─────────────────────────────────────────────────────────────
def get_token(force: bool = False) -> str:
    """유효한 토큰을 돌려준다. 없거나 force=True 일 때만 새로 발급.

    force 는 **401(토큰 무효)** 일 때만 쓰세요.
    429(호출 한도 초과) 재시도에는 절대 쓰지 마세요 — 알림톡이 계속 발송됩니다.
    """
    if not force:
        if _memory["token"] and _memory["exp"] > time.time() + EXPIRE_MARGIN:
            return _memory["token"]           # ① 메모리
        cached = _read_cache()
        if cached:
            _memory["token"], _memory["exp"] = cached
            return cached[0]                  # ② 파일 (프로세스가 바뀌어도 유지)

    if not APP_KEY or not APP_SECRET:
        raise RuntimeError("환경변수 NHPLUG_APP_KEY / NHPLUG_APP_SECRET 이 필요합니다.")

    # ③ 신규 발급 — 이때 알림톡이 발송됩니다 (하루 1회면 정상)
    res = requests.post(
        f"{AUTH_URL}/oauth2/token",
        params={
            "appkey": APP_KEY,
            "appsecretkey": APP_SECRET,
            "grant_type": "client_credentials",
            "scope": "oob",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
        timeout=TIMEOUT,
    )
    res.raise_for_status()
    body = res.json()

    token = body.get("access_token")
    if not token:
        raise RuntimeError(f"토큰 응답에 access_token 이 없습니다: {body}")

    exp = time.time() + int(body.get("expires_in", 86400))   # 기본 24시간
    _memory["token"], _memory["exp"] = token, exp
    _write_cache(token, exp)
    return token


# ─────────────────────────────────────────────────────────────
# API 호출 — 토큰 무효(401)일 때만 1회 재발급 후 재시도
# ─────────────────────────────────────────────────────────────
SUCCESS_CODES = {"00000", "00166", "00221", "13578"}


def api_post(path: str, input_0: dict | None = None, cts: str | None = None) -> dict:
    """POST {BASE_URL}{path} 로 {"Input_0": ...} 를 보내고 응답 JSON 을 돌려준다."""
    force = False
    for attempt in range(2):
        headers = {
            "content-type": "application/json; charset=utf-8",
            "x-client-id": APP_KEY,
            "x-client-secret": APP_SECRET,
            "authorization": f"Bearer {get_token(force=force)}",
        }
        if cts:
            headers["cts"] = cts

        res = requests.post(f"{BASE_URL}{path}",
                            headers=headers,
                            data=json.dumps({"Input_0": input_0 or {}}).encode("utf-8"),
                            timeout=TIMEOUT)

        # 토큰이 무효일 때만 1회 재발급 후 재시도
        if attempt == 0 and (res.status_code == 401 or "IGW40043" in res.text):
            CACHE_FILE.unlink(missing_ok=True)
            _memory["token"], _memory["exp"] = None, 0.0
            force = True
            continue

        # ⚠️ 429(IGW42902, 호출 한도 초과)는 토큰 문제가 아닙니다.
        #    여기서 재발급하면 알림톡만 쌓입니다. 잠시 쉬었다가 다시 호출하세요.
        if res.status_code == 429:
            raise RuntimeError("호출 한도 초과(429). 호출 간격을 늘려 주세요. "
                               "※ 토큰을 재발급하지 마세요.")
        break

    res.raise_for_status()
    data = res.json()

    # HTTP 200 이어도 업무 오류일 수 있습니다
    rsp_cd, rsp_msg = data.get("rsp_cd"), data.get("rsp_msg", "")
    if rsp_cd is not None and rsp_cd not in SUCCESS_CODES and "완료" not in rsp_msg:
        raise RuntimeError(f"업무 오류 [{rsp_cd}] {rsp_msg}")
    return data


# ─────────────────────────────────────────────────────────────
# 동작 확인
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 🔒 토큰 값은 일부라도 출력하지 마세요(화면 공유·로그로 유출될 수 있습니다)
    tok = get_token()
    print(f"토큰 준비 완료 (길이 {len(tok)}자) · 캐시: {CACHE_FILE}")

    data = api_post("/krstock/quote/v1/currentPrice",
                    {"iem_cd": "005930", "market_cd": "KRX"})
    out = data.get("Output_0", {})
    print(f"삼성전자 현재가: {out.get('stck_prpr'):,}원")

    # 두 번째 호출은 캐시를 쓰므로 재발급이 일어나지 않습니다 (알림톡 없음)
    api_post("/n2/acctinfo", {})
    print("두 번째 호출 완료 — 재발급 없음 ✅")
