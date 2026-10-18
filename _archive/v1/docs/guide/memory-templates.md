# DevFlow Memory Templates

DevFlow 운영 시 채택할 수 있는 auto-memory 템플릿 모음. **본 plugin이 강제하지 않으며**, 각 프로젝트 환경에 맞게 복사해서 사용한다.

> **모델**: aidlc-devflow plugin은 building block(skill / hook / utility / pattern docs / conventions)만 제공하고, 운영 정책은 프로젝트별 auto-memory에 위임한다. 본 파일은 그 위임 모델의 reference 역할. 자세한 아키텍처는 `reference_plugin_building_block_model.md` 메모리 참조.

---

## 채택 방법

1. 원하는 패턴 섹션의 **frontmatter + 본문** 영역을 복사
2. 본인 프로젝트 auto-memory(`~/.claude/projects/<encoded-cwd>/memory/`)에 새 파일 생성
3. 본문 그대로 또는 본인 환경에 맞게 수정
4. `MEMORY.md` index에 한 줄 추가

> `<encoded-cwd>` 인코딩 규칙: 작업 디렉토리 절대 경로의 슬래시 → 하이픈 (예: `/Users/jay/repo` → `-Users-jay-repo`).

### 자연 발화 자동화

복사 작업도 LLM에 자연 발화로 요청 가능:

> *"memory-templates.md에서 [패턴명]을 내 프로젝트 메모리에 복사해줘"*

LLM이 본 파일을 읽고 → 해당 섹션 추출 → auto-memory 파일 생성 → MEMORY.md index 갱신.

---

## Pattern Catalog

### Pattern 1 — Mid-cycle Stop 정리 출력 (plugin 2단계 + 세션 요약)

**언제 사용**: mid-cycle pause 시 plugin 기본 2단계 자동화(auto-memory 갱신 + audit append/commit)에 더해, 사용자에게 **진행 요약 / 다음 세션 재개 명령 / 다음 작업**을 일관 형식으로 표시하길 원할 때. 다음 세션이 컨텍스트를 빠르게 복원하는 데 유용.

**vs plugin 기본**:
- Plugin 기본 (`operator-guide.md` §7): 2단계 자동 수행 + 사용자 승인. 출력 형식 미정.
- 본 패턴: plugin 2단계 그대로 준수 + **추가로** 3블록 출력 형식 표시.

**출처**: nexttui 프로젝트 — long-running multi-phase 개발 환경에서 자연 형성.

#### 출력 예시

```
진행 요약 (이번 세션)
- ✅ 1회 Resume + cross-check (이전 stale 발견)
- ✅ Phase 6 Step 8 (73b347d) — ScopeProvider trait
- ✅ Phase 6 Step 9+10 (1f80968) — ActionSender 스탬핑

진행 상황: BL-P2-085 plan 18 Steps 중 10 완료 (~56%)

다음 세션 재개 (자동 검증 가능)

cd /Users/jay.ahn/projects/infra/<project>/.worktrees/<branch>
git branch --show-current        # → feature/<branch>
git log -1 --oneline             # → <expected-hash>
cargo test --lib                 # → <expected> pass
# memory 자동 로드 (project_<name>.md)

다음 작업 — Phase 7 Step 11 (3-cycle 분할 권장):
- 11a: <작업 1>
- 11b: <작업 2>
- 11c: <작업 3>

수고하셨습니다. 정상 종료.
```

#### 복사 대상

