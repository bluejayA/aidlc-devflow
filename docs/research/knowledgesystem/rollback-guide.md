# Knowledge System Phase 1 — Rollback Guide

> **목적**: BL-085 (Phase 1) 운영 중 문제 발견 시 단계별 되돌림 절차. 긴급 상황에 재현 가능한 표준.
>
> **관련**: PR #157, 이슈 #154, `phase1-baseline.md`

---

## 설계적 rollback 친화성

본 Phase 1은 의도적으로 롤백 친화적으로 설계됨:

1. **Metadata는 passive**: `skill_nature`, `applies_to`, pattern frontmatter는 **코드가 읽지 않음** (handoff §2.5 "classification, not enforcement"). 남겨둬도 동작 영향 0.
2. **Hook은 단일 knob**: `hooks/hooks.json` PostToolUse 블록 제거만으로 즉시 비활성.
3. **STORE ownership 변경은 2 파일 localized**: systematic-debugging + construction-orchestrator.

따라서 **부분 롤백** 가능. 전체 되돌림 강요 안 됨.

---

## Level 1: Hook만 비활성 (가장 빠름, 1분)

### 언제
- audit.md 급성장 (100KB 초과 후 수시 경고)
- state.md `## Last Updated` 외 구조 섹션 파손 (T9 Critical)
- hook 실행 지연 (T8 > 500ms 평균)
- 단일 세션에서 audit 오염 관측

### 절차

**A. hooks.json에서 PostToolUse 제거** (repo에서 직접 수정):

```json
{
  "hooks": {
    "SessionStart": [...],
    "PostToolUse": [...]  ← 이 블록 통째로 삭제
  }
}
```

commit:
```bash
git commit -m "revert: disable post-tool-file-edit hook (Level 1 rollback)"
```

**B. 또는 plugin 재설치로 이전 버전 사용**:
```bash
# Claude Code에서:
/plugin install aidlc@1.9.0
```

### 영향
- file-edit 자동 audit 중단
- taxonomy / skill 태깅 / STORE 변경은 그대로 유지
- 데이터 손실: 없음 (기존 audit.md 보존)

### 복구 가능성
- 재활성화 쉬움 (PostToolUse 블록 복원)
- audit.md 데이터는 누적 중단되지만 삭제 안 됨

---

## Level 2: STORE ownership 변경 revert (10-15분)

### 언제
- Solution layer 생성 오류 (SAVE/DUPLICATE/REJECT verdict 처리 버그)
- construction-orchestrator verdict 소비 중 실패
- systematic-debugging 경로에서 STORE 호출이 잘못된 데이터 저장

### 절차

```bash
# Task 2+3 commit revert
git log --oneline --grep "STORE ownership"
# → 697fae3 찾음

git revert 697fae3
# conflict 발생 시 수동 해결 (skills/aidlc-construction-orchestrator/SKILL.md)
```

**test_construction_k_gate.py 재작업 필요**: 현 테스트는 verdict 소비 방식 검증. revert 후 구 K-gate UX 검증으로 복원 필요.

- 원본 test 버전은 `git show 0cdffc2^:tests/test_construction_k_gate.py` 또는 Task 2+3 commit 이전 버전으로 복원

### 영향
- K-gate UX 복원 (사용자 `K)` 선택 선택지 부활)
- Solution 생성은 사용자 opt-in으로 돌아감
- **기존 생성된 Solution 파일은 남음** (경로 유지, 새 schema 아님)

---

## Level 3: 전체 PR revert (30분-1시간)

### 언제
- 근본 설계 실패 (T2 Critical + T9 Critical 동시 발동)
- Multi-system 이상 (hook + STORE + metadata 모두 문제)
- 레드팀 3차 리뷰 결과 "폐기 권고"

### 절차

**단계 1: PR 머지 commit 찾기**
```bash
git log --merges --grep "BL-085" --oneline
# 또는
git log --merges --oneline | head
```

**단계 2: revert merge commit**
```bash
git revert -m 1 <merge-commit-sha>

# merge commit revert는 이후 feature branch 재머지를 막으므로,
# Phase 2에서 재도전 시 다른 접근으로 설계할 것 (같은 commit 재적용 X).
```

**단계 3: plugin 버전 rollback**
```bash
# plugin.json 버전을 1.10.0 → 1.9.0 (또는 1.10.1 = 1.9.0 + revert)
git tag v1.10.1  # revert 포함
git push --tags

# marketplace 업데이트:
# - bluejayA/devflow-marketplace repo에서 aidlc/version 엔트리 수정
# - 사용자: /plugin update aidlc
```

**단계 4: 관련 이슈 처리**
```bash
gh issue reopen 154  # BL-085
gh issue comment 154 --body "설계 문제 발견으로 Level 3 revert 실행. 
revert commit: <hash>
근거: [트리거 T2/T9 데이터]
Phase 2 재설계 필요."
```

