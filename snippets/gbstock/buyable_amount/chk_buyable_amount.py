import os
from buyable_amount import buyable_amount

if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT")
    assert acct, "환경변수 NHPLUG_DEFAULT_ACCOUNT 에 해외거래 계좌번호를 설정하세요."
    data = buyable_amount(acct, "AAPL", price=315)
    o0 = data.get("Output_0", {})
    print("매수가능금액:", o0.get("orr_pbl_amt"), o0.get("wtm_cur_cd"))
    assert o0, "Output_0 없음"
    print("OK")
