from current_execution import current_execution

if __name__ == "__main__":
    data = current_execution("005930")
    rows = data.get("Output_0", [])
    assert rows, "Output_0(시간대별 체결) 없음"
    print("체결:", len(rows), "건 · 최근", rows[0].get("bsop_hour"), "현재가", rows[0].get("stck_prpr"))
    print("종목:", (data.get("Output_1") or {}).get("iem_nm"))
    print("OK")
