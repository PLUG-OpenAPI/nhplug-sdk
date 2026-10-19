# NH투자증권 Open API 단독 실행 예제 — requests + websockets(async)
#   설치: pip install requests websockets
#   준비: cp .env.example .env  후 AppKey / SecretKey 입력  (자세한 내용은 같은 폴더 README.md)

import asyncio
import json
from configparser import ConfigParser
from datetime import datetime, timedelta
from pathlib import Path

import requests    # pip install requests
import websockets  # pip install websockets

BASE_URL = "https://api.nhplug.com:8443"
WS_URL = "wss://api.nhplug.com:7070/websocket"
ENV_PATH = Path(__file__).resolve().parent / ".env"
ACCT_NO = "계좌번호입력"   # 3) 계좌 목록 출력에서 골라 넣으세요
IEM_CD = "005940"          # NH투자증권

session = requests.Session()
session.trust_env = False  # 사내 프록시 환경변수를 무시하고 직접 연결 (getaddrinfo failed 방지)


def call_api(path, body):
    """REST API 호출 (POST, JSON)"""
    response = session.post(BASE_URL + path, json=body, timeout=15,
                            headers={"Authorization": f"Bearer {access_token}"})
    result = response.json()
    print(f"\n[{path}]")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


# 1) .env 에서 앱키와 저장된 토큰 읽기
config = ConfigParser(interpolation=None)
config.optionxform = str
config.read(ENV_PATH, encoding="utf-8")
env = config["NHPLUG"]
access_token = env.get("AccessToken", "")
token_exp_time = env.get("TokenExpTime", "")


# 2) 토큰이 유효하면 재사용, 아니면 새로 발급해 .env 에 저장 (토큰은 24시간 유효 — 매번 발급하지 않는다)
if access_token and token_exp_time and datetime.now() < datetime.strptime(token_exp_time, "%Y-%m-%d %H:%M:%S"):
    print(f"기존 토큰 재사용 (만료시각: {token_exp_time})")
else:
    result = session.post(BASE_URL + "/oauth2/token", timeout=15, data={  # data= 는 form-urlencoded 로 전송된다
        "appkey": env["AppKey"],
        "appsecretkey": env["SecretKey"],
        "grant_type": "client_credentials",
        "scope": "oob",
    }).json()

    access_token = result["access_token"]
    expire_at = datetime.now() + timedelta(seconds=result["expires_in"])
    env["AccessToken"] = access_token
    env["TokenExpTime"] = expire_at.strftime("%Y-%m-%d %H:%M:%S")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        config.write(f)
    print(f"토큰 발급 완료 (만료시각: {expire_at:%Y-%m-%d %H:%M:%S})")


# 3) 계좌 목록 — acct_type 01·02=운영, 03=모의투자
call_api("/n2/acctinfo", {"Input_0": {}})


# 4) 계좌 잔고
call_api("/krstock/inquiry/v1/balance", {"Input_0": {
    "act_no": ACCT_NO,
    "bnc_bse_cd": "1",      # 1:체결기준 총평가, 5:현재가기준
    "ltg_aot_dit_cd": "1",  # 1:상장종목, 9:전체
    "aet_bse": "1",         # 1:순자산, 2:총자산
    "qut_dit_cd": "UNT",    # 시장: UNT(통합)/KRX/NXT
    "aly_qut_cd": "1",      # 시간대: 1:정규장, 2:전체장
}})


# 5) 실시간 시세 — 등록 → 수신 (수신 중 현재가 REST 호출) → 해제
TR_CDS = ("mc", "mb")  # mc: 체결가(통합), mb: 호가(통합)


async def send(ws, tr_type):
    """tr_type 1:등록, 2:해제"""
    for tr_cd in TR_CDS:
        await ws.send(json.dumps({
            "header": {"token": access_token, "tr_type": tr_type},
            "body": {"tr_cd": tr_cd, "tr_key": IEM_CD},
        }))


async def receive(ws):
    """수신해 출력 (등록·해제 응답 + 실시간 데이터)"""
    async for message in ws:
        print(json.dumps(json.loads(message), ensure_ascii=False, indent=2))


async def realtime():
    async with websockets.connect(WS_URL) as ws:
        await send(ws, "1")                          # 등록
        receiver = asyncio.create_task(receive(ws))  # 수신은 백그라운드에서 계속된다
        await asyncio.sleep(3)

        # 실시간 수신 중 REST 호출 — 별도 스레드에서 실행해 수신을 막지 않는다
        await asyncio.to_thread(call_api, "/krstock/quote/v1/currentPrice", {"Input_0": {
            "iem_cd": IEM_CD,
            "market_cd": "UNT",     # 시장: UNT(통합)/KRX/NXT
        }})
        await asyncio.sleep(3)

        await send(ws, "2")     # 해제
        await asyncio.sleep(1)  # 해제 응답 확인
        receiver.cancel()
    print("\n실시간 해제 후 종료합니다.")


asyncio.run(realtime())
