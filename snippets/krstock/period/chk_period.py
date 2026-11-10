from period import period, WEEK

if __name__ == "__main__":
    rows = period("005930", array_cnt=5).get("Output_1", [])
    assert rows, "Output_1(캔들) 없음"
    print("일봉:", len(rows), "건 · 최근", rows[0].get("bsop_date"), "종가", rows[0].get("stck_prpr"))

    weeks = period("005930", gubun=WEEK, array_cnt=3).get("Output_1", [])
    assert weeks, "주봉 Output_1 없음"
    print("주봉:", len(weeks), "건 · 최근", weeks[0].get("bsop_date"))
    print("OK")
