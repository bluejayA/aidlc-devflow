# Knowledge System Phase 2 — 관측 설계 + Consumer Baseline

> **목적**: Phase 1 구현이 plugin repo에 머지된 후, 실사용 데이터가 축적되는 **consumer repo**에서 Phase 2 트리거를 평가하기 위한 관측 설계.
>
> **참조**: `phase1-baseline.md` (plugin repo 기준 T0), `../../plans/2026-04-13-knowledge-system-phase1-plan.md` (Phase 2 Re-evaluation Criteria)

## 전략: Tier 1 단일 Consumer 관측 (OR 조건)

다중 consumer 집계 대신 **대표 repo 1개에서 독립 평가**. 트리거 임계(T1-T10)는 단일 프로젝트 기준으로 설계되었으므로 합산하면 의미가 변질된다. 한 repo라도 임계 초과 = 유효 신호로 간주한다.

| 구분 | Repo | 역할 |
|------|------|------|
| Tier 1 | `/Users/jay.ahn/projects/infra/nexttui` | 실사용 관측 — devflow 주사용 환경 |
| 예비 | (신규 프로젝트) | nexttui 데이터 부족 시 추가 고려. 현재는 불필요 |

신규 greenfield 프로젝트는 **억지로 돌리는 시뮬레이션이 될 위험**이 있어 채택하지 않음. nexttui는 이미 3주+ devflow 반복 사용 이력(archived state 12개)이 확인됨.

## nexttui T0 Snapshot (관측 시작점)

### 측정 시점

- **날짜**: 2026-04-14T04:32:12Z (UTC)
- **commit**: `7d13944` (branch `main`)
- **플러그인 상태**: PR #157 plugin repo 머지 완료 (2026-04-13T23:50:13Z), **단 nexttui에는 아직 새 hook 미반영**

### Baseline 값

| 측정 대상 | 값 | Phase 2 트리거 임계 |
|----------|-----|------|
| `devflow-docs/audit.md` 크기 | **17,326 bytes** (172 lines) | T1: > 100KB → audit-log/ rotation |
| `audit.md` file-edit prefix 건수 | **0** (v1.10.0 설치 완료. nexttui 세션에서 Edit 발생 후 누적 시작) | T10: file-edit > 80% → signal/noise 재검토 |
| `devflow-docs/solutions/` 파일 수 | **0** | T2 (Critical): 14일 후 0 = STORE trigger 실패 분석 |
| `devflow-state.md` | 존재 (3,028 bytes) | T9 (Critical): heading 누락/깨짐 → hook race bug |
| `.archive/` archive 수 (정확) | state **11** + summary **3** + inception **9** + construction **5** | 정상 archive (spec 준수) |
| `.archive/legacy/` 보존 수 | state 12 + summary 3 = **15** | Mar 24~27 구 명명규약 (`-archived-` suffix) 흔적. 측정에서 제외 |

### T0 해석 (중요)

- **`audit.md` 17KB는 Phase 1 hook 적용 전 수치**. plugin 업데이트가 nexttui에 반영되면 file-edit prefix가 누적되기 시작한다.
- **`solutions/` = 0은 이미 T2 Critical 트리거 후보 신호**. 3주 이상 devflow 사용 중인데 STORE 산출물이 한 번도 생성되지 않음. Phase 2 진입 시 최우선 분석 대상.
- **Archive 정합성 cleanup (2026-04-14)**: nexttui `devflow-docs/` 루트에 구 명명규약(`devflow-state-archived-*`, `session-summary-archived-*`) 15개가 spec 표준(`.archive/`)과 분리되어 있었음. `git mv`로 전부 `.archive/legacy/`에 이동. T9 트리거 평가 시 `.archive/` 직속(spec 준수분)만 기준으로 사용한다.

## 관측 프로토콜

### 전제: Plugin 업데이트 반영 확인 (2026-04-14 검증 완료)

Plugin v1.10.0이 `~/.claude/plugins/cache/devflow-marketplace/aidlc/1.10.0`에 **2026-04-14T01:02:12Z 설치 완료**. Hook을 수동 실행(stdin JSON payload)해 audit.md에 entry가 정상 추가되는 것 확인했다. 로직 레벨 검증 PASS.

