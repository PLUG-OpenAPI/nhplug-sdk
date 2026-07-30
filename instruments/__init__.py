"""nhplug.instruments — 종목마스터(.mst) 파서.

구조체 정본은 `headers/<키>.h` 이며, 파서가 그 헤더를 읽어 동작한다
(문서와 코드가 어긋날 수 없는 구조).

사용:
    from nhplug.instruments import load_master, list_masters

    list_masters()                    # 제공 중인 28종 키
    df = load_master("m_new_stock")   # 자동 다운로드(캐시 6h) → 파싱
    df = load_master("m_optksp")      # 지수옵션 (행사가 자동 /100)

    # 포털에서 직접 받은 파일 사용
    df = load_master("m_new_stock", path="./m_new_stock.mst")

브랜드: `.h` 의 @url 은 나무(www.nhplug.com) 기준.
        N2 는 `NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments`.
캐시  : `~/.nhplug/instruments/<도메인>/` (`NHPLUG_INSTRUMENTS_CACHE_DIR` 로 변경)
pandas: 설치돼 있으면 DataFrame, 없으면 dict 리스트를 반환한다.
        `pip install nhplug[instruments]`
"""
from .master import (  # noqa: F401
    DEFAULT_INSTRUMENTS_BASE,
    Field,
    Layout,
    apply_domain_rules,
    download,
    instruments_base,
    list_masters,
    load_layout,
    load_master,
    parse_file,
    resolve_url,
)

__all__ = [
    "load_master", "list_masters", "load_layout", "parse_file",
    "download", "resolve_url", "instruments_base", "apply_domain_rules",
    "Layout", "Field", "DEFAULT_INSTRUMENTS_BASE",
]
