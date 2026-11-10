from etf_current import etf_current

if __name__ == "__main__":
    data = etf_current("069500")
    o0, o3 = data.get("Output_0") or {}, data.get("Output_3") or {}
    assert o0, "Output_0 없음"
    assert o3, "Output_3(ETF 지표) 없음"
    print(o0.get("iem_nm"), "현재가", o0.get("stck_prpr"),
          "· NAV", o3.get("itmt_last_nav"), "· 괴리율", o3.get("dprt"))
    print("OK")
