"""해외주식 매도가능수량 조회 (POST /gbstock/inquiry/v1/buyableAmount, pcs_dit="3").

⚠️ 해외주식은 **매도 전용 API 가 따로 없다.** 매수가능금액 API(buyableAmount)에
   처리구분(pcs_dit)을 바꿔 매도가능수량을 조회한다. (국내는 sellableQuantity 별도 API)

pcs_dit: 1.매수가능금액 2.매수가능수량 3.매도가능수량 4.예약매수금액/수량 5.예약매도수량

응답 Output_0.sll_pbl_qty = 매도가능수량, hld_qty = 보유수량. (국내와 필드명 동일)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def sellable_quantity(act_no: str, iem_cd: str = "AAPL", nat_cd: str = "200") -> dict:
    """해외주식 매도가능수량. iem_cd 는 티커(AAPL), nat_cd: 200.미국 070.일본 120.홍콩 160.상해 170.심천."""
    return call("/gbstock/inquiry/v1/buyableAmount", {
        "act_no": act_no,
        "pcs_dit": "3",                # 3.매도가능수량조회
        "fc_sec_trd_nat_cd": nat_cd,
        "iem_cd": iem_cd,
        "wtm_cur_knd_cd": "2",         # 2.원화
        "oss_orr_knd_cd": "1",         # 1.GTS(미국시장주문)
        "ahi_nmn_pr_tp_cd": "03",      # 03.시장가
    })


if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_해외거래_계좌번호")
    print(sellable_quantity(acct, "AAPL"))
