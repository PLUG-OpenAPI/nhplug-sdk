from order_buy import order_buy

if __name__ == "__main__":
    # 드라이런: 전송 없이 주문 payload 구조만 검증
    data = order_buy("20101984948", "AAPL", 1, price=315, dry_run=True)
    assert data.get("dry_run") is True, "dry_run 이어야 함"
    i0 = data["Input_0"]
    for k in ["act_no", "fc_sec_trd_nat_cd", "iem_cd", "orr_qty", "ahi_nmn_pr_tp_cd", "wtm_cur_knd_cd"]:
        assert k in i0, f"필수 필드 누락: {k}"
    print("주문 payload:", i0)
    print("OK (dry-run)")
