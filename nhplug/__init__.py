"""nhplug — NH투자증권 Open API 공용 파이썬 클라이언트.

사용 예:
    from nhplug import call, NhplugError
    try:
        data = call("/krstock/quote/v1/currentPrice", {"iem_cd": "005930", "market_cd": "KRX"})
    except NhplugError as e:
        print(e.category, e.code, e.message)   # 업무 오류(rsp_cd)도 예외로 올라옵니다

토큰은 24시간 유효하며 ~/.nhplug/ 에 파일 캐시되어 프로세스가 바뀌어도 재사용됩니다
(불필요한 재발급 = 보안 알림 발생). 끄려면 NHPLUG_TOKEN_CACHE=0.
"""
try:
    from dotenv import load_dotenv  # .env 자동 로드(있으면)
    load_dotenv()
except Exception:
    pass

from .auth import get_token, get_base_url, get_auth_url, clear_token, cache_path
from .client import call, success_codes
from .errors import NhplugError

__version__ = "0.1.0"

__all__ = [
    "call", "success_codes",
    "get_token", "get_base_url", "get_auth_url", "clear_token", "cache_path",
    "NhplugError",
    "__version__",
]

# 하위 모듈은 필요할 때 import 한다 (선택 의존성이 없어도 패키지가 로드되도록).
#   from nhplug.realtime import subscribe          # websocket-client 필요
#   from nhplug.instruments import load_master     # pandas 는 선택
