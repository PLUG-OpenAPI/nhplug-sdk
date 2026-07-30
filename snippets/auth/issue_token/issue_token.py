"""접근 토큰 발급 (POST /oauth2/token)."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from nhplug import get_token


def issue_token() -> str:
    return get_token()


if __name__ == "__main__":
    # 🔒 토큰 값은 일부라도 출력하지 않는다(화면 공유·로그 캡처로 유출될 수 있음).
    tok = issue_token()
    print(f"토큰 발급 성공 (길이 {len(tok)}자) ✅")
