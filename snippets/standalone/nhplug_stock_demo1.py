# ============================================================================
# 이 예제는 SDK 없이(표준 라이브러리·requests 만으로) 동작하는 원시 예제입니다.
#
#   대부분의 경우  pip install nhplug  이 훨씬 짧고 안전합니다.
#   토큰 캐시·연속조회·호출 유량 제어·WebSocket 서버 한도를 모두 자동 처리합니다.
#       https://pypi.org/project/nhplug/
#
#   아래 예제는 외부 패키지 설치가 제한된 환경, 다른 언어로 포팅할 때,
#   또는 내부 동작을 직접 확인하고 싶을 때를 위한 것입니다.
#   같은 폴더의 README.md 를 함께 읽어 주세요.
# ============================================================================

# ============================================================================
# 실행 전 준비사항 (필독)
# ============================================================================
#
# 이 파일은 nhplug_stock_demo2.py와 하는 일은 동일하지만, 구현 방식이 다르다.
#   - REST 호출:      urllib.request / urllib.parse (표준 라이브러리, 별도 설치 불필요)
#   - WebSocket 구독:  websocket-client (콜백 방식: on_open/on_message/on_error/on_close)
#
# [필수 Python 버전]
#   Python 3.10 이상
#   - 아래 truststore 라이브러리 자체가 Python 3.10 이상을 요구함
#   - 확인 방법: python --version
#
# [설치해야 할 라이브러리] (표준 라이브러리 제외 전부)
#   pip install websocket-client truststore
#
#   - websocket-client : 실시간 시세 WebSocket 접속/구독(import websocket)에 사용
#   - truststore       : WebSocket 접속 시 OS(윈도우/맥) 인증서 저장소로 TLS 인증서를
#                        검증하는 데 사용. NH 실거래 WebSocket 서버가 중간 인증서를
#                        내려주지 않아, 파이썬 기본 인증서 저장소로는 검증이 실패할 수 있음
#
# [함께 있어야 할 파일]
#   이 스크립트와 같은 폴더에 .env 파일이 있어야 하며, [NHPLUG] 섹션에
#   AppKey / SecretKey 값이 채워져 있어야 한다.
#   (AccessToken / TokenExpTime은 비어 있어도 되고, 최초 실행 시 자동으로 채워진다)
#
# [네트워크]
#   사내 프록시 환경변수(HTTP_PROXY 등)가 설정돼 있으면 DNS 오류(getaddrinfo failed)가
#   날 수 있다. 아래 코드에서 이 환경변수를 자동으로 무시하도록 처리해뒀다.
#
# ============================================================================

"""
NH투자증권 Open API 국내주식 조회 · 실시간시세 데모 스크립트 (urllib + websocket-client 버전)

흐름:
  1) .env 파일에서 AppKey / SecretKey, 그리고 기존 토큰 정보를 읽는다
  2) .env에 저장된 토큰이 아직 유효하면 재사용하고, 없거나 만료됐으면
     POST /oauth2/token 으로 새로 발급받아 .env에 저장한다
  3) 토큰으로 POST /n2/acctinfo 계좌 목록을 조회해 출력한다
  4) 토큰으로 POST /krstock/inquiry/v1/balance 계좌 잔고를 조회해 출력한다
  5) 삼성전자(005930)로 POST /krstock/quote/v1/currentPrice 현재가를 조회해 출력한다
  6) 같은 종목의 실시간 시세를 WebSocket으로 구독한다. 채널(tr_cd)은 미리 목록으로
     선언해두는 대신, call_api()처럼 필요한 시점에 subscribe()를 호출해서 등록하고,
     5초간 수신한 뒤 종료한다

참고:
  - 접근토큰 발급은 운영(api.nhplug.com) 전용이며, 토큰만 발급하는 것이므로
    실제 매매는 발생하지 않는다.
  - 토큰은 24시간(expires_in=86400) 유효하다. 매 호출마다 재발급하지 말고
    TokenExpTime을 확인해서 만료 전까지 재사용해야 한다.
  - 연속조회(cts/cts_flag)를 지원하는지 여부는 API마다 다르다. 그래서 아래 call_api()는
    일단 한 번 호출해보고, 응답 헤더에 cts_flag="Y"가 내려온 경우에만 이어서 호출한다.
    cts를 내려주지 않는 API는 자연스럽게 한 번만 호출하고 끝난다.
"""

