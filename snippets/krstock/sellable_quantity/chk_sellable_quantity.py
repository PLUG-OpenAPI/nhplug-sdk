import os
from sellable_quantity import sellable_quantity

if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT")
    assert acct, "환경변수 NHPLUG_DEFAULT_ACCOUNT 에 계좌번호를 설정하세요."
    code = os.environ.get("NHPLUG_TEST_STOCK", "005930")

    data = sellable_quantity(acct, code)
    o0 = data.get("Output_0") or {}
    if isinstance(o0, list):        # 응답이 배열로 오는 경우 대비
        o0 = o0[0] if o0 else {}
    print("종목:", o0.get("iem_nm"), o0.get("iem_cd"))
    print("보유수량:", o0.get("bnc_qty"), "| 매도가능수량:", o0.get("sll_pbl_qty"))
    assert "sll_pbl_qty" in o0, "매도가능수량(sll_pbl_qty) 없음"
    print("OK")
