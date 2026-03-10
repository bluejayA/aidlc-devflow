# 스킬 통합 테스트

## 목적

devflow 스킬이 예상대로 트리거되고 동작하는지 검증한다. 스킬이 정의한 "철의 법칙"과 프로세스를 Claude Code가 실제로 준수하는지 확인하는 것이 핵심이다.

## 테스트 구조

```
tests/
├── README.md                    # 이 파일
├── skill-triggering/            # 스킬 자동 트리거 테스트
│   └── test-using-devflow.sh
├── explicit-skill-requests/     # 명시적 스킬 호출 테스트
│   └── test-systematic-debugging.sh
└── subagent-driven-dev/        # 서브에이전트 개발 흐름 테스트
    └── test-full-flow.sh
```

## 테스트 실행 방법

```bash
# 단일 테스트
bash tests/skill-triggering/test-using-devflow.sh

# 전체 테스트 (향후)
bash tests/run-all.sh
```

## 테스트 방식

Claude Code 헤드리스 모드로 실제 세션을 실행한 뒤, 트랜스크립트를 파싱해 스킬 준수 여부를 검증한다.

- **헤드리스 모드**: `claude --headless --print "..."` 로 세션 실행
- **트랜스크립트**: `.jsonl` 형식으로 출력, 이벤트 단위로 파싱
- **검증**: 예상 동작 vs 실제 동작 비교

## 테스트 작성 가이드

1. **압박 시나리오 정의**: 스킬이 없으면 반드시 실패하는 상황을 먼저 설계한다.
2. **헤드리스 세션 실행**: `claude --headless --print` 로 입력을 주입하고 트랜스크립트를 수집한다.
3. **트랜스크립트 파싱**: `.jsonl`에서 `tool_use` 이벤트, 텍스트 키워드, 파일 생성 여부를 확인한다.
4. **합격/불합격 판정**: GREEN(스킬 준수) / RED(즉흥 대응 또는 프로세스 스킵) 로 결과를 출력한다.

### 압박 시나리오 예시

| 입력 메시지 | 기대 스킬 |
|------------|----------|
| "버그가 있어요: TypeError at line 42" | `systematic-debugging` 트리거 |
| "완료했습니다" | `verification-before-completion` 트리거 |
| "새 앱 만들어줘" | `using-devflow` 트리거 → INCEPTION 페이즈 시작 |

## 비용 안내

전체 플로우 테스트(`subagent-driven-dev/`)는 토큰 소모가 크다. 주요 스킬 트리거 검증에 집중하고, 전체 INCEPTION → CONSTRUCTION 흐름은 필요할 때만 선별 실행하길 권장한다.
