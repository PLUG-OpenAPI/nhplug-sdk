from list_accounts import list_accounts

if __name__ == "__main__":
    data = list_accounts()
    assert data.get("rsp_cd") is not None, "응답 봉투 없음"
    print("계좌 수:", len(data.get("Output_0", [])), "| rsp:", data.get("rsp_msg"))
    print("OK")