### 영향
- Phase 1 전체 되돌림
- 남는 자산:
  - `docs/research/knowledgesystem/` 설계 문서 (보존 권장)
  - `phase1-baseline.md` + 후속 measurements (post-mortem 근거)
  - 생성된 Solution 파일 (사용자 판단에 따라 archive 또는 삭제)

---

## 완전 Abandon 경로

최악의 경우: Phase 1 설계 자체가 틀렸다고 판단.

### 절차

1. **Level 3 revert 실행** (위)
2. **설계 문서는 보존**:
   - `docs/research/knowledgesystem/` 전체 유지
   - 이유: 설계 의도 + debate 영속화. 미래 재시도 시 같은 실수 방지
3. **메모리 업데이트**:
   - `~/.claude/projects/-.../memory/project_knowledge_system_phase1.md` → "abandoned, lessons learned"로 재작성
   - 추가 memory: feedback type으로 "knowledge system abandon 이유 + 재시도 조건"
4. **이슈 처리**:
   - BL-085 #154 재오픈 후 "설계 abandoned" 코멘트
   - 교훈을 새 이슈(BL-089 candidate)로 분리: "Phase 1 실패 경험 — 재설계 제약"
5. **Post-mortem 작성**:
   - 경로: `docs/research/knowledgesystem/phase1-postmortem.md`
   - 내용: 관측 데이터 (baseline + measurements), 트리거 발동 이력, 설계 결함 원인, 향후 재시도 시 제약

### 보존 vs 삭제 판단

| 자산 | 권고 |
|------|------|
| `docs/research/knowledgesystem/` 설계 문서 | **보존** (재시도 제약 근거) |
| `phase1-baseline.md` + measurements | **보존** (post-mortem 근거) |
| `devflow-docs/solutions/` 생성 데이터 | **사용자 판단** (재사용 가능하면 유지, 오염이면 archive/삭제) |
| `skills/_shared/` frontmatter | **유지** (passive, 영향 없음. 추후 다른 목적 재활용 가능) |
| `skill_nature` metadata on SKILL.md | **유지** (동일 이유) |

---

## Rollback 실행 전 체크리스트

긴급 상황이라도 다음 확인 필수:

- [ ] **실제 트리거 데이터 확인**: audit.md, state.md, solutions/ 실측 값 vs `phase1-baseline.md` T0
- [ ] **문제 원인 파악**: Level 선택 근거 — 어느 component가 실패했나?
- [ ] **필요 Level 결정**: Level 1 → 2 → 3 순. 과잉 롤백 금지
- [ ] **백업**: revert 전 `git branch backup/pre-rollback-YYYY-MM-DD` 브랜치 생성
- [ ] **이해관계자 통지**: 사용자 / 다른 플러그인 사용자에게 rollback 계획 알림
- [ ] **레드팀 상담**: Level 3 이상 결정 시 레드팀 3차 리뷰 호출 권장

---

## Post-Rollback 조치

### Level 1 후
- hook 비활성 원인 분석 → BL-087 / BL-088 / 신규 이슈로 분리
- 2주 후 재활성화 여부 재평가

### Level 2 후
- STORE ownership 설계 재검토
- K-gate vs verdict 소비 방식 tradeoff 재측정
- 대안 옵션 β (context 분기) / γ (dedup) 재검토 (plan §2.2 참조)

### Level 3 후
- Post-mortem 작성 (위 참조)
- Phase 2 plan을 "재설계" 방향으로 작성
- 레드팀 3차 리뷰 호출

---

## 절대 하지 말 것

- ❌ **`git reset --hard origin/main` on rollback** — 데이터 손실. revert 사용
- ❌ **tag 삭제**: v1.9.0, v1.10.0 등 기존 tag 삭제 금지 (marketplace 과거 버전 참조 보호)
- ❌ **`devflow-docs/` 전체 삭제**: 운영 데이터 + archive 손실
- ❌ **revert 없이 metadata 수동 제거**: passive라 불필요. 오히려 다른 skill 파손 위험
- ❌ **PR 머지 후 feature branch 즉시 삭제**: 최소 4주 보존 권장 (rollback 참조용)

---

## 관련 자료

- `docs/plans/2026-04-13-knowledge-system-phase1-plan.md` §Phase 2 Re-evaluation Criteria
- `docs/research/knowledgesystem/handoff-context.md` — 설계 의도 + debate
- `docs/research/knowledgesystem/phase1-baseline.md` — T0 baseline
- PR #157, 이슈 #154

**연락 / 상담**:
- 레드팀 3차 리뷰: Critical 트리거 발동 시 자동 호출 기준
- Codex: `/codex:rescue` 사용 가능
