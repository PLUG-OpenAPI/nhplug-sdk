# docs — API 명세는 **도메인이 정본(SSOT)**

NH Open API 명세의 정본은 **도메인**입니다. 이 폴더에는 사본을 커밋하지 않습니다(항상 최신 유지, 재동기화 불필요).

- 전체 개요·인증·공통 규약: **https://www.nhplug.com/llms.txt** (나무) · **https://www.n2plug.com/llms.txt** (N2)
- 자산군별 정본: **https://www.nhplug.com/openapi-docs/&lt;자산&gt;/{openapi.json, overview.md, README.md}** (나무 / N2는 `n2plug.com`)
  - 자산: `common` · `krstock` · `gbstock` · `krfuture` · `gbfuture` · `krbond` · `krgold`
  - 브랜드: API·필드는 동일, **접속 도메인만 다름**(나무 nhplug.com / N2 n2plug.com). 런타임엔 본인 브랜드 도메인을 쓰세요.

## 로컬 사본이 필요하면 (오프라인·AI 컨텍스트용)

```bash
python scripts/fetch_docs.py
```

도메인에서 최신 `llms.txt` + 7개 자산 문서를 이 폴더로 내려받습니다. 받은 파일은 `.gitignore` 처리되어 커밋되지 않습니다.

> AI 에이전트에게는 위 URL 을 직접 컨텍스트로 주거나, `fetch_docs.py` 로 받은 뒤 "docs 폴더의 명세를 먼저 읽어줘"라고 지시하세요.

> 에러 처리 규약(`rsp_cd` `00000`/`00166`=정상, `IGW…` 코드)과 호출 제한은 llms.txt·각 openapi.json 및 포털 정책을 따릅니다.
