"""국내주식 통합 함수 모음 (REST). nhplug 공용 클라이언트 사용."""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from nhplug import call


def current_price(iem_cd: str, market_cd: str = "KRX") -> dict:
    return call("/krstock/quote/v1/currentPrice", {"iem_cd": iem_cd, "market_cd": market_cd})


def balance(act_no: str, aly_qut_cd: str = "1") -> dict:
    """국내주식 잔고. aly_qut_cd 는 필수(1=정규장 / 2=전체장) — 명세 260911."""
    return call("/krstock/inquiry/v1/balance", {
        "act_no": act_no, "bnc_bse_cd": "5", "ltg_aot_dit_cd": "9",
        "aet_bse": "2", "qut_dit_cd": "UNT", "aly_qut_cd": aly_qut_cd,
    })


def list_accounts() -> dict:
    return call("/n2/acctinfo", {})


def cash_buy(act_no: str, iem_cd: str, orr_qty: int, orr_pr: int | None = None) -> dict:
    is_market = orr_pr is None
    inp = {
        "act_no": act_no, "iem_cd": iem_cd, "orr_qty": orr_qty,
        "nmn_pr_tp_cd": "05" if is_market else "01",
        "orr_cnd_dit_cd": "00", "ssl_nmn_pr_dit_cd": "00",
        "rmt_mkt_cd": "KRX", "sor_mkt_sli_yn": "N",
    }
    if not is_market:
        inp["orr_pr"] = orr_pr
    return call("/krstock/order/v1/cashBuy", inp)


def cash_sell(act_no: str, iem_cd: str, orr_qty: int, orr_pr: int | None = None) -> dict:
    is_market = orr_pr is None
    inp = {
        "act_no": act_no, "iem_cd": iem_cd, "orr_qty": orr_qty,
        "nmn_pr_tp_cd": "05" if is_market else "01",
        "orr_cnd_dit_cd": "00", "ssl_nmn_pr_dit_cd": "00",
        "rmt_mkt_cd": "KRX", "sor_mkt_sli_yn": "N",
    }
    if not is_market:
        inp["orr_pr"] = orr_pr
    return call("/krstock/order/v1/cashSell", inp)
