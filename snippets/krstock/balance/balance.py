"""국내주식 잔고 조회 (POST /krstock/inquiry/v1/balance).

🔴 aly_qut_cd 는 **필수**다 (명세 260911 · KRX 시간연장).
   1 = 정규장   2 = 전체장(정규장 + 정규장외)
   빠뜨리면 호출이 실패한다. qut_dit_cd(시장)와는 다른 축이다 —
   qut_dit_cd = 어느 **시장**의 시세(UNT/KRX/NXT), aly_qut_cd = 어느 **시간대**의 시세.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def balance(act_no: str, qut_dit_cd: str = "UNT", aly_qut_cd: str = "1") -> dict:
    """국내주식 잔고. aly_qut_cd: 1=정규장(기본) / 2=전체장(정규장외 포함)."""
    return call("/krstock/inquiry/v1/balance", {
        "act_no": act_no,
        "bnc_bse_cd": "5",
        "ltg_aot_dit_cd": "9",
        "aet_bse": "2",
        "qut_dit_cd": qut_dit_cd,
        "aly_qut_cd": aly_qut_cd,   # 필수 — 빼면 실패
    })


if __name__ == "__main__":
    import os as _os
    acct = _os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_계좌번호")
    print(balance(acct))
