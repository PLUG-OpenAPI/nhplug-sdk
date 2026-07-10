from order_cash_buy import order_cash_buy

if __name__ == "__main__":
    # 안전: 드라이런으로 payload 형식만 검증(실주문 X)
    r = order_cash_buy("00000000000", "005930", 1, orr_pr=70000, dry_run=True)
    assert r["Input_0"]["iem_cd"] == "005930" and r["Input_0"]["orr_pr"] == 70000
    print("payload OK:", r["Input_0"])
    print("실제 주문은 dry_run=False 로 호출하세요(모의투자 권장).")