import configparser
import json
import os
import ssl
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import truststore  # pip install truststore
import websocket  # pip install websocket-client

ENV_PATH = Path(__file__).resolve().parent / ".env"
SECTION = "NHPLUG"
ACCT_NO = "계좌번호입력"   # 아래 3) 계좌 목록 조회 결과에서 골라 넣으세요
IEM_CD = "005940"  # NH투자증권

# 사내 프록시 환경변수가 남아 있으면 DNS 오류(getaddrinfo failed)가 나므로, 무시하고 직접 연결한다.
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))


def call_api(label, url, headers, body):
    """
    API를 호출한다. (POST, JSON)

    - 먼저 cts 관련 헤더 없이 한 번 호출한다.
    - 응답 헤더의 cts_flag가 "Y"이고 cts 값이 이전 호출과 다르면, 그 cts/cts_flag 값을
      다음 요청 헤더에 그대로 담아 이어서 호출한다. (다음 페이지가 있다는 뜻)
    - cts_flag가 "N"이거나, cts 값이 이전과 동일하거나, API가 cts 자체를 내려주지 않으면
      더 이상 호출하지 않고 끝낸다.

    각 페이지의 응답(JSON)을 리스트로 반환한다.
    """
    call_headers = dict(headers)
    previous_cts = ""
    page = 1
    results = []

    while True:
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            method="POST",
            headers=call_headers,
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read())
            cts = response.headers.get("cts", "")
            cts_flag = response.headers.get("cts_flag", "")

        print(f"\n[{label} - {page}페이지] 요청 헤더:", {**call_headers, "Authorization": "Bearer ***"})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        results.append(result)

        has_next_page = cts_flag == "Y" and cts != previous_cts
        if not has_next_page:
            return results

        # 다음 호출은 이번 응답의 cts/cts_flag를 헤더에 그대로 담아서 요청한다
        call_headers["cts"] = cts
        call_headers["cts_flag"] = cts_flag
        previous_cts = cts
        page += 1


# 1) .env 파일에서 AppKey / SecretKey, 기존 토큰 정보 읽기
config = configparser.ConfigParser(interpolation=None)
config.optionxform = str  # 대소문자 그대로 유지 (AppKey, SecretKey ...)
config.read(ENV_PATH, encoding="utf-8")

app_key = config[SECTION]["AppKey"]
secret_key = config[SECTION]["SecretKey"]
access_token = config[SECTION].get("AccessToken", "")
token_exp_time = config[SECTION].get("TokenExpTime", "")

token_is_valid = (
    access_token != ""
    and token_exp_time != ""
    and datetime.now() < datetime.strptime(token_exp_time, "%Y-%m-%d %H:%M:%S")
)


# 2) .env에 저장된 토큰이 유효하면 재사용, 없거나 만료됐으면 새로 발급
if token_is_valid:
    print(f"기존 토큰 재사용 (만료시각: {token_exp_time})")

else:
    request = urllib.request.Request(
        "https://api.nhplug.com:8443/oauth2/token",
        data=urllib.parse.urlencode({
            "appkey": app_key,
            "appsecretkey": secret_key,
            "grant_type": "client_credentials",
            "scope": "oob",
        }).encode(),
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read())

    access_token = result["access_token"]
    expire_at = datetime.now() + timedelta(seconds=result["expires_in"])

    config[SECTION]["AccessToken"] = access_token
    config[SECTION]["TokenExpTime"] = expire_at.strftime("%Y-%m-%d %H:%M:%S")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        config.write(f)

    print(f"토큰 발급 완료. 만료시각: {expire_at:%Y-%m-%d %H:%M:%S}")


# 3) 계좌 목록 조회
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}
pages = call_api("계좌 목록 조회", "https://api.nhplug.com:8443/n2/acctinfo", headers, {"Input_0": {}})
result = pages[0]

acct_type_name = {"01": "운영(일반)", "02": "운영(주문대리인)", "03": "모의투자"}

print("\n계좌 목록")
for account in result["Output_0"]:
    print(f"  {account['acct_no']}  [{acct_type_name.get(account['acct_type'], account['acct_type'])}]")


