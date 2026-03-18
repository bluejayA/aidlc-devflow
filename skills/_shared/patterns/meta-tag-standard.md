# Meta Tag Standard

SKILL.md 파일에 삽입하는 기계 읽기 가능한 메타 태그의 규격을 정의한다.
메타 태그는 HTML 주석(`<!-- -->`)이므로 마크다운 렌더링에 영향을 주지 않는다.

## Tag Types

### @gate

게이트(분기점)를 선언한다. 사용자 선택이 필요한 지점.

```
<!-- @gate: [gate-id] -->
```

- `gate-id`: 고유 식별자 (kebab-case)
- 바로 아래에 `@gate-option` 태그가 따른다

### @gate-option

게이트의 선택지를 정의한다. 각 선택이 어디로 이동하는지 명시.

```
<!-- @gate-option: [option] -> [target] -->
<!-- @gate-option: [option] -> [target] {condition} -->
```

- `option`: 선택지 레이블 (A, B, C 등)
- `target`: 이동 대상 (step-id, gate-id, 또는 외부 스킬명)
- `condition` (선택): 조건 설명 (중괄호로 감싼다)

### @step

스킬 내부의 실행 단계를 순서대로 선언한다.

```
<!-- @step:[N] id=[step-id] -->
<!-- @step:[N] id=[step-id] skip-when=[mode-name] -->
```

- `N`: 순서 번호 (양의 정수, 단조 증가)
- `step-id`: 고유 식별자 (kebab-case)
- `skip-when` (선택): 이 모드일 때 스텝을 건너뜀

### @condition

조건부 분기를 정의한다. 입력값에 따라 자동으로 다음 단계가 결정되는 지점.

```
<!-- @condition: [condition-expr] -> [target] -->
```

- `condition-expr`: 평가 조건 (예: `complexity==Minimal`)
- `target`: 조건 충족 시 이동 대상

## Placement Rules

1. 태그는 해당 섹션의 **시작** 또는 관련 마크다운 바로 위/아래에 배치
2. `@gate` + `@gate-option`은 함께 그룹으로 배치
3. `@step`은 해당 단계 설명의 시작 부분에 배치
4. `@condition`은 조건 분기 로직 설명 근처에 배치
5. 기존 자연어 내용은 절대 변경하지 않음 — 태그 줄만 추가

## Examples

### 오케스트레이터 게이트 예시

```markdown
### 2. Complexity Declaration Gate
<!-- @gate: complexity-declaration -->
<!-- @gate-option: A -> complexity-declaration {adjust} -->
<!-- @gate-option: B -> requirements-analysis -->
```

### 스텝 순서 예시

```markdown
## The Orchestration Loop
<!-- @step:1 id=workspace-detection -->
<!-- @step:2 id=complexity-declaration -->
<!-- @step:3 id=requirements-analysis -->
```

### 조건부 분기 예시

```markdown
### 4. Pre-Planning 분기
<!-- @condition: complexity==Minimal -> workflow-planning -->
<!-- @condition: complexity==Comprehensive -> user-stories -->
```

## Maintenance

### 태그 변경이 필요한 상황

| 변경 유형 | 예시 | 필요한 태그 수정 |
|-----------|------|-----------------|
| 게이트 추가/삭제 | 새 스테이지 게이트 신설 | `@gate` + `@gate-option` 추가/삭제 |
| 게이트 옵션 변경 | A/B → A/B/C, target 변경 | `@gate-option` 수정 |
| 스텝 순서 변경 | 스테이지 재배치, 새 스텝 삽입 | `@step` 순서 번호 재조정 |
| 조건 분기 변경 | complexity 분기 로직 수정 | `@condition` 수정 |
| 스킬 이름 변경 | 외부 참조 대상 스킬명 변경 | `@gate-option` target 수정 |

### 동기화 검증

SKILL.md 수정 후 `bash tests/run-all.sh` 실행으로 태그 불일치를 검출한다.
테스트가 잡는 문제:
- dead-end: 존재하지 않는 target 참조
- unreachable: 어디서도 도달하지 않는 step/gate
- option 누락: gate에 옵션이 2개 미만
- 순서 위반: step order가 단조 증가하지 않음
- 시나리오 불일치: 라우팅 경로가 기대와 다름

### 현재 태그 적용 범위

- `aidlc-inception-orchestrator/SKILL.md` — 8 steps, 11 gates, 5 conditions
- `aidlc-construction-orchestrator/SKILL.md` — 3 steps, 5 gates
