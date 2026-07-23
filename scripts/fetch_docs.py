#!/usr/bin/env python3
"""도메인(정본)에서 최신 API 명세를 docs/ 로 내려받는다.

정본(SSOT)은 도메인입니다:
  - https://www.nhplug.com/llms.txt
  - https://www.nhplug.com/openapi-docs/<자산>/{openapi.json, overview.md, README.md}

이 스크립트로 받은 docs/ 사본은 .gitignore 처리되어 커밋되지 않습니다(항상 최신 유지).
사용:  python scripts/fetch_docs.py
"""
import os
import sys
import urllib.request
import urllib.error

BASE = "https://www.nhplug.com"
ASSETS = ["common", "krstock", "gbstock", "krfuture", "gbfuture", "krbond", "krgold"]
FILES = ["openapi.json", "overview.md", "README.md"]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


def fetch(url: str, dest: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nhplug-sdk/fetch_docs"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  ✗ {url} — {e}")
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    print(f"  ✓ {os.path.relpath(dest, ROOT)} ({len(data):,} bytes)")
    return True


def main() -> None:
    print(f"정본 도메인에서 명세를 내려받습니다: {BASE}")
    ok = fetch(f"{BASE}/llms.txt", os.path.join(DOCS, "llms.txt"))
    for asset in ASSETS:
        for name in FILES:
            ok &= fetch(f"{BASE}/openapi-docs/{asset}/{name}", os.path.join(DOCS, asset, name))
    print("\n완료 ✅  (docs/ 는 .gitignore 처리되어 커밋되지 않습니다)" if ok
          else "\n일부 파일 실패 ✗  네트워크·URL 을 확인하세요")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
