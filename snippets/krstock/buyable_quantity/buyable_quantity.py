"""국내주식 매수가능수량 조회 (POST /krstock/inquiry/v1/buyableQuantity).

price 지정 시 보통가(01) 기준, 생략 시 시장가(05) 기준으로 조회한다.
ost_dit_cd: 1.현금 2.신용 3.매입자금대출.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def buyable_quantity(act_no: str, iem_cd: str, price: int | None = None) -> dict:
    input_0 = {
        "ost_dit_cd": "1",                              # 1.현금
        "act_no": act_no,
        "iem_cd": iem_cd,
        "nmn_pr_tp_cd": "01" if price is not None else "05",  # 01.보통가 / 05.시장가
    }
    if price is not None:
        input_0["orr_pr"] = price
    return call("/krstock/inquiry/v1/buyableQuantity", input_0)


if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_계좌번호")
    print(buyable_quantity(acct, "005930", price=70000))
