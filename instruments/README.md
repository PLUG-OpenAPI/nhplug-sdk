# 종목마스터(.mst) — 구조체 문서 + 파서

NH투자증권이 배포하는 **종목마스터 파일 28종**을 파싱하는 샘플입니다.

> ## 🔴 구조체 정본은 포털입니다
>
> ```
> https://www.nhplug.com/instruments/<파일명>.h      (N2: www.n2plug.com)
> ```
>
> `.mst` 와 **1:1 대응**합니다 — `m_new_stock.mst` → `m_new_stock.h`. **인증 불필요.**
> 포털 `.h` 에는 양 브랜드 URL·파이썬 파서 코드·`pandas` 사용 금지 경고·C 컴파일 타임 크기 검증이 들어 있습니다.

- **`headers/*.h`** — 위 포털 정본의 **동봉 사본**(28종). 파서가 **오프라인에서도** 동작하도록 패키지에 함께 넣은 것입니다.
- **`master.py`** — `.h` 를 **읽어서** 동작하는 파서. 문서와 코드가 어긋날 수 없습니다.
- **`chk_all_masters.py`** — 28종 일괄 검증(성공/실패 리포트).
- `tools/build_headers.py` — 통합명세서(엑셀) → `.h` 생성기(관리자용).

> ⚠️ **동봉 사본과 포털이 다르면 포털이 맞습니다.** 파싱이 실패하면(`파일크기 % 레코드크기 != 0`)
> 포털 `.h` 를 먼저 확인하세요. 구조체가 개정됐을 수 있습니다.

> `.mst` 원본은 저장소에 포함하지 않습니다. 매일 갱신되는 데이터라 포털이 정본입니다.
> 다운로드는 **인증이 필요 없습니다** — 토큰·`x-client-*` 헤더 없이 공개 접근입니다.

## 빠른 시작

**설치해서 쓰기 (권장)**

```bash
pip install "nhplug[instruments]"   # pandas 포함. 그냥 nhplug 만 설치하면 dict 리스트 반환
```

```python
from nhplug.instruments import load_master, list_masters

list_masters()                    # 28종 키 목록
df = load_master("m_new_stock")   # 자동 다운로드(캐시 6h) → 파싱
```

**저장소에서 직접 실행**

```bash
pip install pandas          # 선택. 없으면 dict 리스트로 반환
python master.py m_new_stock
```

> 캐시는 `~/.nhplug/instruments/<도메인>/` 에 저장됩니다(`NHPLUG_INSTRUMENTS_CACHE_DIR` 로 변경 가능).

### 브랜드(도메인) — 나무 / N2

마스터 파일은 브랜드별로 다른 도메인에서 배포됩니다. `.h` 의 `@url` 은 **나무 기준**이므로 N2 고객은 기준 URL 을 바꿔 주세요.

| 브랜드 | 다운로드 기준 URL | 설정 |
|---|---|---|
| 나무(Namuh) | `https://www.nhplug.com/instruments` | 기본값 (설정 불필요) |
| N2 | `https://www.n2plug.com/instruments` | `NHPLUG_INSTRUMENTS_BASE` 지정 |

```bash
# N2 고객
export NHPLUG_INSTRUMENTS_BASE=https://www.n2plug.com/instruments   # Windows: set / $env:
python chk_all_masters.py
```

> 캐시는 도메인별 폴더로 분리되므로 브랜드를 바꿔도 파일이 섞이지 않습니다. 파일 구조체(`.h`)는 두 브랜드 공용입니다.

```python
from master import load_master, list_masters

list_masters()                       # 제공 중인 28종 키 목록
df = load_master("m_new_stock")      # 자동 다운로드(캐시 6h) → 파싱 → DataFrame
df = load_master("m_optksp")         # 지수옵션 (행사가 자동 /100)

# 포털에서 직접 받은 파일을 쓰는 경우
df = load_master("m_new_stock", path="./m_new_stock.mst")
```

## 전체 검증

```bash
python chk_all_masters.py                    # 28종 전부
python chk_all_masters.py m_new_stock m_optksp   # 일부만
python chk_all_masters.py --local ./mst          # 포털에서 받은 폴더 사용
```

