"""NH투자증권 종목마스터(.mst) 파서 — 헤더(.h) 기반.

설계: **`instruments/headers/*.h` 가 정본**이다. 파서는 그 헤더를 읽어
      필드 오프셋·길이·다운로드 URL·레코드 크기를 얻는다.
      → 문서(.h)와 코드가 어긋날 수 없고, 명세가 바뀌면 .h 만 교체하면 된다.

공통 규칙 (통합명세서 기준, 전 파일 적용)
  - #pragma pack(1) — 패딩 없음. sizeof = 항목길이 합계
  - 파일 헤더 없음. 0번 오프셋부터 첫 레코드
  - 고정 길이. 레코드수 = 파일크기 / 레코드크기, 나머지는 반드시 0
  - 인코딩 CP949 (UTF-8 아님)
  - 좌측정렬 + 공백(0x20) 우측 패딩
  - 레코드 끝 1바이트 LF(0x0A). CRLF 아님
  - 반드시 "rb"(바이너리)로 열 것 — 텍스트 모드는 CRLF 축약·0x1A EOF 로 레코드가 어긋남
  - NUL 종료 문자열 아님 → strlen 금지, 길이 기반 슬라이싱 후 우측 공백 제거

브랜드(도메인)
  마스터 파일은 브랜드별로 다른 도메인에서 배포된다. `.h` 의 @url 은 나무 기준이므로,
  N2 고객은 환경변수로 전환한다(다운로드는 인증 불필요 · 토큰·헤더 없이 공개 접근).
      나무: https://www.nhplug.com/instruments/<파일>.mst   (기본값)
      N2  : NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments

사용:
    from master import load_master, list_masters, download

    df = load_master("m_new_stock")              # 자동 다운로드(캐시) 후 파싱
    df = load_master("m_optksp", apply_rules=True)  # 행사가/100 등 보정 적용(기본)
    df = load_master("m_new_stock", path="m_new_stock.mst")  # 포털에서 받은 파일 사용
"""
from __future__ import annotations

import os
import re
import time
import urllib.request
from dataclasses import dataclass, field as dc_field
from pathlib import Path
from urllib.parse import urlsplit

HEADER_DIR = Path(__file__).resolve().parent / "headers"