# 4) 계좌 잔고 조회
#    ACCT_NO 는 위 3)에서 출력된 계좌 목록 중 하나를 골라 파일 상단에 넣으면 된다.
#    운영(api) 환경에서는 acct_type 01/02, 모의투자(moapi) 환경에서는 03 계좌를 써야 한다.
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}
body = {
    "Input_0": {
        "act_no": ACCT_NO,
        "bnc_bse_cd": "1",      # 1:체결기준 총평가, 5:현재가기준
        "ltg_aot_dit_cd": "1",  # 1:상장종목, 9:전체
        "aet_bse": "1",         # 1:순자산, 2:총자산
        "qut_dit_cd": "UNT",    # 시세구분: UNT(통합)/KRX/NXT
    }
}
call_api("계좌 잔고 조회", "https://api.nhplug.com:8443/krstock/inquiry/v1/balance", headers, body)


# 5) 삼성전자(005930) 현재가 조회
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}
body = {
    "Input_0": {
        "iem_cd": IEM_CD,
        "market_cd": "UNT",  # 시세구분: UNT(통합)/KRX/NXT
    }
}
call_api(f"현재가 조회 ({IEM_CD})", "https://api.nhplug.com:8443/krstock/quote/v1/currentPrice", headers, body)


# 6) 같은 종목의 실시간 시세를 WebSocket으로 구독
#    tr_cd 목록을 미리 선언해두지 않고, 연결이 열린 뒤 필요한 시점에 subscribe()를
#    호출해서 채널을 하나씩 등록한다 (call_api()를 필요할 때 호출하는 것과 같은 방식).
#    tr_cd 예: mc(실시간체결가통합) mb(실시간호가통합) oc(실시간체결가KRX) 등
connected_event = threading.Event()  # on_open이 호출된 뒤에만 subscribe()를 보낼 수 있으므로 필요


def subscribe(ws, tr_cd, tr_key):
    """이미 열려 있는 WebSocket 연결에 채널 하나를 구독 등록한다. 필요한 시점에 여러 번 호출 가능."""
    message = {
        "header": {"token": access_token, "tr_type": "1"},  # tr_type 1:등록(구독)
        "body": {"tr_cd": tr_cd, "tr_key": tr_key},
    }
    ws.send(json.dumps(message))
    print(f"[구독 등록] tr_cd={tr_cd} tr_key={tr_key}")


def on_open(ws):
    connected_event.set()


def on_message(ws, message):
    data = json.loads(message)
    tr_cd = data.get("header", {}).get("tr_cd", "?")  # 여러 채널이 섞여 오므로 tr_cd로 구분해서 출력
    print(f"[{tr_cd}]", json.dumps(data, ensure_ascii=False, indent=2))


def on_error(ws, error):
    print("WebSocket 오류:", error)


def on_close(ws, status_code, message):
    print("WebSocket 연결 종료")


# 실거래 WebSocket 서버가 중간 인증서를 내려주지 않아 파이썬 기본 인증서 저장소로는 TLS 검증이
# 실패할 수 있다. truststore를 쓰면 OS(윈도우)에 이미 등록된 인증서 저장소로 검증하므로,
# 검증을 끄지 않고도(cert_reqs=CERT_NONE 없이) 정상적으로 접속할 수 있다.
ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

ws = websocket.WebSocketApp(
    "wss://api.nhplug.com:7070/websocket",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

# run_forever는 계속 블로킹되므로 별도 스레드에서 돌린다.
thread = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"context": ssl_context}}, daemon=True)
thread.start()

connected_event.wait(timeout=10)  # 연결이 열릴 때까지 대기해야 subscribe()가 안전하게 전송된다

# 연결된 뒤, 필요한 채널을 그때그때 등록한다. 여기서는 예시로 두 채널을 등록했다.
subscribe(ws, "mc", IEM_CD)  # 실시간체결가통합
subscribe(ws, "mb", IEM_CD)  # 실시간호가통합

# 메인 스레드는 최대 5초만 기다린다. 5초가 되기 전에 Ctrl+C를 누르면 즉시 종료된다.
try:
    time.sleep(5)
    print("\n5초 경과, 실시간 시세 수신을 종료합니다.")
except KeyboardInterrupt:
    print("\n사용자가 종료했습니다.")
finally:
    ws.close()
