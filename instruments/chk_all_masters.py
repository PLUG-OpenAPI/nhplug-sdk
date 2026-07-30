"""28종 종목마스터 일괄 검증 — 어떤 파일이 성공/실패했는지 리포트.

각 마스터에 대해:
  1) headers/<key>.h 로드 (레이아웃 무결성: @record == 필드 길이합)
  2) @url 에서 .mst 다운로드 (캐시 6시간)
  3) 파일크기 % 레코드크기 == 0 검증
  4) 전 레코드 CP949 파싱 + 도메인 보정 규칙 적용

구조체가 실제 파일과 다르면 3)에서 나머지가 남아 실패로 보고된다.

사용:
    python instruments/chk_all_masters.py              # 전체 28종
    python instruments/chk_all_masters.py m_new_stock m_optksp   # 일부만
    python instruments/chk_all_masters.py --local ./mst          # 포털에서 받은 폴더 사용
"""
import sys
import time
from pathlib import Path

try:  # 설치된 패키지로 실행될 때
    from . import master
except ImportError:  # 저장소에서 스크립트로 직접 실행될 때
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import master  # noqa: E402


def check(key: str, local_dir: Path | None):
    t0 = time.time()
    info = {"key": key, "records": 0, "size": 0, "record_size": 0,
            "fields": 0, "sec": 0.0, "error": ""}
    try:
        lay = master.load_layout(key)
        info["record_size"], info["fields"] = lay.record, len(lay.fields)

        if local_dir:
            path = local_dir / lay.file
            if not path.exists():
                raise FileNotFoundError(f"로컬 파일 없음: {path}")
        else:
            path = master.download(key)

        info["size"] = path.stat().st_size
        rows = master.parse_file(key, path)         # 여기서 배수 검증 + 디코딩
        rows = master.apply_domain_rules(key, rows)  # 보정 규칙까지 통과하는지
        info["records"] = len(rows)
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {e}"
    info["sec"] = time.time() - t0
    return info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    local_dir = None
    if "--local" in sys.argv:
        i = sys.argv.index("--local")
        local_dir = Path(sys.argv[i + 1]) if i + 1 < len(sys.argv) else Path(".")
        args = [a for a in args if a != str(local_dir)]

    keys = args or master.list_masters()
    src = (f"로컬 폴더 {local_dir}" if local_dir
           else f"자동 다운로드(캐시 6h) · {master.instruments_base()}")
    print(f"종목마스터 검증 — {len(keys)}종 · {src}\n")
    print(f"{'마스터':18s} {'상태':4s} {'레코드':>9s} {'크기(B)':>12s} {'RS':>5s} {'필드':>4s}  비고")
    print("-" * 88)

    ok, ng = [], []
    for k in keys:
        r = check(k, local_dir)
        if r["error"]:
            ng.append(r)
            print(f"{k:18s} {'❌':4s} {'-':>9s} {r['size']:>12,d} {r['record_size']:>5d} "
                  f"{r['fields']:>4d}  {r['error'][:44]}")
        else:
            ok.append(r)
            print(f"{k:18s} {'✅':4s} {r['records']:>9,d} {r['size']:>12,d} {r['record_size']:>5d} "
                  f"{r['fields']:>4d}  {r['sec']:.1f}s")

    print("-" * 88)
    print(f"성공 {len(ok)} / 실패 {len(ng)}  (총 {len(keys)}종)")
    if ok:
        print(f"총 레코드 {sum(r['records'] for r in ok):,} 건")
    if ng:
        print("\n■ 실패 목록 (구조체·파일 점검 필요)")
        for r in ng:
            print(f"  - {r['key']}: {r['error']}")
        sys.exit(1)
    print("\n전체 통과 ✅")


if __name__ == "__main__":
    main()
