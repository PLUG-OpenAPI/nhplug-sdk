"""해외주식 매수가능금액·수량 조회 (POST /gbstock/inquiry/v1/buyableAmount).

⚠️ 이 API 하나가 처리구분(pcs_dit)에 따라 매수/매도 가능수량을 모두 처리한다.
   1.매수가능금액 2.매수가능수량 3.매도가능수량 4.예약매수금액/수량 5.예약매도수량
   → **매도가능수량은 snippets/gbstock/sellable_quantity 참고** (pcs_dit="3")
   (국내주식은 buyableQuantity / sellableQuantity 로 API 가 나뉘어 있다)

price 를 주면 지정가(호가유형 00) 기준, 생략하면 시장가(03) 기준으로 조회한다.
응답 Output_0.orr_pbl_amt = 주문가능금액, max_pbl_qty = 최대가능수량, wtm_cur_cd = 통화.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def buyable_amount(act_no: str, iem_cd: str = "AAPL",
                   price: float | None = None, nat_cd: str = "200",
                   pcs_dit: str = "1") -> dict:
    """pcs_dit: 1.매수가능금액(기본) 2.매수가능수량 3.매도가능수량 4.예약매수 5.예약매도."""
    input_0 = {
        "act_no": act_no,
        "pcs_dit": pcs_dit,
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
