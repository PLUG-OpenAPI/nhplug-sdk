"""국내주식 당일 시간대별 체결 (POST /krstock/quote/v1/currentExecution).

Output_0 = 시간대별 체결(배열, 최신이 앞) · Output_1 = 당일 누적 체결 요약(객체).

🔴 view_main_yn 은 **필수**다 — Y = 정규장 / N = 전체장(정규장 + 정규장외).
⚠️ array_cnt(읽을갯수)는 선택 입력이라 넣지 않는다. 한 페이지에 300건이 오고(실측 2026-11-10),
   더 있으면 응답 헤더 cts_flag=Y 다. 전체가 필요하면 nhplug.paginate() 를 쓴다.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call


def current_execution(iem_cd: str, market_cd: str = "KRX", view_main_yn: str = "Y") -> dict:
    """당일 시간대별 체결. view_main_yn: Y=정규장(기본) / N=전체장."""
    return call("/krstock/quote/v1/currentExecution", {
        "market_cd": market_cd,
        "iem_cd": iem_cd,
        "view_main_yn": view_main_yn,  # 필수 — 빼면 실패
    })


if __name__ == "__main__":
    print(current_execution("005930"))
