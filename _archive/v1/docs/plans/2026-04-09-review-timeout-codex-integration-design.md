# 리뷰 타임아웃 방어 + Codex 통합 설계

**Complexity:** Standard
**Date:** 2026-04-09
**Related:** BL-082 (#147) 일부 연관

---

## 1. 문제

agent-council 기반 코드 리뷰(R1/R2/R3)에서 타임아웃이 빈번하게 발생한다.

- **증상 B**: Claude Code "tool call timed out" 에러
- **증상 C**: 리뷰 결과가 불완전하게 반환 (중간 끊김)

### 원인 분석

| 원인 | 모드 | 설명 |
|------|------|------|
| 서브에이전트 장시간 실행 | R1/R2/R3 | 리뷰어가 대용량 diff를 분석할 때 Agent tool call 자체가 타임아웃 |
| 순차 누적 | R1 | Stage 1→2→3→4 순차 실행, 각 stage의 리뷰+재시도가 누적 |
| 팀 동기화 대기 | R3 | 가장 느린 에이전트가 전체를 블로킹 |

---

## 2. 설계: 타임아웃 방어

### 2.1 개별 에이전트 타임아웃

| 설정 | 기본값 | 사용자 오버라이드 |
|------|--------|------------------|
| 개별 리뷰어 타임아웃 | 300초 | 자유 발화로 세션별 조정 |
| R3 팀 전체 타임아웃 | 600초 | 자유 발화로 세션별 조정 |

- 설정 위치: `devflow-conventions.md` 리뷰 규약
- 오버라이드 방법: 리뷰 시작 시 "타임아웃 600초로" → 해당 세션에 적용

### 2.2 타임아웃 발생 시 동작

| 상황 | 동작 |
|------|------|
| 개별 리뷰어 타임아웃 (300초) | 해당 stage "⏭ 타임아웃" 표시, 나머지 stage 결과로 Verdict 종합 |
| Codex 타임아웃 | "Codex 세컨드 오피니언: ⏭ 타임아웃" 표시, Claude 결과만으로 진행 |
| R3 팀 전체 타임아웃 (600초) | 완료된 에이전트 결과만 종합, 미완료 에이전트는 "⏭ 타임아웃" |
| 모든 리뷰어 타임아웃 | 사용자에게 escalate — "리뷰 실행 불가. A) 재시도 / B) 리뷰 스킵" |

> **R2 (Council) 범위**: R2는 기존 `council-review-protocol.md`의 타임아웃 정책을 유지한다. 이 설계는 R1/R3 + Codex 통합에 집중하며, R2는 별도로 다루지 않는다.

### 2.3 R1 병렬화 확대

현재 Comprehensive에서만 Stage 3+4 병렬. Standard에서도 Stage 2+3을 병렬 dispatch한다 (Quality와 Security는 독립적 관점).

```
[Before] 순차
Stage 1 (Spec) → Stage 2 (Quality) → Stage 3 (Security)
총 시간: T1 + T2 + T3

[After] 병렬
Stage 1 (Spec)
    ↓
Stage 2 (Quality, background) ─┐
Stage 3 (Security, background) ─┤ 병렬
    ↓
결과 종합
총 시간: T1 + max(T2, T3)
```

**Stage FAIL 시 병렬 결과 처리**: Stage 2 또는 Stage 3이 FAIL을 반환하면, 다른 stage의 결과는 **유지**한다. FAIL stage만 수정 루프에 진입하고, 이미 PASS한 stage는 재실행하지 않는다.

### 2.4 R3 부분 완료 허용

느린 에이전트 1개를 기다리지 않고, 타임아웃된 에이전트는 "⏭ 타임아웃" 표시 후 나머지 결과로 종합.

---

## 3. 설계: Codex 리뷰 통합

### 3.1 Phase별 Codex 도구 매핑

| Phase | 리뷰 대상 | Claude 리뷰어 | Codex 도구 | 실행 방식 |
|-------|----------|--------------|-----------|----------|
| CONSTRUCTION | Stage 2 (Quality) | code-quality-reviewer | `/codex:review` | 수동 — 실행 가이드 표시 |
| INCEPTION | brainstorming Spec | spec-document-reviewer | `/codex:adversarial-review` | 수동 — 사용자 판단 |
| INCEPTION | writing-plans Plan | plan-document-reviewer | `/codex:adversarial-review` | 수동 — 사용자 판단 |

### 3.2 실행 방식

**모든 Phase에서 수동 실행**: `/codex:review`와 `/codex:adversarial-review`는 `disable-model-invocation` 제약으로 Claude가 자동 호출할 수 없다. Claude 리뷰 결과와 함께 Codex 실행 가이드를 표시하고, 사용자가 필요 시 직접 실행한다.

**CONSTRUCTION — requesting-code-review가 실행 가이드 생성:**

```
Claude 리뷰 완료
    ↓
결과 표시 + Codex 실행 가이드:
  → /codex:review --scope branch
    브랜치: [branch명], 워크트리: [path]
    참고: [CONDITIONAL/FAIL stage 관점 힌트]
    ↓ 사용자 판단
  실행 또는 스킵
```

**INCEPTION — 사용자 자율 실행:**

```
brainstorming/writing-plans 완료 → 산출물 저장
    ↓ 사용자 판단
/codex:adversarial-review (필요 시 직접 실행)
```

### 3.3 Codex 실행 가이드 컨텍스트

requesting-code-review는 다음 정보를 기반으로 실행 가이드를 생성한다:

| 항목 | 소스 |
|------|------|
| 워크트리 경로 | `devflow-state.md`의 `## Worktree` → `path` |
| 브랜치명 | `devflow-state.md`의 `## Worktree` → `branch` |
| 리뷰 범위 | 워크트리 있음 → `--scope branch`, 없음+staged → `--uncommitted`, 없음+커밋 완료 → `--base main` |
| 관점 힌트 | CONDITIONAL/FAIL stage의 이슈 요약 |

### 3.4 Codex 미설치 fallback

Codex CLI 미감지(`command -v codex` 실패) 시 실행 가이드를 생략한다. 세션당 1회 감지, 결과 캐싱.

---

## 4. 변경 대상 파일

| 파일 | 변경 내용 |
|------|----------|
| `_shared/devflow-conventions.md` | 타임아웃 기본값 추가, 병렬화 정책 |
| `aidlc-requesting-code-review/SKILL.md` | 타임아웃 적용, Stage 2+3 병렬화, Codex 통합 (CONSTRUCTION) |
| `aidlc-brainstorming/SKILL.md` | Codex 수동 실행 안내 추가 |
| `aidlc-writing-plans/SKILL.md` | Codex 수동 실행 안내 추가 |

---

## Assumptions

- Codex CLI가 설치된 환경에서는 `command -v codex`로 감지 가능 (기존 `council-cli-detection.md` 패턴 재사용 검토)
- 서브에이전트 background dispatch 시 메인 컨텍스트에서 Codex 실행이 블로킹되지 않음. 블로킹될 경우 fallback: 순차 실행 (Claude 완료 후 Codex)
- Codex `/codex:review`와 `/codex:adversarial-review`의 출력 포맷이 사람이 읽을 수 있는 마크다운
- 타임아웃 기본값(300초/600초)은 현재 관측된 리뷰 소요 시간(~120초 기본 + 대용량 diff 시 초과)에 기반한 경험적 추정치
