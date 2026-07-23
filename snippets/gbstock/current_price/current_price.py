"""해외주식 현재가상세 (POST /gbstock/quote/v1/current).

종목코드는 티커(예: 미국주식 APPLE = AAPL)를 iem_cd 로 넣는다.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def current_price(iem_cd: str = "AAPL") -> dict:
    return call("/gbstock/quote/v1/current", {"iem_cd": iem_cd})


if __name__ == "__main__":
    print(current_price("AAPL"))
