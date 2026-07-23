import os
from buyable_quantity import buyable_quantity

if __name__ == "__main__":
    acct = os.environ.get("NHPLUG_DEFAULT_ACCOUNT")
    assert acct, "환경변수 NHPLUG_DEFAULT_ACCOUNT 에 계좌번호를 설정하세요."
    data = buyable_quantity(acct, "005930", price=70000)
    o0 = data.get("Output_0", {})
    assert o0, "Output_0 없음"
    print("응답 필드(일부):", list(o0.keys())[:8])
    print("OK")
