"""계좌 목록 조회 (POST /n2/acctinfo). 응답 Output_0[].acct_no."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def list_accounts() -> dict:
    return call("/n2/acctinfo", {})


if __name__ == "__main__":
    data = list_accounts()
    for a in data.get("Output_0", []):
        print(a.get("acct_no"), a.get("acct_type"))
