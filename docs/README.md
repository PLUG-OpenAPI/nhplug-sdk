# docs — API 명세 (AI 컨텍스트 정본)

AI 코딩 도구(Antigravity·Cursor·Claude 등)와 개발자가 참고하는 NH Open API 명세입니다.
이 폴더의 파일이 **저장소에 포함**되어 있어, 클론만 하면 별도 다운로드 없이 바로 컨텍스트로 쓸 수 있습니다.

- `llms.txt`                : 전체 개요·인증·공통 규약 (정본 위치: https://www.nhplug.com/llms.txt)
- `common/openapi.json`     : 토큰 발급·계좌목록 (플랫폼 공통)
- `krstock/openapi.json`    : 국내주식
- `gbstock/ krfuture/ gbfuture/ krbond/ krgold/` : 각 자산군 openapi.json + overview.md + README.md
- `error_codes.md`, `rate_limits.md` : 에러코드·호출제한 (템플릿 — 실제 값으로 보강)

> 원본이 갱신되면 이 폴더의 사본도 함께 갱신하세요. AI 에이전트에게는 "docs 폴더의 명세를 먼저 읽어줘"라고 지시하면 정확도가 올라갑니다.