nexttui에서 실제 Claude Code 세션이 Edit/Write를 수행하면 자동 기록된다:

```bash
cd /Users/jay.ahn/projects/infra/nexttui
grep -c 'file-edit' devflow-docs/audit.md  # > 0 이면 E2E 확인
```

**주의**: 다른 repo에서 열린 Claude Code 세션이 nexttui 파일을 Edit해도 hook은 "outside repo"로 판단해 기록하지 않는다 (설계상 의도). 반드시 nexttui를 cwd로 한 세션이어야 한다.

### 측정 시점

| 시점 | 날짜 | 액션 |
|------|------|------|
| T0 | 2026-04-14 | 본 문서 T0 snapshot (상단 표) |
| T0' | Hook 반영 직후 | file-edit prefix 1건 발견 시점 재측정 |
| T+3 | 2026-04-17 | Sprint 1 1차 체크 — audit 성장률, solutions 생성 유무 |
| T+14 | 2026-04-28 | Phase 2 plan 작성 시점 + 레드팀 3차 리뷰 호출 권장 |

(원 baseline의 T+3=2026-04-16, T+14=2026-04-27은 plugin repo 기준. nexttui는 T0가 하루 늦어 조정.)

### 재측정 명령

```bash
cd /Users/jay.ahn/projects/infra/nexttui
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit: $(git rev-parse --short HEAD)"
echo "audit.md size: $(wc -c < devflow-docs/audit.md) bytes"
echo "audit.md lines: $(wc -l < devflow-docs/audit.md) lines"
echo "file-edit count: $(grep -c 'file-edit' devflow-docs/audit.md 2>/dev/null || echo 0)"
echo "solutions/ count: $(find devflow-docs/solutions -type f 2>/dev/null | wc -l)"
echo "state.md present: $([ -f devflow-docs/devflow-state.md ] && echo yes || echo no)"
# .archive/ 직속만 카운트 (legacy/ 제외)
echo "archived states: $(find devflow-docs/.archive -maxdepth 1 -name 'devflow-state-*.md' 2>/dev/null | wc -l)"
echo "archived summaries: $(find devflow-docs/.archive -maxdepth 1 -name 'session-summary-*.md' 2>/dev/null | wc -l)"
echo "archived inception/: $(find devflow-docs/.archive -maxdepth 1 -name 'inception-*' -type d 2>/dev/null | wc -l)"
echo "archived construction/: $(find devflow-docs/.archive -maxdepth 1 -name 'construction-*' -type d 2>/dev/null | wc -l)"
```

## Phase 2 평가 시 사용 방법

1. 위 재측정 명령으로 **nexttui 새 값** 기록
2. `phase1-baseline.md` 재실행으로 **plugin repo 새 값** 기록 (대조군)
3. nexttui 값을 기준으로 T1-T10 트리거 테이블 적용 (OR 조건)
4. Critical 트리거(T2/T9) 발동 여부 먼저 확인
5. 새 plan 작성: `docs/plans/YYYY-MM-DD-knowledge-system-phase2-*.md`
6. 레드팀 3차 리뷰 호출 자료:
   - 본 관측 문서 + 재측정 결과
   - `phase1-baseline.md` (plugin repo 기준)
   - `handoff-context.md` (설계 의도)
   - 트리거 발동 현황 표

## 알려진 제약

- **단일 repo 관측의 한계**: nexttui에 특화된 신호가 plugin 일반 문제로 해석될 위험. 특이 패턴 발견 시 "nexttui 특성인지 plugin 일반인지" 구분 필요.
- **Hook 반영 지연**: 플러그인 marketplace 기반 업데이트 주기에 따라 T0'가 늦어질 수 있음. 이 기간의 데이터는 file-edit 기반 트리거에서 제외.
- **Brownfield 노이즈**: nexttui는 이미 상당량의 audit/state 이력 보유. 절대값 임계(T1: 100KB)는 신규 증가분 기준으로 재해석 권장.
