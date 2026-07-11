"""국내주식 현재가 시세 (POST /krstock/quote/v1/currentPrice)."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def current_price(iem_cd: str, market_cd: str = "KRX") -> dict:
    return call("/krstock/quote/v1/currentPrice", {"iem_cd": iem_cd, "market_cd": market_cd})


if __name__ == "__main__":
    print(current_price("005930"))
