#!/usr/bin/env python3
"""문서·코드 일관성 검사 — 명세 사실이 여러 파일에 흩어져 어긋나는 것을 잡는다.

**코드를 정본으로 삼아 문서를 검증한다.** 같은 사실이 10곳 넘게 복사돼 있어
한 곳만 고치면 조용히 어긋나는 문제가 반복됐다(실제 사례: AGENTS.md 상단은
성공코드 4종으로 고쳤는데 안전규칙 절은 `00000` 인 채 남음).

사용:
    python scripts/check_consistency.py              # nhplug-sdk 검사
    python scripts/check_consistency.py --all        # 형제 저장소(mcp·프로필)까지
    python scripts/check_consistency.py --repo ../nhplug-mcp

종료코드: 0 통과 · 1 실패
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parent.parent
WS = SDK.parent  # 워크스페이스 루트(형제 저장소 탐색용)

DOC_EXT = {".md", ".mdc", ".example", ".txt"}
CODE_EXT = {".py", ".ts", ".mjs"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "dist", "build", ".cache"}

results: list[tuple[bool, str, str]] = []  # (ok, 항목, 상세)
roots_cache: list[Path] = []   # check_python_version 이 문서 전체를 훑을 때 쓴다


def add(ok: bool, item: str, detail: str = "") -> None:
    results.append((ok, item, detail))


SELF = Path(__file__).resolve()


def files(root: Path, exts: set[str]):
    """SKIP_DIRS 를 가지치기하며 순회한다(rglob 은 큰 폴더까지 다 훑어 느림).

    검사 스크립트 자신은 제외한다 — 검사 대상 키워드를 코드에 담고 있어 항상 걸린다.
    """
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix in exts and p.resolve() != SELF:
                yield p


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(WS))
    except ValueError:
        return str(p)


# ─────────────────────────────────────────────── 1. 성공코드
def check_success_codes(roots: list[Path]) -> None:
    src = SDK / "nhplug" / "client.py"
    m = re.search(r"DEFAULT_SUCCESS_CODES\s*=\s*\(([^)]+)\)", src.read_text(encoding="utf-8"))
    if not m:
        add(False, "성공코드", f"{rel(src)} 에서 DEFAULT_SUCCESS_CODES 를 찾지 못함")
        return
    codes = re.findall(r'"(\d+)"', m.group(1))
    truth = " · ".join(codes)

    # 판정 규칙: "00000" 을 말하면서 **가장 빠뜨리기 쉬운 코드**를 함께 말하지 않으면 낡음.
    #   기준 코드 = 00000 을 제외한 나머지 중 마지막(현재 13578). 실제로는 00221 누락이 반복됐으므로
    #   "00000 을 언급한 줄은 00221 도 함께 언급해야 한다" 를 최소 조건으로 본다.
    key = "00221" if "00221" in codes else (codes[-1] if codes else "")
    bad = []
    for root in roots:
        for p in files(root, DOC_EXT | CODE_EXT):
            # 테스트는 코드값을 '픽스처'로 쓴다(성공/실패 케이스). 문서 주장이 아니므로 제외.
            if "tests" in p.parts:
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if "00000" not in line or key in line:
                    continue                      # 최신 코드를 인지한 줄 — 정상
                if "NHPLUG_SUCCESS_CODES=" in line:
                    continue                      # 환경변수 예시
                if "00000000000" in line:
                    continue                      # 계좌번호 자리표시자
                if "tr_type" in line or "WSS" in line or "WS_ACK" in line:
                    continue                      # WebSocket 구독응답 — REST 성공코드와 별개 체계
                bad.append(f"{rel(p)}:{i}  {line.strip()[:72]}")
    add(not bad, f"성공코드 ({truth})",
        "\n".join(f"      {b}" for b in bad) if bad else f"코드 정본과 문서 일치")


# ─────────────────────────────────────────────── 2. WebSocket 포트
def check_ws_ports(roots: list[Path]) -> None:
    src = SDK / "nhplug" / "realtime.py"
    ports = dict(re.findall(r'PORT_(\w+)\s*=\s*"(\d+)"', src.read_text(encoding="utf-8")))
    if not ports:
        add(False, "WS 포트", f"{rel(src)} 에서 PORT_* 를 찾지 못함")
        return
    known = set(ports.values())
    bad = []
    for root in roots:
        for p in files(root, DOC_EXT | CODE_EXT):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                for found in re.findall(r"wss://[^\s`\"']*:(\d{4,5})", line):
                    if found not in known:
                        bad.append(f"{rel(p)}:{i}  포트 {found} (정본: {'·'.join(sorted(known))})")
    add(not bad, f"WS 포트 ({'·'.join(f'{k.lower()} {v}' for k, v in ports.items())})",
        "\n".join(f"      {b}" for b in bad) if bad else "코드 정본과 문서 일치")


# ─────────────────────────────────────────────── 3. 종목마스터 수
def check_master_count(roots: list[Path]) -> None:
    n = len(list((SDK / "instruments" / "headers").glob("*.h")))
    bad = []
    for root in roots:
        for p in files(root, DOC_EXT):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if not ("마스터" in line or "instruments" in line or ".mst" in line):
                    continue
                if "성공코드" in line or "코드 4종" in line:
                    continue          # "성공코드 4종" 등 — 마스터 수가 아님
                for claim in re.findall(r"(\d+)\s*종(?=[^\w]|$)", line):
                    if int(claim) != n:
                        bad.append(f"{rel(p)}:{i}  '{claim}종' (실제 {n}종)")
    add(not bad, f"종목마스터 수 ({n}종)",
        "\n".join(f"      {b}" for b in bad) if bad else "문서 표기와 실제 파일 수 일치")


# ─────────────────────────────────────────────── 4. devapi 잔존
def check_devapi(roots: list[Path]) -> None:
    bad = []
    for root in roots:
        for p in files(root, DOC_EXT | CODE_EXT | {".json"}):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if "devapi" in txt:
                for i, line in enumerate(txt.splitlines(), 1):
                    if "devapi" in line:
                        bad.append(f"{rel(p)}:{i}")
    add(not bad, "devapi 폐지",
        "\n".join(f"      {b}" for b in bad) if bad else "잔존 0건")


# ─────────────────────────────────────────────── 5. 상대 링크
def check_links(roots: list[Path]) -> None:
    bad = []
    for root in roots:
        for p in files(root, {".md", ".mdc"}):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                for target in re.findall(r"\]\(([^)\s]+)\)", line):
                    if target.startswith(("http", "#", "mailto:")):
                        continue
                    t = (p.parent / target.split("#")[0]).resolve()
                    if not t.exists():
                        bad.append(f"{rel(p)}:{i}  → {target}")
    add(not bad, "상대 링크",
        "\n".join(f"      {b}" for b in bad) if bad else "전부 유효")


# ─────────────────────────────────────────────── 6. 버전 일치
def check_version() -> None:
    ver_toml = re.search(r'^version\s*=\s*"([^"]+)"',
                         (SDK / "pyproject.toml").read_text(encoding="utf-8"), re.M)
    ver_init = re.search(r'__version__\s*=\s*"([^"]+)"',
                         (SDK / "nhplug" / "__init__.py").read_text(encoding="utf-8"))
    a = ver_toml.group(1) if ver_toml else "?"
    b = ver_init.group(1) if ver_init else "?"
    add(a == b, f"버전 표기 ({a})",
        "pyproject.toml 과 __init__.py 일치" if a == b
        else f"      pyproject={a}  __init__={b}")


# ─────────────────────────────────────────────── 7. MCP 번들 op 수
def check_mcp_ops(mcp: Path | None) -> None:
    if not mcp or not (mcp / "specs").is_dir():
        return
    n = 0
    for f in (mcp / "specs").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        n += sum(1 for _, ops in d.get("paths", {}).items()
                 for _, op in ops.items()
                 if isinstance(op, dict) and op.get("operationId"))
    readme = (mcp / "README.md").read_text(encoding="utf-8", errors="ignore")
    claims = [int(c) for c in re.findall(r"REST\s*(\d+)개", readme)]
    bad = [f"README 'REST {c}개' (실제 {n}개)" for c in claims if c != n]
    add(not bad, f"MCP 엔드포인트 수 ({n}개)",
        "\n".join(f"      {b}" for b in bad) if bad else "README 표기와 번들 일치")


# ─────────────────────────────────────────────── 8. 허용 호스트 (SDK ↔ MCP)
def check_allowed_hosts(mcp: Path | None) -> None:
    """자격증명이 나가는 허용 호스트 목록이 SDK 와 MCP 에서 같은지.

    같은 목록을 파이썬·타입스크립트 두 벌로 들고 있어 한쪽만 고치면
    조용히 어긋난다(한쪽에서 막히고 다른 쪽에서 통과하는 상태).
    """
    def hosts_in(path: Path, var: str) -> list[str]:
        m = re.search(rf"{var}\s*[:=]?\s*[=]\s*[\(\[](.*?)[\)\]]",
                      path.read_text(encoding="utf-8"), re.S)
        return sorted(re.findall(r'"([a-z0-9.\-]+\.[a-z]{2,})"', m.group(1))) if m else []

    sdk_hosts = hosts_in(SDK / "nhplug" / "auth.py", "ALLOWED_HOSTS")
    if not sdk_hosts:
        add(False, "허용 호스트", "nhplug/auth.py 에서 ALLOWED_HOSTS 를 찾지 못함")
        return
    if not mcp or not (mcp / "src" / "config.ts").is_file():
        add(True, f"허용 호스트 ({len(sdk_hosts)}종)", " · ".join(sdk_hosts))
        return

    mcp_hosts = hosts_in(mcp / "src" / "config.ts", "ALLOWED_HOSTS")
    same = sdk_hosts == mcp_hosts
    add(same, f"허용 호스트 ({len(sdk_hosts)}종)",
        " · ".join(sdk_hosts) if same else
        f"      SDK: {sdk_hosts}\n      MCP: {mcp_hosts}")


# ─────────────────────────────────────────────── 9. 최소 파이썬 버전
#: pyproject 의 requires-python 을 정본으로, 문서 표기와 3.11+ 전용 문법 사용을 함께 본다.
#: ⚠️ 실측: 3.10 에서 전 기능 동작 확인(2026-08). 아래 API 를 쓰면 3.10 이 조용히 깨진다.
PY311_ONLY = ("tomllib", "typing import Self", "ExceptionGroup", "TaskGroup",
              "asyncio.timeout", "StrEnum", "except*")


def check_python_version() -> None:
    m = re.search(r'requires-python\s*=\s*">=(\d+\.\d+)"',
                  (SDK / "pyproject.toml").read_text(encoding="utf-8"))
    if not m:
        add(False, "최소 파이썬 버전", "pyproject.toml 에서 requires-python 을 찾지 못함")
        return
    ver = m.group(1)
    bad = []

    # ① classifier 에 해당 버전이 있는지
    if f'Python :: {ver}"' not in (SDK / "pyproject.toml").read_text(encoding="utf-8"):
        bad.append(f"pyproject.toml classifiers 에 'Python :: {ver}' 누락")

    # ② 문서가 다른 버전을 말하는지
    for root in roots_cache:
        for p in files(root, DOC_EXT):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                for claim in re.findall(r"Python\s*(\d+\.\d+)\s*이상", line):
                    if claim != ver:
                        bad.append(f"{rel(p)}:{i}  'Python {claim} 이상' (정본 {ver})")

    # ③ 상위 버전 전용 문법·API 사용
    for pat in PY311_ONLY:
        for p in files(SDK / "nhplug", {".py"}):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if pat in line and "PY311_ONLY" not in line:
                    bad.append(f"{rel(p)}:{i}  3.11+ 전용 '{pat}'")

    add(not bad, f"최소 파이썬 버전 ({ver})",
        "\n".join(f"      {b}" for b in bad) if bad
        else f"classifier·문서·문법 모두 {ver} 기준과 일치")


# ─────────────────────────────────────────────── 10. AI 탐색성 (/tree/ 링크)
#: GitHub robots.txt 는 폴더 목록(/tree/)을 크롤러에 막는다(2026-08 실측).
#: AI 는 /blob/ 와 raw.githubusercontent 만 읽을 수 있으므로, 폴더를 가리키려면
#: 그 안의 README.md 를 /blob/ 로 가리켜야 한다. 안 그러면 AI 에게 그 폴더는 없는 것과 같다.
def check_tree_links(roots: list[Path]) -> None:
    pat = re.compile(r"github\.com/[^)\s\"']*/tree/[^)\s\"']*")
    bad = []
    for root in roots:
        for p in files(root, DOC_EXT | CODE_EXT):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                for m in pat.findall(line):
                    bad.append(f"{rel(p)}:{i}  {m}")
    add(not bad, "AI 탐색성 (/tree/ 링크 금지)",
        "\n".join(f"      {b}  → /blob/<폴더>/README.md 로 바꿀 것" for b in bad) if bad
        else "폴더 링크 0건 — 전부 /blob/ 또는 상대경로")


# ─────────────────────────────────────────────── 11. 고객 노출 연락처·계정
# 문의 접수는 apisupport@nhsec.com 으로만 받는다. GitHub 계정만 PLUG-OpenAPI 로 이전됐고
# 이메일은 바뀌지 않았다. 실제로 0.2.0 배포 때 plugsupport@ 가 PyPI 에 노출된 적 있다.
SUPPORT_EMAIL = "apisupport@nhsec.com"
FORBIDDEN_PUBLIC = (
    "plugsupport@nhsec.com",        # 문의 접수 주소가 아님 (GitHub 로그인용)
    "github.com/plug-support",      # 차단된 옛 계정
    "github:plug-support/",
    "github.com/nhsec/",            # 실재하지 않는 조직
)


def check_public_contacts(roots: list[Path]) -> None:
    bad = []
    for root in roots:
        for p in files(root, DOC_EXT | CODE_EXT | {".toml", ".json"}):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for n, line in enumerate(text.splitlines(), 1):
                for pat in FORBIDDEN_PUBLIC:
                    if pat in line:
                        bad.append(f"{rel(p)}:{n}  {pat}")
    add(not bad, f"고객 노출 연락처·계정 ({SUPPORT_EMAIL})",
        "\n".join(f"      {b}" for b in bad) if bad
        else f"금지 표기 0건 (plugsupport@ · plug-support · nhsec/)")


# ─────────────────────────────────────────────── 10. 커밋 위생
def check_hygiene(roots: list[Path]) -> None:
    import subprocess
    bad = []
    for root in roots:
        if not (root / ".git").is_dir():
            continue
        try:
            out = subprocess.run(
                ["git", "--no-optional-locks", "ls-files"],
                cwd=root, capture_output=True, text=True, timeout=20).stdout
        except Exception:
            continue
        for line in out.splitlines():
            if re.search(r"(^|/)\.env$|\.mst$|^dist/|\.egg-info/", line):
                bad.append(f"{root.name}/{line}")
    add(not bad, "커밋 위생 (.env·.mst·dist)",
        "\n".join(f"      {b}" for b in bad) if bad else "추적 대상 0건")


# ─────────────────────────────────────────────── main
def main() -> int:
    args = sys.argv[1:]
    roots = [SDK]
    mcp = None
    if "--all" in args:
        # org-profile = 조직 대문 클론(PLUG-OpenAPI/.github). 정본은 profile/README.md.
        for name in ("nhplug-mcp", "org-profile"):
            p = WS / name
            if p.is_dir():
                roots.append(p)
        mcp = WS / "nhplug-mcp"
    while "--repo" in args:
        i = args.index("--repo")
        p = Path(args[i + 1]).resolve()
        roots.append(p)
        if p.name == "nhplug-mcp":
            mcp = p
        del args[i:i + 2]

    roots_cache[:] = roots
    print(f"일관성 검사 — 대상 {len(roots)}개 저장소\n" + "─" * 66)

    check_success_codes(roots)
    check_ws_ports(roots)
    check_master_count(roots)
    check_devapi(roots)
    check_links(roots)
    check_version()
    check_mcp_ops(mcp)
    check_allowed_hosts(mcp)
    check_python_version()
    check_tree_links(roots)
    check_public_contacts(roots)
    check_hygiene(roots)

    fails = 0
    for ok, item, detail in results:
        print(f"{'✅' if ok else '❌'} {item}")
        if detail:
            print(detail if detail.startswith("      ") else f"      {detail}")
        if not ok:
            fails += 1

    print("─" * 66)
    if fails:
        print(f"실패 {fails}건 — 위 파일을 확인하세요.")
        print("참고: 명세 사실이 박제된 위치 목록은 워크스페이스 CLAUDE.md 참조")
        return 1
    print(f"전체 통과 ✅  ({len(results)}개 항목)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
