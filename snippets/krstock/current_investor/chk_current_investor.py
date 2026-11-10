from current_investor import current_investor

if __name__ == "__main__":
    rows = current_investor("005930", array_cnt=5).get("Output_0", [])
    assert rows, "Output_0(일자별 투자자) 없음"
    r = rows[0]
    print("일자별:", len(rows), "건 · 최근", r.get("bsop_date1"), "종가", r.get("stck_prpr"),
          "· 기관", r.get("gigwan"), "· 개인", r.get("person"))
    print("OK")
