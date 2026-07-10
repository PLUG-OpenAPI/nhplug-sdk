from issue_token import issue_token

if __name__ == "__main__":
    tok = issue_token()
    assert tok and len(tok) > 10, "토큰 발급 실패"
    print("OK - 토큰 발급 성공")
