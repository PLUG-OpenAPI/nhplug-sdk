import os
from balance import balance

if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT")
    assert acct, "환경변수 NHPLUG_DEFAULT_ACCOUNT 에 계좌번호를 설정하세요."
    data = balance(acct)
    o0 = data.get("Output_0", {})
    print("예수금:", o0.get("dca"), "| 총자산:", o0.get("tot_aet_amt"))
    print("보유종목 수:", len(data.get("Output_1", [])))
    print("OK")
