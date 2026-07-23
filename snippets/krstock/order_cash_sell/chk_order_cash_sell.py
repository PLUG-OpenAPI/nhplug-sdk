from order_cash_sell import order_cash_sell

if __name__ == "__main__":
    # 드라이런: 전송 없이 주문 payload 구조만 검증
    data = order_cash_sell("20101036881", "005930", 1, orr_pr=70000, dry_run=True)
    assert data.get("dry_run") is True, "dry_run 이어야 함"
    i0 = data["Input_0"]
    for k in ["act_no", "iem_cd", "orr_qty", "nmn_pr_tp_cd", "ssl_nmn_pr_dit_cd", "rmt_mkt_cd"]:
        assert k in i0, f"필수 필드 누락: {k}"
    print("매도 payload:", i0)
    print("OK (dry-run)")
