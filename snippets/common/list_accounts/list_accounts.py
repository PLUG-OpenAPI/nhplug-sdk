"""계좌 목록 조회 (POST /n2/acctinfo). 응답 Output_0[].acct_no · acct_type.

⚠️ 중요 — acct_type 은 이 계좌를 쓸 수 있는 **환경**을 결정한다.
    01 · 02 → 🔴 운영(api)      03 → 🟢 모의투자(moapi)
계좌 목록에는 여러 구분이 섞여 내려온다. **호출 환경과 같은 구분의 계좌를 골라야** 한다
(운영 도메인에 03 계좌를, 모의투자 도메인에 01·02 계좌를 쓰면 실패한다).

사용:
    from list_accounts import list_accounts, accounts, usable_accounts

    accounts()          # [{acct_no, acct_type, env, desc, usable}, ...]
    usable_accounts()   # 현재 NHPLUG_BASE_URL 환경에서 쓸 수 있는 계좌만
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call, get_base_url

# acct_type → (환경, 설명)
ACCT_TYPES = {
    "01": ("live", "운영 (일반)"),
    "02": ("live", "운영 (주문대리인)"),
    "03": ("mock", "모의투자"),
}


def list_accounts() -> dict:
    """원본 응답 그대로 반환."""
    return call("/n2/acctinfo", {})


def current_env(base_url: str | None = None) -> str:
    """지금 호출 대상 환경. 'live' | 'mock' | 'unknown'

    moapi 호스트면 모의투자, api 호스트면 운영. (브랜드 nhplug/n2plug 무관)
    """
    host = (base_url or get_base_url()).split("//")[-1].split("/")[0].lower()
    if host.startswith("moapi."):
        return "mock"
    if host.startswith("api."):
        return "live"
    return "unknown"


def accounts(data: dict | None = None) -> list[dict]:
    """계좌 목록에 환경 정보를 붙여 반환.

    usable=True 면 현재 NHPLUG_BASE_URL 환경에서 쓸 수 있는 계좌다.
    """
    data = data if data is not None else list_accounts()
    env = current_env()
    out = []
    for a in data.get("Output_0", []) or []:
        code = (a.get("acct_type") or "").strip()
        acct_env, desc = ACCT_TYPES.get(code, ("unknown", f"미정의 코드({code or '없음'})"))
        out.append({
            "acct_no": a.get("acct_no"),
            "acct_type": code,
            "env": acct_env,
            "desc": desc,
            # 환경을 판별할 수 없으면 막지 않고 통과시킨다(오탐 방지)
            "usable": (env == "unknown" or acct_env == "unknown" or acct_env == env),
        })
    return out


def usable_accounts(data: dict | None = None) -> list[dict]:
    """현재 환경에서 사용 가능한 계좌만."""
    return [a for a in accounts(data) if a["usable"]]


if __name__ == "__main__":
    env = current_env()
    rows = accounts()
    print(f"호출 환경: {env}  ({get_base_url()})\n")
    print(f"{'계좌번호':14s} {'구분':5s} {'환경':6s} {'사용가능':8s} 설명")
    print("-" * 62)
    for a in rows:
        print(f"{a['acct_no'] or '-':14s} {a['acct_type']:5s} {a['env']:6s} "
              f"{'✅' if a['usable'] else '❌ 환경불일치':8s} {a['desc']}")

    unusable = [a for a in rows if not a["usable"]]
    if unusable:
        other = "모의투자(moapi)" if env == "live" else "운영(api)"
        print(f"\n⚠️ {len(unusable)}개 계좌는 이 환경에서 쓸 수 없습니다 → {other} 도메인에서 사용하세요.")
