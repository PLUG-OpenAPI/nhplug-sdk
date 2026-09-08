# AI IDE 규칙 템플릿

AI 코딩 도구가 NH투자증권 Open API 를 **정확하게** 다루도록, 프로젝트에 넣어두는 규칙 파일입니다.
규칙이 없으면 AI 가 필드명·성공코드·환경을 **추측**해서 틀린 코드를 만듭니다.

## 어느 파일을 쓰나요?

| 쓰는 도구 | 넣을 파일 | 프로젝트 내 위치 |
|---|---|---|
| **Antigravity** · OpenAI Codex | `AGENTS.md` | 루트 |
| **Claude Code** | `CLAUDE.md` | 루트 |
| **Cursor** | `cursor/nhplug.mdc` | **`.cursor/rules/nhplug.mdc`** |

> 여러 도구를 쓴다면 해당 파일을 모두 두면 됩니다. 서로 충돌하지 않습니다.

## 설치

```bash
# 프로젝트 폴더에서 (Antigravity·Codex)
curl -O https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/AGENTS.md

# Claude Code
curl -O https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/CLAUDE.md

# Cursor
mkdir -p .cursor/rules
curl -o .cursor/rules/nhplug.mdc https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/cursor/nhplug.mdc
```

Windows PowerShell:

```powershell
iwr -useb https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/AGENTS.md -OutFile AGENTS.md

New-Item -ItemType Directory -Force .cursor\rules | Out-Null
iwr -useb https://raw.githubusercontent.com/PLUG-OpenAPI/nhplug-sdk/main/templates/cursor/nhplug.mdc -OutFile .cursor\rules\nhplug.mdc
```

> 파일을 브라우저로 열어 복사해 붙여넣어도 됩니다.

## ⚠️ Cursor 사용자 주의

**레거시 `.cursorrules` 파일은 Cursor Agent 모드에서 무시됩니다.**
반드시 **`.cursor/rules/nhplug.mdc`** 경로로 두세요. 예전 방식으로 두면 규칙이 조용히 적용되지 않습니다.

## 무엇이 들어 있나요

세 파일 모두 같은 내용을 각 도구 형식에 맞춰 담았습니다.

- **SDK 우선** — `pip install nhplug` 로 인증·토큰캐시·에러판정을 맡기고, `requests` 로 직접 짜지 않게
- **명세 정본** — 도메인 `llms.txt` · 자산군 `openapi.json` 을 보게 (필드 추측 방지)
- **성공 판정** — `rsp_msg` 우선. `rsp_cd` 는 API 마다 의미가 달라 단독 판정이 불가하며, 코드값 하드코딩을 막습니다
- **계좌구분** — `01`·`02` 운영 / `03` 모의. 첫 계좌를 그대로 쓰지 않게
- **브랜드** — N2 는 세 줄 모두 전환(하나라도 빠지면 조용히 나무로)
- **주문 필드** — `iem_cd` 6자리(A 없음) · `orr_pr` 정수
- **안전** — 키·토큰 미출력 · 기본은 운영이라 실제 체결 · `dry_run` 기본
- **MCP 혼동 방지** — SDK 는 URI 경로, MCP 는 operationId

## 프로젝트에 맞게 고쳐 쓰세요

이 템플릿은 **출발점**입니다. 프로젝트 고유 규칙(폴더 구조·로깅 방식·테스트 규칙)을 아래에 덧붙이면 AI 가 함께 지킵니다.

## 관련 문서

- [Antigravity·Cursor 로 바이브코딩하기](../guides/antigravity.md) — 설치부터 첫 실행까지
- [SDK README](../README.md) · [저장소 AGENTS.md](../AGENTS.md)
- 명세 정본: [llms.txt](https://www.nhplug.com/llms.txt) (N2: [n2plug](https://www.n2plug.com/llms.txt))
