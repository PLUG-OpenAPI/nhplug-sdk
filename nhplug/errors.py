"""NHPLUG 공통 오류 모델.

HTTP 오류와 **업무 오류(rsp_cd)** 를 하나의 예외로 표현한다.
HTTP 200 이어도 rsp_cd 가 성공 코드가 아니면 실패다(가장 흔한 사고 원인).
"""


class NhplugError(Exception):
    """NH Open API 호출 실패.

    category:
      - "config"     : 설정 오류 — 호출하기 전에 막은 것 (허용되지 않은 호스트, https 아님 …)
      - "auth"       : 토큰 발급/인증 실패 (IGW40031, IGW40043, 401 …)
      - "rate_limit" : 호출 유량 초과 (429, IGW42902)
      - "business"   : HTTP 200 이지만 업무 오류 (rsp_cd 가 성공 코드 아님)
      - "network"    : 네트워크/타임아웃
      - "http"       : 그 외 HTTP 오류
    """

    def __init__(
        self,
        message: str,
        *,
        category: str = "business",
        code: str | None = None,
        status: int | None = None,
        path: str | None = None,
        retryable: bool = False,
        retry_after_ms: int | None = None,
        environment: str | None = None,
        raw=None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.code = code                    # rsp_cd 또는 IGW… 코드
        self.status = status                # HTTP 상태코드
        self.path = path                    # 호출 경로
        self.retryable = retryable          # 재시도 의미가 있는가(자동 재시도는 하지 않음)
        self.retry_after_ms = retry_after_ms
        self.environment = environment      # 호출 대상 base url
        self.raw = raw                      # 서버 원본 응답(dict 또는 문자열)

    def __str__(self) -> str:
        parts = [f"[{self.category}]"]
        if self.code:
            parts.append(str(self.code))
        parts.append(self.message)
        if self.path:
            parts.append(f"({self.path})")
        if self.retry_after_ms:
            parts.append(f"retry_after={self.retry_after_ms}ms")
        return " ".join(parts)
