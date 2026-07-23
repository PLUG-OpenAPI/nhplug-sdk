"""해외주식 매수가능금액 조회 (POST /gbstock/inquiry/v1/buyableAmount).

price 를 주면 지정가(호가유형 00) 기준, 생략하면 시장가(03) 기준으로 조회한다.
응답 Output_0.orr_pbl_amt = 주문가능금액, wtm_cur_cd = 통화.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def buyable_amount(act_no: str, iem_cd: str = "AAPL",
                   price: float | None = None, nat_cd: str = "200") -> dict:
    input_0 = {
        "act_no": act_no,
        "pcs_dit": "1",               # 1.매수가능금액조회
        "fc_sec_trd_nat_cd": nat_cd,  # 200.미국
        "iem_cd": iem_cd,             # 티커(AAPL)
        "wtm_cur_knd_cd": "2",        # 2.원화
        "oss_orr_knd_cd": "1",        # 1.GTS(미국시장주문)
        "ahi_nmn_pr_tp_cd": "00" if price is not None else "03",  # 00.지정가 / 03.시장가
    }
    if price is not None:
        input_0["fc_orr_uit_pr"] = price
    return call("/gbstock/inquiry/v1/buyableAmount", input_0)


if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_해외거래_계좌번호")
    print(buyable_amount(acct, "AAPL", price=315))