```markdown
---
name: feedback_session_end_format
description: mid-cycle pause 시 plugin 2단계 자동화 준수 + 진행 요약/재개 명령/다음 작업 3블록 출력 형식. 다음 세션 컨텍스트 복원 시간 단축. plugin 기본(operator-guide.md §7)을 대체하지 않고 보강.
type: feedback
---
mid-cycle pause 신호(*"잠시 중단"*, *"오늘은 여기까지"*, *"내일 이어서"*, *"수고했어"*, *"정상 종료"* 등) 수신 시 다음 두 부분을 함께 수행한다.

## 1. Plugin 기본 2단계 자동화 (먼저 수행)

`docs/guide/operator-guide.md` §7 그대로:

**① auto-memory 갱신** (+ MEMORY.md index 동시)
- `~/.claude/projects/<encoded-cwd>/memory/`의 관련 메모리에 commit hash / test 결과 / resume point / 의사결정 갱신
- 경계 주의: exact match 디렉토리만 (다중 후보/부재 시 skip + audit 사유 기록)

**② audit append + commit**
- `[<ISO ts>] session-paused | branch=<n> | head=<short> | resume=<phase>` append
- `chore(devflow): mid-cycle pause checkpoint` commit
- 사용자 승인 후 진행. unrelated staged 변경 있으면 안 함.

> state.md는 자동 갱신 안 함 (advisory cache). 사용자 자연 발화 시에만 갱신.

## 2. 3블록 출력 형식 (1단계 후 사용자에게 표시)

### 블록 ①: 진행 요약 (이번 세션)
- 제목: `진행 요약 (이번 세션)`
- ✅로 시작하는 항목 4-8개 (각 1줄 — commit hash + 한 줄 설명 권장)
- 마지막 한 줄: `진행 상황: <plan 이름> <N/M Steps> 완료 (~<%>%)`

### 블록 ②: 다음 세션 재개 (자동 검증 가능)
- 제목: `다음 세션 재개 (자동 검증 가능)`
- bash 명령 블록 — `cd`, `git branch --show-current`, `git log -1 --oneline`, 테스트 명령
- 각 명령 옆 주석 `# → <expected output>` (다음 세션이 자동 검증 가능)
- 마지막 한 줄: `# memory 자동 로드 (<관련 메모리>)`

### 블록 ③: 다음 작업
- 제목: `다음 작업 — <Phase/Step 이름>`
- 분할 권장 시: `(N-cycle 분할 권장)` 같은 힌트
- 하위 항목 (a, b, c 등) — 각 1줄

## 3. 종료 인사
`수고하셨습니다. 정상 종료.` 또는 동급 1줄.

## 적용 범위
- mid-cycle pause: 본 패턴 = plugin 2단계 + 3블록 출력
- finishing 시 (PR 마무리): 본 패턴 + finishing-a-development-branch skill의 PR/머지 절차 (skill이 우선)

## 관련
- plugin 기본 mid-cycle 2단계: `docs/guide/operator-guide.md` §7
- session-summary 파일 형식: `_shared/patterns/session-continuity.md` (별개 — 본 패턴은 LLM 응답 텍스트, 그쪽은 .md 산출물)
- plugin 위임 모델: `reference_plugin_building_block_model.md`
```

---

## 새 패턴 추가 가이드

본 파일은 **자연 발생 패턴 우선** 원칙을 따른다. 즉:

1. 어떤 프로젝트에서 자연스럽게 형성된 운영 패턴이 있고
2. 그 패턴이 다른 프로젝트에도 가치 있을 가능성이 보이면
3. 본 파일에 frontmatter + 본문 형식으로 추가

추측 기반 일반화는 거부 (`feedback_systemization_limit.md` 원칙). 단일 프로젝트 사례라도 출처를 명시하고 *"본인 환경 판단 후 채택"* 안내가 필수.

### 패턴 항목 형식

```markdown
### Pattern N — <짧은 이름>

**언제 사용**: <한 줄 trigger 조건>
**vs plugin 기본**: <plugin 기본과의 차이>
**출처**: <어느 프로젝트/사례>

#### 복사 대상

\`\`\`markdown
---
name: <memory_name>
description: <한 줄 description>
type: feedback (or reference, project)
---
<본문>
\`\`\`
```

### 검토된 후 거절된 패턴 (참고)

- **Mid-cycle Stop 5단계 strict (3-way sync)** — nexttui `feedback_stop_checklist.md` 사례. plugin 기본(advisory cache 2단계) 대신 strict 정책. 본 plugin level에서는 *plugin 2단계가 충분*하다는 결정으로 채택 보류 (본 plugin은 drift 허용 모델). 본인 프로젝트에서 strict 정책이 필요하면 직접 메모리 작성 가능.

---

## References

- 위임 모델 아키텍처: `~/.claude/projects/<encoded-cwd>/memory/reference_plugin_building_block_model.md` (본인 메모리)
- Plugin 기본 운영 가이드: `docs/guide/operator-guide.md`
- 정합성 체크리스트: `docs/guide/consistency-checklist.md`
- Plugin 컨벤션: `skills/_shared/devflow-conventions.md`
