"""국내주식 현재가 일자별 (POST /krstock/quote/v1/currentDaily).

시세 조회는 market_cd(KRX/NXT/UNT) + iem_cd(6자리) 를 함께 넣는다.
응답 Output_0 은 일자별 시세 배열(이동평균·백테스트 등에 활용).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def current_daily(iem_cd: str, market_cd: str = "KRX", array_cnt: int = 30) -> dict:
    return call("/krstock/quote/v1/currentDaily", {
        "market_cd": market_cd,
        "iem_cd": iem_cd,
        "array_cnt": str(array_cnt),   # 문자열로 전달
    })


if __name__ == "__main__":
    print(current_daily("005930", array_cnt=5))
