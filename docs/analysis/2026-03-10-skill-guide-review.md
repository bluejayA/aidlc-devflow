# B안 Skill Guide 준수 리뷰

- **작성일**: 2026-03-10
- **기준**: `~/.claude/projects/-Users-jay-ahn-projects-ai/memory/skill-building-guide.md`
- **대상**: `phase3/b-plan` 브랜치 — 9개 skill (using-devflow, 7개 stage skill, 2개 _utils)

---

## 발견된 이슈 (12개)

### 🔴 Critical

#### 1. `devflow-state`, `devflow-audit` — YAML frontmatter 완전 누락
- **위치**: `skills/_utils/devflow-state/SKILL.md`, `skills/_utils/devflow-audit/SKILL.md`
- **문제**: `---` 구분자, `name`, `description` 필드 없음
- **영향**: skill 로드/트리거 불가

#### 2. stage skill 7개 — description이 내부 구현 메모
- **위치**: workspace-detection, requirements-analysis, workflow-planning, application-design, units-generation, code-generation, build-and-test
- **문제**: `description: B안 순수 실행자 — 오케스트레이터(using-devflow)의 호출로만 실행됨` — WHAT+WHEN 없음
- **영향**: 오케스트레이터 호출 시 Claude가 skill을 올바르게 식별하지 못할 수 있음

#### 3. 에러 핸들링 없음 — 모든 skill
- **위치**: 전체
- **문제**: devflow-docs/ 없음, 이전 산출물 없음, units.md 없는데 multi-unit 진입 등 에러 케이스 미처리
- **영향**: 런타임 실패 시 복구 불가

---

### 🟡 Important

#### 4. `application-design`, `units-generation` — 파일 경로 미명시
- "Read requirements and workspace analysis" — 어느 파일인지 불명확

#### 5. `code-generation` PART 2 — 호출 메커니즘 불명확
- "orchestrator signals with 'generate'" — 실제 Claude 실행 방식 미명시

#### 6. `build-and-test` Step 1 — 분석 대상 미명시
- "Review generated code" — 어디를 볼지 불명확

#### 7. `using-devflow` — devflow-docs/ 디렉토리 생성 보장 없음
- devflow-state 유틸 호출 전 디렉토리 존재를 확인하는 단계 없음

#### 8. 예시(Examples) 없음 — 모든 skill
- using-devflow(진입점), code-generation(2단계 프로세스)에 특히 필요

---

### 🔵 Minor

#### 9. `using-devflow` description — trigger phrase 부족
- "AI-DLC workflow"는 사용자가 쓰는 표현이 아님

#### 10. 선택 메타데이터 없음
- version, author 미기재

#### 11. `using-devflow` Troubleshooting 없음
- 세션 재개 실패, 산출물 없음 등 케이스 미기재

#### 12. `_utils` 폴더명 규칙 검토 필요
- `_utils`는 언더스코어로 시작 — kebab-case 예외 케이스, plugin.json에서는 정상 참조됨

---

## 수정 결과

모든 이슈 수정 완료 (2026-03-10).
