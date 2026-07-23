from current_price import current_price

if __name__ == "__main__":
    data = current_price("AAPL")
    o0 = data.get("Output_0", {})
    assert o0, "Output_0 없음"
    print("응답 필드(일부):", list(o0.keys())[:8])
    print("OK")
