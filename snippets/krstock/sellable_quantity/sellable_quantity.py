"""국내주식 매도가능수량 조회 (POST /krstock/inquiry/v1/sellableQuantity).

국내는 매수(buyableQuantity)와 매도(sellableQuantity)가 **별도 API** 다.
해외주식은 buyableAmount 한 API 에서 pcs_dit 로 구분한다(snippets/gbstock/sellable_quantity 참고).

주의: 명세상 iem_cd 는 선택이지만 **실제로는 필수**다. 없으면 rsp_cd 10006
      ("종목코드 항목을 입력하세요.") 로 실패한다.

응답 Output_0.sll_pbl_qty = 매도가능수량, bnc_qty = 보유수량.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def sellable_quantity(act_no: str, iem_cd: str, cfd_lon_cd: str = "00",
                      lon_dt: str | None = None) -> dict:
    """국내주식 매도가능수량. cfd_lon_cd: 00.일반거래 01.유통융자 02.자기융자 03.유통대주 04.자기대주."""
    input_0 = {
        "act_no": act_no,
        "iem_cd": iem_cd,        # 6자리(예: 005930). 실제로는 필수
        "cfd_lon_cd": cfd_lon_cd,
    }
    if lon_dt:
        input_0["lon_dt"] = lon_dt  # 신용대출코드 01.유통융자일 때 YYYYMMDD
    return call("/krstock/inquiry/v1/sellableQuantity", input_0)


if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT", "여기에_계좌번호")
    print(sellable_quantity(acct, "005930"))
