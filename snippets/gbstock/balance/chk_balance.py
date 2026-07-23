import os
from balance import balance

if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT")
    assert acct, "환경변수 NHPLUG_DEFAULT_ACCOUNT 에 해외거래 계좌번호를 설정하세요."
    data = balance(acct, nat_cd="200", cur_cd="USD")
    o0 = data.get("Output_0", {})
    print("외화총자산:", o0.get("fc_aet_amt"), "| 원화환산총자산:", o0.get("tot_aet_amt"))
    print("보유종목 수:", len(data.get("Output_1", [])))
    print("OK")
