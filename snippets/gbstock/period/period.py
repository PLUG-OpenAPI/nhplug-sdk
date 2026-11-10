"""해외주식 기간별 시세 — 일·주·월봉 (POST /gbstock/quote/v1/period).

종목코드는 티커(예: AAPL)를 iem_cd 로 넣는다.
캔들은 Output_1(배열, 최신이 앞) · 종목 요약은 Output_0(배열 1건).

🔴 필수 입력이 **8개**다. 아래 함수가 일·주·월봉 기준값을 채운다.
🔴 gubun(주기) 코드가 **국내와 다르다** (명세 261015)
   해외  1.틱 2.분 3.일 4.주 5.월
   국내  1.일 2.주 3.월 4.년   (snippets/krstock/period)
   국내 값 "1"(일)을 넣으면 오류 없이 **틱**이 온다. 아래 상수(DAY·WEEK·MONTH)를 쓴다.

입력값 (명세 261015)
   end_dt      검색종료일 YYYYMMDD
   xtick       조회단위 — 일·주·월봉은 "0001" (분·틱일 때만 다른 값)
   today_cls   0.종료일조회 1.당일조회
   market_cls  장시간구분 0.전체 1.정규장
   maxavg      최대이평 — "0" 으로 호출해 정상 응답 확인(실측 2026-11-10)

⚠️ 가격·거래량이 **숫자**로 온다(국내 기간별은 문자열).
연속조회: 더 있으면 응답 헤더 cts_flag=Y 다. 전체가 필요하면 nhplug.paginate() 를 쓴다.
"""
import os, sys
from datetime import date
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call

DAY, WEEK, MONTH = "3", "4", "5"   # 해외 gubun — 국내와 다르다


def period(iem_cd: str = "AAPL", gubun: str = DAY, count: int = 30,
           end_dt: str | None = None, market_cls: str = "1") -> dict:
    """기간별 시세. gubun: DAY·WEEK·MONTH. end_dt 생략 시 오늘. market_cls: 1=정규장(기본) / 0=전체."""
    return call("/gbstock/quote/v1/period", {
        "iem_cd": iem_cd,
        "end_dt": end_dt or date.today().strftime("%Y%m%d"),
        "count": str(count),       # 문자열로 전달
        "maxavg": "0",
        "gubun": gubun,
        "xtick": "0001",           # 일·주·월봉
        "today_cls": "0",          # 종료일(end_dt) 기준
        "market_cls": market_cls,
    })


if __name__ == "__main__":
    print(period("AAPL", count=5))
