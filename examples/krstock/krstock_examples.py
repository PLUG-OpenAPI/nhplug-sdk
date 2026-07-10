"""국내주식 사용 예제. 필요한 부분만 주석 해제해 실행하세요."""
import krstock_functions as k

if __name__ == "__main__":
    # 1) 계좌 목록
    accts = k.list_accounts().get("Output_0", [])
    print("계좌:", [a["acct_no"] for a in accts])

    # 2) 현재가
    price = k.current_price("005930").get("Output_0", {})
    print("삼성전자 현재가:", price.get("stck_prpr"))

    # 3) 잔고 (첫 계좌)
    if accts:
        bal = k.balance(accts[0]["acct_no"]).get("Output_0", {})
        print("예수금:", bal.get("dca"))

    # 4) 매수 주문 (실주문 — 필요 시 주석 해제, 모의투자 권장)
    # print(k.cash_buy(accts[0]["acct_no"], "005930", 1, orr_pr=70000))
