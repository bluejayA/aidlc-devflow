# 컨텍스트 격리 + Instruction Priority 설계

**이슈**: #9 + #14
**날짜**: 2026-03-17
**상태**: 설계 승인됨

## 범위

conventions.md에 2개 섹션 추가 + 관련 스킬 2개 정합성 수정.

## Task 1: conventions에 Instruction Priority 추가

아키텍처 개요 다음, YAML 메타데이터 규약 전에 배치:
```
1. 사용자 지시 (CLAUDE.md, 프로젝트 설정, 직접 요청) — 최우선
2. 스킬 규칙 (SKILL.md, _shared/ 규약) — 기본 동작 오버라이드
3. 기본 동작 (시스템 프롬프트) — 최하위
```

## Task 2: conventions에 서브에이전트 컨텍스트 격리 추가

기존 "Subagent Dispatch Rules" 바로 아래에 배치.
- 원칙: 세션 히스토리 금지, 최소 컨텍스트만
- 필수 포함: 태스크 명세, 파일 경로, 기술 제약, 산출물 형식
- 금지: 이전 대화, 다른 태스크 결과, 사용자 피드백 원문

## Task 3: conventions 정합성 보완 (M2, M5)

- M2: return_behavior 정의 명확화 — "stop-no-gate는 오케스트레이터 게이트 금지. 스킬 내 단계별 사용자 확인은 허용"
- M5: depth fallback 우선순위 — 호출 텍스트 → workflow-plan Stage Depths → devflow-state Complexity

## Task 4: 스킬 정합성 (H1, H2)

- dispatching-parallel-agents: return_behavior 추가, description CSO 수정, 컨텍스트 격리 참조
- executing-plans: return_behavior 추가, description CSO 수정
