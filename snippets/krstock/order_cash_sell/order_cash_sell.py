"""국내주식 현금 매도 주문 (POST /krstock/order/v1/cashSell).

주의: 실제 주문이 접수됩니다. 기본은 dry_run=True 로 payload 만 반환합니다.
price 지정 시 보통가(01) + orr_pr, 생략 시 시장가(05).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def order_cash_sell(act_no: str, iem_cd: str, orr_qty: int,
                    orr_pr: int | None = None, dry_run: bool = True) -> dict:
    is_market = orr_pr is None
    input_0 = {
        "act_no": act_no,
        "iem_cd": iem_cd,
        "orr_qty": orr_qty,
        "nmn_pr_tp_cd": "05" if is_market else "01",  # 05.시장가 / 01.보통가
        "orr_cnd_dit_cd": "00",                        # 00.없음
        "ssl_nmn_pr_dit_cd": "00",                     # 00.정상
        "rmt_mkt_cd": "KRX",
        "sor_mkt_sli_yn": "N",
    }
    if not is_market:
        input_0["orr_pr"] = orr_pr
    if dry_run:
        return {"dry_run": True, "Input_0": input_0}
    return call("/krstock/order/v1/cashSell", input_0)


if __name__ == "__main__":
    # 기본은 드라이런(전송 안 함). 실제 전송하려면 dry_run=False + 테스트/모의투자 환경.
    print(order_cash_sell("여기에_계좌번호", "005930", 1, orr_pr=70000, dry_run=True))
