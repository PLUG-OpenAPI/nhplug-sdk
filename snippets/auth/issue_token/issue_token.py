"""접근 토큰 발급 (POST /oauth2/token)."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import get_token


def issue_token() -> str:
    return get_token()


if __name__ == "__main__":
    tok = issue_token()
    print("access_token:", tok[:16], "...")
