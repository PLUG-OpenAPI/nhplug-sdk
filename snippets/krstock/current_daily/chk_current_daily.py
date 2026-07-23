from current_daily import current_daily

if __name__ == "__main__":
    data = current_daily("005930", array_cnt=5)
    rows = data.get("Output_0", [])
    assert rows, "Output_0 없음"
    print("일자별 건수:", len(rows))
    print("최근:", rows[0].get("bsop_date"), "종가:", rows[0].get("stck_clpr"))
    print("OK")
