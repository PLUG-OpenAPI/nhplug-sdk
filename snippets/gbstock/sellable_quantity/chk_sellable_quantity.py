import os
from sellable_quantity import sellable_quantity

if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT")
    assert acct, "환경변수 NHPLUG_DEFAULT_ACCOUNT 에 해외거래 계좌번호를 설정하세요."
    ticker = os.environ.get("NHPLUG_TEST_TICKER", "AAPL")

    data = sellable_quantity(acct, ticker)
    o0 = data.get("Output_0") or {}
    if isinstance(o0, list):
        o0 = o0[0] if o0 else {}
    print("티커:", ticker)
    print("보유수량:", o0.get("hld_qty"), "| 매도가능수량:", o0.get("sll_pbl_qty"))
    assert "sll_pbl_qty" in o0, "매도가능수량(sll_pbl_qty) 없음"
    print("OK")
