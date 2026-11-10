from period import period, WEEK

if __name__ == "__main__":
    rows = period("AAPL", count=5).get("Output_1", [])
    assert rows, "Output_1(캔들) 없음"
    print("일봉:", len(rows), "건 · 최근", rows[0].get("trade_date"), "종가", rows[0].get("close_prc"))

    weeks = period("AAPL", gubun=WEEK, count=3).get("Output_1", [])
    assert weeks, "주봉 Output_1 없음"
    print("주봉:", len(weeks), "건 · 최근", weeks[0].get("trade_date"))
    print("OK")
