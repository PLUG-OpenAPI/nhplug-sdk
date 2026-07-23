"""해외주식 매수 주문 (POST /gbstock/order/v1/buy).

주의: 실제 주문이 접수됩니다. 기본은 dry_run=True 로 payload 만 반환합니다.
- iem_cd: 티커종목코드(예: AAPL)
- price 지정 시 지정가(호가유형 00) + fc_orr_uit_pr, 생략 시 시장가(03)
- wtm_cur_knd_cd: 1.해당통화 2.원화
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def order_buy(act_no: str, iem_cd: str, orr_qty: int,
              price: float | None = None, nat_cd: str = "200",
              dry_run: bool = True) -> dict:
    input_0 = {
        "act_no": act_no,
        "fc_sec_trd_nat_cd": nat_cd,   # 200.미국
        "iem_cd": iem_cd,              # 티커(AAPL)
        "orr_qty": orr_qty,
        "ahi_nmn_pr_tp_cd": "00" if price is not None else "03",  # 00.지정가 / 03.시장가
        "wtm_cur_knd_cd": "2",         # 2.원화
    }
    if price is not None:
        input_0["fc_orr_uit_pr"] = price
    if dry_run:
        return {"dry_run": True, "Input_0": input_0}
    return call("/gbstock/order/v1/buy", input_0)


if __name__ == "__main__":
    # 기본은 드라이런(전송 안 함). 실제 전송하려면 dry_run=False + 테스트/모의투자 환경.
    print(order_buy("여기에_해외거래_계좌번호", "AAPL", 1, price=315, dry_run=True))