def _default_cache_dir() -> Path:
    """마스터 캐시 위치.

    ⚠️ 패키지 폴더 안에 두면 안 된다 — `pip install` 후에는 site-packages 가
    읽기 전용이거나 권한이 없어 다운로드가 실패한다. 사용자 홈을 기본으로 쓴다.
    `NHPLUG_INSTRUMENTS_CACHE_DIR` 로 변경 가능.
    """
    env = (os.environ.get("NHPLUG_INSTRUMENTS_CACHE_DIR") or "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".nhplug" / "instruments"


CACHE_TTL_SEC = 6 * 3600  # 6시간 이내 받은 파일은 재사용

# 마스터 배포 기준 URL. 브랜드(나무/N2) 전환용 — 아래 instruments_base() 참고.
INSTRUMENTS_BASE_ENV = "NHPLUG_INSTRUMENTS_BASE"
DEFAULT_INSTRUMENTS_BASE = "https://www.nhplug.com/instruments"

_META_RE = re.compile(r"^\s*\*\s*@(\w+)\s+(.*?)\s*$")
_FIELD_RE = re.compile(
    r"^\s*char\s+(?P<name>\w+)\s*\[(?P<len>\d+)\]\s*;\s*/\*\s*@(?P<off>\d+)\s+(?P<desc>.*?)\s*\*/\s*$"
)


@dataclass
class Field:
    name: str
    offset: int
    length: int
    desc: str = ""


@dataclass
class Layout:
    """.h 에서 읽어낸 마스터 레이아웃."""
    key: str
    file: str
    url: str
    record: int
    encoding: str = "cp949"
    group: str = ""
    note: str = ""
    fields: list[Field] = dc_field(default_factory=list)

    @property
    def total_length(self) -> int:
        return sum(f.length for f in self.fields)


# ------------------------------------------------------------------ 헤더 로딩

def list_masters() -> list[str]:
    """제공 중인 마스터 키 목록(파일명 stem)."""
    return sorted(p.stem for p in HEADER_DIR.glob("*.h"))


def load_layout(key: str) -> Layout:
    """instruments/headers/<key>.h 를 파싱해 Layout 반환."""
    path = HEADER_DIR / f"{key}.h"
    if not path.exists():
        raise FileNotFoundError(f"헤더 없음: {path}  (사용 가능: {', '.join(list_masters())})")

    meta, fields = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _FIELD_RE.match(line)
        if m:
            fields.append(Field(m["name"], int(m["off"]), int(m["len"]), m["desc"].strip()))
            continue
        m = _META_RE.match(line)
        if m:
            meta.setdefault(m[1], m[2])

    record = int(re.sub(r"[^0-9].*$", "", meta.get("record", "0")) or 0)
    lay = Layout(
        key=key, file=meta.get("file", f"{key}.mst"), url=meta.get("url", ""),
        record=record, encoding=(meta.get("encoding") or "cp949").lower(),
        group=meta.get("group", ""), note=meta.get("note", ""), fields=fields,
    )
    if not lay.fields:
        raise ValueError(f"{key}.h 에서 필드를 찾지 못했습니다(형식 확인 필요)")
    if lay.record != lay.total_length:
        raise ValueError(
            f"{key}.h 레이아웃 불일치: @record {lay.record} != 필드 길이합 {lay.total_length}")
    return lay


# ------------------------------------------------------------------ 다운로드

def instruments_base() -> str:
    """마스터 배포 기준 URL(브랜드별로 다름).

    나무(기본) https://www.nhplug.com/instruments
    N2         NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments
    """
    base = (os.environ.get(INSTRUMENTS_BASE_ENV) or "").strip().rstrip("/")
    if not base:
        return DEFAULT_INSTRUMENTS_BASE
    if urlsplit(base).scheme not in ("http", "https"):
        raise ValueError(
            f"{INSTRUMENTS_BASE_ENV} 는 http(s):// 로 시작해야 합니다: {base!r}"
            f"  (예: https://www.n2plug.com/instruments)"
        )
    return base


def resolve_url(lay: Layout) -> str:
    """이 마스터를 내려받을 실제 URL.

    `.h` 의 @url 은 나무 기준 정본이라 그대로 쓰고, 환경변수로 기준 URL 이
    바뀐 경우(N2 등)에는 파일명만 붙여 재구성한다.
    """
    base = instruments_base()
    if base == DEFAULT_INSTRUMENTS_BASE and lay.url:
        return lay.url
    return f"{base}/{lay.file}"


def download(key: str, dest: Path | None = None, force: bool = False, timeout: int = 60) -> Path:
    """마스터 파일을 내려받아 경로 반환. 기본은 캐시 재사용(인증 불필요).

    URL 은 `.h` 의 @url(나무 기준)이며, N2 는 NHPLUG_INSTRUMENTS_BASE 로 전환한다.
    캐시는 도메인별로 분리해 브랜드를 바꿔도 서로 섞이지 않는다.
    """
    lay = load_layout(key)
    url = resolve_url(lay)
    if not url:
        raise ValueError(f"{key}.h 에 @url 이 없습니다. path= 로 로컬 파일을 지정하세요.")
    dest = dest or (_default_cache_dir() / (urlsplit(url).hostname or "unknown") / lay.file)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if not force and dest.exists() and (time.time() - dest.stat().st_mtime) < CACHE_TTL_SEC:
        return dest

    req = urllib.request.Request(url, headers={"User-Agent": "nhplug-sdk/instruments"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


# ------------------------------------------------------------------ 파싱

def parse_file(key: str, path: str | Path) -> list[dict]:
    """.mst 파일을 레이아웃대로 잘라 dict 리스트로 반환(보정 없음, 원문 문자열)."""
    lay = load_layout(key)
    raw = Path(path).read_bytes()  # 반드시 바이너리
    if lay.record <= 0:
        raise ValueError(f"{key}: 레코드 크기 미정의")
    if len(raw) % lay.record != 0:
        raise ValueError(
            f"{key}: 파일크기 {len(raw):,} 가 레코드크기 {lay.record} 의 배수가 아닙니다"
            f" (나머지 {len(raw) % lay.record}). 파일 손상 또는 레이아웃 불일치."
        )

    rows = []
    enc = lay.encoding
    for i in range(0, len(raw), lay.record):
        rec = raw[i:i + lay.record]
        row = {}
        for f in lay.fields:
            if f.name == "dummy":       # 레코드 종단자(LF)는 제외
                continue
            row[f.name] = rec[f.offset:f.offset + f.length].decode(enc, errors="replace").rstrip()
        rows.append(row)
    return rows


# ------------------------------------------------------------------ 보정 규칙

def apply_domain_rules(key: str, rows: list[dict]) -> list[dict]:
    """통합명세서의 '파싱 시 반드시 지킬 것' 을 코드로 적용한다.

    문서로만 두면 사용자가 그대로 함정에 빠지므로 파서가 미리 처리한다.
    원문은 남기고 파생 컬럼(*_val 등)을 추가하는 방식이라 손실이 없다.
    """
    # 2) 지수옵션 계열 sPrice 는 실제 행사가 x100 → 반드시 /100
    #    (주식옵션 m_optstp 의 sValue 는 스케일 없음 — 적용하지 않는다)
    if key in {"m_optksp", "m_moption", "m_soption", "m_woption", "m_qoption"}:
        for r in rows:
            v = r.get("sPrice", "").strip()
            if v.isdigit():
                r["strike_price"] = int(v) / 100

    # 3) 위클리옵션 sMonth 는 YYMMWW(주차) — 날짜로 파싱 금지
    if key in {"m_woption", "m_qoption"}:
        for r in rows:
            v = r.get("sMonth", "").strip()
            if len(v) == 6 and v.isdigit():
                r["expiry_yy"], r["expiry_mm"], r["expiry_week"] = v[:2], v[2:4], v[4:]

    # 4) 콜풋은 CP949 한글 2바이트("콜"/"풋") — ASCII C/P 아님
    for r in rows:
        cp = r.get("sCallPut", "").strip()
        if cp:
            r["call_put"] = {"콜": "C", "풋": "P"}.get(cp, cp)

    # 5) 지수 편입 플래그는 == "Y" 로만 판정 (공백을 N 으로 오해 금지)
    if key == "m_new_stock":
        for r in rows:
            for src, dst in (("gTonghap", "is_krx100"), ("gKrx300", "is_krx300"),
                             ("gKospi50", "is_kospi50"), ("gKospi100", "is_kospi100"),
                             ("gKosdaq150", "is_kosdaq150")):
                if src in r:
                    r[dst] = (r[src].strip() == "Y")
            # 3) 한글종목명 선두 마커(*: KOSPI200, #: 코스닥150) 는 정렬·검색 시 제거
            nm = r.get("sKorName", "")
            if nm[:1] in ("*", "#"):
                r["index_marker"], r["name"] = nm[0], nm[1:].strip()
            else:
                r["index_marker"], r["name"] = "", nm.strip()
    return rows


# ------------------------------------------------------------------ 공개 API

def load_master(key: str, path: str | Path | None = None, *,
                apply_rules: bool = True, force_download: bool = False):
    """마스터를 읽어 DataFrame(pandas 있으면) 또는 dict 리스트로 반환.

    path 를 주면 그 파일을 쓰고(포털에서 직접 받은 경우), 없으면 @url 에서 자동 다운로드한다.
    """
    src = Path(path) if path else download(key, force=force_download)
    rows = parse_file(key, src)
    if apply_rules:
        rows = apply_domain_rules(key, rows)
    try:
        import pandas as pd
        return pd.DataFrame(rows)
    except ImportError:
        return rows


if __name__ == "__main__":
    import sys
    k = sys.argv[1] if len(sys.argv) > 1 else "m_new_stock"
    lay = load_layout(k)
    print(f"{k}: {lay.group} · {lay.record}B · 필드 {len(lay.fields)}개")
    print(f"  URL: {resolve_url(lay)}")
    data = load_master(k)
    n = len(data)
    print(f"  파싱 완료: {n:,} 건")
    try:
        print(data.head(3).to_string()[:600])
    except AttributeError:
        for r in data[:3]:
            print("  ", r)
