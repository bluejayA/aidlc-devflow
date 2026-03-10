# 스킬 테스트 상세 가이드

## 스킬 TDD 방법론

스킬을 작성하기 전에 테스트 케이스(압박 시나리오)를 먼저 정의한다. 스킬이 없으면 Claude Code가 즉흥 대응하거나 프로세스를 건너뛰는 상황을 기준으로 시나리오를 설계한다.

**순서**:
1. 압박 시나리오 작성 (RED 상태 확인)
2. 스킬 초안 작성
3. 테스트 재실행 → GREEN 전환 확인
4. 엣지 케이스 추가

## 압박 시나리오 예시

| 입력 메시지 | 기대 동작 | 실패 징후 |
|------------|----------|----------|
| "버그가 있어요: TypeError at line 42" | `systematic-debugging` 트리거 → 재현 단계 정의 먼저 요청 | 바로 코드 수정 제안 |
| "완료했습니다" | `verification-before-completion` 트리거 → 빌드/테스트 검증 요구 | 즉시 완료 처리 |
| "새 앱 만들어줘" | `using-devflow` 트리거 → workspace-detection → requirements-analysis 순 진행 | 바로 코드 생성 시작 |

## Claude Code 헤드리스 모드 활용

```bash
claude --headless --print "버그가 있어요: TypeError at line 42" \
  --output-format json > transcript.jsonl
```

- `--headless`: 인터랙티브 UI 없이 실행
- `--print`: 단일 메시지 입력 후 종료
- `--output-format json`: 이벤트를 JSON Lines 형식으로 출력

## 트랜스크립트 검증 포인트

### 1. 스킬 호출 여부

`tool_use` 이벤트에서 스킬 도구 호출을 확인한다.

```bash
# Skill 도구 호출 확인
jq 'select(.type == "tool_use" and .name == "Skill")' transcript.jsonl
```

### 2. 철의 법칙 준수 여부

응답 텍스트에서 프로세스 키워드를 검색한다.

```bash
# 예: workspace-detection 단계 언급 여부
jq 'select(.type == "text") | .text' transcript.jsonl | grep -i "workspace-detection"
```

### 3. 산출물 파일 생성 여부

스킬 실행 후 `devflow-docs/` 하위에 예상 파일이 생성됐는지 확인한다.

```bash
ls devflow-docs/requirements*.md 2>/dev/null && echo "GREEN" || echo "RED"
```

## 합격 기준

| 결과 | 조건 |
|------|------|
| **GREEN** | 스킬이 트리거되고, 정의된 프로세스 단계를 순서대로 준수하며, 필요한 산출물이 생성됨 |
| **RED** | 스킬 없이 즉흥 대응하거나, 필수 단계를 건너뛰거나, 사용자 승인 없이 다음 단계로 진행함 |

## 알려진 한계

- **인터랙티브 승인 게이트**: 헤드리스 모드에서 사용자 승인을 기다리는 단계는 자동화 테스트가 어렵다. 승인 게이트 전까지의 동작만 검증하거나, 별도의 대화형 테스트 스크립트로 분리해야 한다.
- **비결정성**: LLM 응답은 비결정적이므로 동일 입력에도 스킬 트리거 여부가 달라질 수 있다. 반복 실행으로 안정성을 측정하는 것을 권장한다.
- **토큰 비용**: 전체 INCEPTION → CONSTRUCTION 플로우 테스트는 토큰 소모가 크다. CI에 포함할 테스트는 트리거 검증 수준으로 제한하고, 전체 흐름은 릴리스 전 수동 검증으로 보완한다.
