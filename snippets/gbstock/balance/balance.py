"""해외주식 잔고 조회 (POST /gbstock/inquiry/v1/balance).

fc_sec_trd_nat_cd: 200.미국 070.일본 120.홍콩 160.상해 170.심천
cur_cd: KRW.전체 USD/CNY/HKD/JPY
응답: Output_0(계좌 요약) + Output_1(보유종목 배열).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def balance(act_no: str, nat_cd: str = "200", cur_cd: str = "USD") -> dict:
    return call("/gbstock/inquiry/v1/balance", {
        "act_no": act_no,
        "qut_iqr_dit_cd": "9",        # 9.전체
        "fc_sec_trd_nat_cd": nat_cd,  # 200.미국
        "cur_cd": cur_cd,             # USD
        "xns_dit_cd": "1",            # 1.비용 포함 (선택)
    })


if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_해외거래_계좌번호")
    print(balance(acct))
