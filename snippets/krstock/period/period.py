"""국내주식 기간별 시세 — 일·주·월·년봉 (POST /krstock/quote/v1/period).

캔들은 Output_1(배열, 최신이 앞) · 종목 요약은 Output_0(객체).

🔴 gubun(주기) 코드가 **해외와 다르다** (명세 261015)
   국내  1.일 2.주 3.월 4.년 5.분 6.초 7.틱
   해외  1.틱 2.분 3.일 4.주 5.월   (snippets/gbstock/period)
   그대로 옮기면 오류 없이 **다른 봉**이 온다. 아래 상수(DAY·WEEK…)를 쓴다.

🔴 view_main_yn 은 **필수**다 — Y = 정규장 / N = 전체장(정규장 + 정규장외).

⚠️ market_cd=UNT(통합) + view_main_yn=Y 는 **2026-09-14 이후 데이터만** 온다(실측 2026-11-10,
   연속조회로도 늘지 않음). 긴 기간이 필요하면 KRX 를 쓴다 — 이 함수의 기본값이다.

연속조회: 한 번에 array_cnt 건이 오고, 더 있으면 응답 헤더 cts_flag=Y 다.
   전체가 필요하면 같은 경로·입력으로 nhplug.paginate() 를 쓴다.
분·초·틱봉(gubun 5~7)은 xtick·today_cls_code 를 추가로 넣어야 한다 — 명세 openapi.json 참조.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import call

DAY, WEEK, MONTH, YEAR = "1", "2", "3", "4"   # 국내 gubun — 해외와 다르다


def period(iem_cd: str, gubun: str = DAY, array_cnt: int = 30,
           market_cd: str = "KRX", view_main_yn: str = "Y") -> dict:
    """기간별 시세. gubun: DAY·WEEK·MONTH·YEAR. view_main_yn: Y=정규장(기본) / N=전체장."""
    return call("/krstock/quote/v1/period", {
        "market_cd": market_cd,
        "iem_cd": iem_cd,
        "gubun": gubun,
        "array_cnt": str(array_cnt),   # 문자열로 전달
        "view_main_yn": view_main_yn,  # 필수 — 빼면 실패
    })


if __name__ == "__main__":
    print(period("005930", array_cnt=5))
