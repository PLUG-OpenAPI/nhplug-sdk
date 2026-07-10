# pipeline — 설계 → 검증 → 실행

전략을 코드로 설계하고, 과거 데이터로 검증한 뒤, 검증된 시그널로 주문을 실행하는 파이프라인입니다.
(현재는 골격 — 실동작 MVP는 다음 단계에서 추가)

```
strategy_builder/  전략 정의(yaml) → BUY/SELL/HOLD 시그널 생성
backtester/        과거 데이터로 시그널 검증 + 리포트
runner/            검증된 전략을 실계좌/모의계좌에 실행 (사람/스케줄러가 구동)
```

## 설계 원칙
- 실행 계층(runner)은 결정론적 코드가 담당한다. 대화형 LLM은 설계·분석·준비까지만.
- 기본 환경은 모의투자. 실거래 전환은 명시적으로, 주문 전 로그·에러코드 확인.

## MVP 로드맵
1. `strategy_builder`: 골든크로스(5/20 이동평균) 전략 정의 + 시그널 함수
2. `backtester`: 일봉 데이터로 단순 수익률 백테스트 + 결과 출력
3. `runner`: 시그널 → `examples/krstock` 의 cash_buy/cash_sell 호출
