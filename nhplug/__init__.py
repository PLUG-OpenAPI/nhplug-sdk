"""nhplug — NH투자증권 Open API 공용 파이썬 클라이언트.

사용 예:
    from nhplug import call
    data = call("/krstock/quote/v1/currentPrice", {"shrn_iscd": "005930"})
"""
try:
    from dotenv import load_dotenv  # .env 자동 로드(있으면)
    load_dotenv()
except Exception:
    pass

from .auth import get_token, get_base_url
from .client import call

__all__ = ["get_token", "get_base_url", "call"]
