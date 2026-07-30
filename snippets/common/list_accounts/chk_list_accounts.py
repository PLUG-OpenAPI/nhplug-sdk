from list_accounts import ACCT_TYPES, accounts, current_env, list_accounts, usable_accounts

if __name__ == "__main__":
    data = list_accounts()
    assert data.get("rsp_cd") is not None, "응답 봉투 없음"

    env = current_env()
    rows = accounts(data)
    usable = usable_accounts(data)
    print("계좌 수:", len(rows), "| rsp:", data.get("rsp_msg"))
    print("호출 환경:", env, "| 사용 가능 계좌:", len(usable))

    # acct_type 은 환경 판별의 근거이므로 값이 비어 있으면 알린다
    unknown = [a for a in rows if a["env"] == "unknown"]
    if unknown:
        print("⚠️ 미정의 acct_type:", [(a["acct_no"], a["acct_type"]) for a in unknown],
              "| 정의된 코드:", sorted(ACCT_TYPES))

    if rows and not usable:
        print("⚠️ 이 환경에서 쓸 수 있는 계좌가 없습니다 — NHPLUG_BASE_URL 을 확인하세요.")

    print("OK")
