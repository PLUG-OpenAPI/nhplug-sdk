"""국내주식 잔고 조회 (POST /krstock/inquiry/v1/balance)."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def balance(act_no: str) -> dict:
    return call("/krstock/inquiry/v1/balance", {
        "act_no": act_no,
        "bnc_bse_cd": "5",
        "ltg_aot_dit_cd": "9",
        "aet_bse": "2",
        "qut_dit_cd": "UNT",
    })


if __name__ == "__main__":
    import os as _os
    acct = _os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_계좌번호")
    print(balance(acct))
