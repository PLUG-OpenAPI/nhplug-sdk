"""ETF·ETN 현재가 (POST /krstock/quote/v1/etfCurrent).

입력은 종목코드 하나다(market_cd 없음). 응답 블록이 5개다.
   Output_0  현재가·호가·거래량 등(객체)
   Output_1  시간대별 체결(배열)
   Output_2  예상체결(객체)
   Output_3  ETF 지표 — itmt_last_nav(장중/최종 NAV) · dprt(괴리율) · trc_errt(추적오차율) · cnfg_cnt(구성종목수)
   Output_4  기초지수(객체)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def etf_current(iem_cd: str = "069500") -> dict:   # 069500 = KODEX 200
    return call("/krstock/quote/v1/etfCurrent", {"iem_cd": iem_cd})


if __name__ == "__main__":
    print(etf_current("069500"))
