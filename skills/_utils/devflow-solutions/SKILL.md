---
name: devflow-solutions
description: 디버깅 완료 후 해결 지식을 구조화하여 devflow-docs/solutions/{category}/에 저장한다. systematic-debugging이 근본 원인을 확정한 직후 orchestrator가 호출. STORE 인터페이스로 5개 필드를 받아 Solution-Writer로 개인정보를 제거한 뒤 Knowledge-Librarian이 중복 검사 후 YAML+Markdown 솔루션 파일로 저장한다.
metadata:
  version: 0.1.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
  return_behavior: stop-no-gate
---

# devflow-solutions

<!-- FR-2: 디버깅 해결 지식을 구조화하여 축적. FR-3: 향후 LIST() 인터페이스로 검색 가능. -->
<!-- 출력 언어: 한국어 (Korean) -->

## Purpose

`aidlc-systematic-debugging` 완료 후 orchestrator가 호출하여 해결 지식을 `devflow-docs/solutions/` 에 저장한다.
중복 솔루션을 방지하고, 개인 경로/토큰 등 민감 정보를 scrub한 뒤 표준 포맷으로 보존한다.

---

## Interface

### STORE(5필드)

orchestrator가 이 인터페이스로 호출한다:

```
STORE(
  root_cause:       "근본 원인 한 줄 요약",
  fix_summary:      "수정 내용 한 줄 요약",
  regression_test:  "회귀 테스트명 또는 경로",
  test_result:      "N passed, 0 failed",
  error_message:    "원본 에러 메시지 (raw)"
)
```

### Return

```
Return(
  saved_path:  "devflow-docs/solutions/{category}/{YYYY-MM-DD}-{slug}.md" | null,
  verdict:     "SAVE" | "DUPLICATE" | "REJECT",
  reason:      "판정 이유",
  similar_to:  "유사 솔루션 경로" | null
)
```

### LIST() — BL-057 (미구현)

향후 `LIST(category?, stack?)` 인터페이스로 솔루션 목록 검색 지원 예정.

---

## 디스패치 순서

```
STORE 호출
  └─► Solution-Writer (Privacy Scrub + 포맷 생성)
        └─► Knowledge-Librarian (검증 + 저장)
              └─► Return to orchestrator
```

---

## Solution-Writer (인라인 서브에이전트)

**역할**: 5개 입력 필드를 받아 Privacy Scrubbing 후 YAML frontmatter + Markdown body를 생성한다.

**Tools**: 없음 (tool-less — 텍스트 변환만 수행, REJECT 권한 없음)

### Privacy Scrubbing 치환 규칙

다음 패턴을 치환 후 출력한다. 원본은 보존하지 않는다.

| 패턴 | 치환값 |
|------|--------|
| `/Users/*` 경로 | `<USER_HOME>/` |
| `/home/*` 경로 | `<USER_HOME>/` |
| `token=` 뒤 값 | `<REDACTED>` |
| `Bearer ` 뒤 토큰 | `<REDACTED>` |
| API 키 패턴 (`sk-*`, `ghp_*` 등) | `<REDACTED>` |
| 구체적 사용자명 | `<USERNAME>` |
| 구체적 호스트명 | `<HOSTNAME>` |

### 출력 포맷

Solution-Writer는 다음 포맷의 텍스트를 Knowledge-Librarian에 전달한다:

```markdown
---
title: [error_message에서 추출한 문제 한 줄 요약]
error_signature: [에러 메시지 핵심 패턴]
category: [build | test | runtime | config | dependency]
project_type: [plugin | web | api | cli]
stack: [python | node | go | rust | markdown]
created: [ISO 8601]
last_validated: [ISO 8601]
---

## Problem

[증상 설명 — scrubbed]

## Root Cause

[root_cause 필드 내용]

## Solution

[fix_summary 필드 내용]

## Prevention

[회귀 방지를 위한 제안 — regression_test + test_result 기반]
```

**category 결정 기준**:
- `build`: 빌드/컴파일/패키징 오류
- `test`: 테스트 실패/환경 문제
- `runtime`: 실행 중 예외/크래시
- `config`: 설정 파일/환경변수 오류
- `dependency`: 패키지/버전 충돌

---

## Knowledge-Librarian (인라인 서브에이전트)

**역할**: Solution-Writer 출력을 받아 검증 → 중복 확인 → 저장 결정

**Tools**: Glob, Read, Write

### 검증 순서

1. **Privacy Check** — `<USER_HOME>`, `<REDACTED>`, `<USERNAME>`, `<HOSTNAME>` 치환 여부 확인
   - 실패 시: `REJECT` 반환 (reason: "Privacy scrubbing incomplete — raw path/token detected")

2. **Format Validation** — YAML frontmatter 6개 필드 존재 여부 + ## 섹션 4개 확인
   - 실패 시: `REJECT` 반환 (reason: "Invalid format — missing fields: [목록]")

3. **Tag Validation** — category가 `build|test|runtime|config|dependency`, project_type이 `plugin|web|api|cli`, stack이 `python|node|go|rust|markdown` 중 ��나인지 확인
   - 실패 시: `REJECT` 반환 (reason: "Invalid tag: [field]=[값]")

4. **Duplicate Check** — `devflow-docs/solutions/{category}/` 내 기존 파일 검사
   - `error_signature`가 완전 일치 → `DUPLICATE` 반환, similar_to 설정
   - `error_signature` 유사도 70%+ (핵심 토큰 3개 이상 일치) → `SAVE` + similar_to 설정
   - 중복 없음 → `SAVE`

### 저장 규칙

- **디렉토리 미존재 시**: `devflow-docs/solutions/{category}/` 자동 생성
- **파일명**: `{YYYY-MM-DD}-{slug}.md`
  - `slug`: `error_signature`에서 영어 키워드 2-4단어, 하이픈 연결
  - 예: `2026-03-30-module-not-found-import.md`
- **Write 도구로 신규 파일 생성** — 기존 파일 덮어쓰기 금지

### Duplicate 기준 상세

```
완전 일치:  error_signature가 동일 → DUPLICATE (저장 안 함)
부분 유사:  핵심 단어 3개+ 겹침 → SAVE + similar_to = 기존 파일 경로
차이:       유사도 낮음 → SAVE (similar_to = null)
```

---

## 반환 예시

| verdict | saved_path | reason | similar_to |
|---------|-----------|--------|------------|
| `SAVE` | `devflow-docs/solutions/runtime/2026-03-30-null-pointer-none-type.md` | 새 솔루션 저장 완료 | null |
| `SAVE` | `devflow-docs/solutions/test/2026-03-30-pytest-fixture-scope.md` | 유사 솔루션 존재하나 다른 컨텍스트 | 기존 파일 경로 |
| `DUPLICATE` | null | 동일 error_signature 이미 존재 | 기존 파일 경로 |
| `REJECT` | null | Privacy scrubbing incomplete | null |

---

## 출력 언어

- orchestrator에 반환하는 메시지: **한국어**
- SKILL.md 본문 (내부 로직): 영어
- 솔루션 파일 body: 영어 (에러 메시지 맥락 보존)
- description 필드: 한국어

---

## 동작 규칙

- **REJECT는 비차단적**: 솔루션 저장 실패 시 devflow-audit에 기록 후 워크플로우 계속 진행
- **디렉토리 자동 생성**: `devflow-docs/solutions/{category}/` 미존재 시 Write 전에 생성
- **error_signature 폴백**: error_message가 너무 짧으면 root_cause 키워드로 error_signature 보완
- **TTL 참고**: `last_validated` 기준 60일 경과 시 stale 표시 예정 (BL-057에서 구현)
