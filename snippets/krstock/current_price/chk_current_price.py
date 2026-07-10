from current_price import current_price

if __name__ == "__main__":
    data = current_price("005930")
    o0 = data.get("Output_0", {})
    print("종목:", o0.get("hts_isnm"), "| 현재가:", o0.get("stck_prpr"))
    assert o0, "Output_0 없음"
    print("OK")
