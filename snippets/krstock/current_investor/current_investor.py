"""국내주식 투자자별 매매 (POST /krstock/quote/v1/currentInvestor).

Output_0 = 일자별 투자자 순매수(배열, 최신이 앞).
   주요 필드: bsop_date1(거래일자) · stck_prpr(종가) · gigwan(기관계) · person(개인)
             frgn_ntby_qty·invest(외국인) · program(프로그램) · for_rate(외국인지분율)
   필드 정의는 명세 openapi.json 이 정본이다.

🔴 array_cnt(요청건수)는 **필수**다.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def current_investor(iem_cd: str, market_cd: str = "KRX", array_cnt: int = 10) -> dict:
    """투자자별 매매. 최근 array_cnt 일 분량을 받는다."""
    return call("/krstock/quote/v1/currentInvestor", {
        "market_cd": market_cd,
        "iem_cd": iem_cd,
        "array_cnt": str(array_cnt),   # 필수 — 문자열로 전달
    })


if __name__ == "__main__":
    print(current_investor("005930", array_cnt=5))