레코드 크기가 실제 파일과 맞지 않으면 해당 마스터가 ❌ 로 보고됩니다(구조체·파일 점검 필요).

## 파서가 대신 처리해 주는 것 (⚠️ 직접 짤 때 자주 틀리는 부분)

| 함정 | 파서 동작 |
|---|---|
| 지수옵션 `sPrice` 는 **실제 행사가 ×100** | `strike_price` 컬럼에 `/100` 적용 (`m_optksp·moption·soption·woption·qoption`) |
| 주식옵션 `m_optstp` `sValue` 는 **스케일 없음** | `/100` 을 **적용하지 않음** |
| 위클리옵션 `sMonth` 는 **YYMMWW(주차)** | `expiry_yy·expiry_mm·expiry_week` 로 분해 (날짜 오파싱 방지) |
| 콜풋은 **CP949 한글 2바이트**("콜"/"풋") | `call_put` = `C`/`P` |
| 지수 편입은 **`== "Y"` 로만** 판정 | `is_krx100·is_krx300·is_kospi50·is_kospi100·is_kosdaq150` (공백은 False) |
| 한글종목명 선두 마커 `*`(KOSPI200)·`#`(코스닥150) | `index_marker` 분리, `name` 은 마커 제거본 |
| 파일이 손상되거나 구조체가 다름 | `파일크기 % 레코드크기 != 0` 이면 **즉시 실패** |

원문 필드는 그대로 두고 파생 컬럼을 추가하므로 손실이 없습니다.

## 공통 규칙 (전 파일 적용)

- `#pragma pack(1)` — 패딩 없음. `sizeof` = 항목길이 합계
- 파일 헤더 없음. 0번 오프셋부터 첫 레코드
- 고정 길이. **레코드수 = 파일크기 ÷ 레코드크기, 나머지는 반드시 0**
- 인코딩 **CP949** (UTF-8 아님)
- 좌측정렬 + 공백(0x20) 우측 패딩
- 레코드 끝 1바이트 **LF(0x0A)** — CRLF 아님
- 반드시 **`"rb"`(바이너리)** 로 열 것 — 텍스트 모드는 CRLF 축약·0x1A EOF 로 레코드가 어긋남
- NUL 종료 문자열이 **아님** → `strlen` 금지, 길이 기반 슬라이싱 후 우측 공백 제거

## 제공 마스터 (28종)

| 구분 | 마스터 |
|---|---|
| 국내주식 | `m_new_stock` |
| 해외주식 | `m_gtsstock` |
| 국내 선물 | `m_future`·`m_futsp`·`m_starfut`·`m_starfutsp`·`m_stkfut`·`m_stkfutsp`·`m_vfuture`·`m_vfutsp`·`m_mfuture`·`m_mfutsp`·`m_kfuture`·`m_kfutsp`·`m_new_xfuture`·`m_new_xfutsp` |
| 국내 옵션 | `m_optksp`·`m_moption`·`m_soption`·`m_woption`·`m_qoption`·`m_optstp` |
| 해외파생 | `foitem_h`·`fucode_h`·`fucode_fhke_h`·`opcode_h`·`opcode_ohke_h` |
| 국내 장내채권 | `bond_hts` |

각 마스터의 필드 정의는 `headers/<키>.h` 를 보세요. 금현물은 마스터 파일이 없고 전문(`IVOGLDREQ01`)으로 조회합니다.

## 명세가 갱신되면 (관리자용)

**정본은 포털이므로, 포털 `.h` 가 갱신되면 저장소 동봉본도 뒤따라 맞춥니다.**

```bash
python tools/build_headers.py 종목마스터_통합명세서.xlsx   # headers/*.h 재생성
python chk_all_masters.py                                  # 28종 재검증
```

> 동봉본을 갱신했다면 **PyPI 재배포**가 필요합니다 — `.h` 는 패키지에 들어가는 유일한 명세 결합 지점입니다.
> (REST 명세는 패키지에 번들되지 않아 재배포가 필요 없습니다.)
