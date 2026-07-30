"""설정 파일(.env) 로딩 — 한 곳만 고치면 모든 코드에 적용되도록.

탐색 순서 (먼저 설정된 값이 이긴다 · 기존 환경변수는 절대 덮어쓰지 않는다):

  1. 이미 설정된 **실제 환경변수** — CI·컨테이너·`claude_desktop_config.json` 등
  2. `NHPLUG_ENV_FILE` 로 **직접 지정한 파일**
  3. **프로젝트 `.env`** — 현재 작업 폴더(CWD)에서 위로 올라가며 탐색
  4. **전역 `~/.nhplug/.env`** — 한 번 만들어 두면 모든 프로젝트에 공통 적용

즉 평소에는 `~/.nhplug/.env` 하나만 관리하고, 특정 프로젝트만 다르게 쓰고 싶을 때
그 폴더에 `.env` 를 두면 그쪽이 우선한다.

⚠️ 왜 CWD 기준인가: `load_dotenv()` 를 인자 없이 호출하면 **호출한 파일의 위치**부터
탐색한다. 패키지가 설치되면 그 위치가 `site-packages/nhplug/` 라서 사용자의 `.env` 를
영영 찾지 못한다. 그래서 명시적으로 CWD 기준으로 찾는다.
"""
from __future__ import annotations

import os
from pathlib import Path

ENV_FILE_VAR = "NHPLUG_ENV_FILE"
GLOBAL_ENV_PATH = Path.home() / ".nhplug" / ".env"

_loaded: list[str] = []


def global_env_path() -> Path:
    """전역 설정 파일 경로 (`~/.nhplug/.env`)."""
    return GLOBAL_ENV_PATH


def loaded_files() -> list[str]:
    """실제로 읽어들인 설정 파일 목록 (진단용)."""
    return list(_loaded)


def load_env(override: bool = False) -> list[str]:
    """설정 파일을 순서대로 읽는다. 읽은 파일 경로 목록을 반환.

    `override=False`(기본)라 **이미 설정된 환경변수는 유지**되고,
    앞 순서에서 채워진 값도 뒤 파일이 덮어쓰지 않는다.
    """
    try:
        from dotenv import find_dotenv, load_dotenv
    except Exception:  # python-dotenv 미설치 — 환경변수만 사용
        return []

    _loaded.clear()
    candidates: list[Path] = []

    explicit = (os.environ.get(ENV_FILE_VAR) or "").strip()
    if explicit:
        candidates.append(Path(explicit).expanduser())

    # 현재 작업 폴더에서 위로 올라가며 .env 탐색 (설치본에서도 동작하도록 usecwd=True)
    found = find_dotenv(usecwd=True)
    if found:
        candidates.append(Path(found))

    candidates.append(GLOBAL_ENV_PATH)

    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen or not path.is_file():
            continue
        seen.add(key)
        load_dotenv(path, override=override)
        _loaded.append(key)
    return list(_loaded)
