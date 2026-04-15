# graphify 참조 차용 아이디어

> **소스**: [safishamsi/graphify](https://github.com/safishamsi/graphify) — AI coding assistant skill that turns any folder into a queryable knowledge graph
> **작성일**: 2026-04-15
> **목적**: Phase 2 plan 작성 시 차용 여부를 판단하기 위한 후보 아이디어 정리 (참조용, 미확정)

---

## 1. 프로젝트 요약

graphify는 `/graphify .` 한 줄로 **코드/문서/PDF/이미지/비디오를 지식 그래프로 변환**하는 Claude Code skill. 3-pass 추출(AST → Whisper → LLM subagent), Leiden community detection, EXTRACTED/INFERRED/AMBIGUOUS 태그 체계. 26k+ stars, Python 기반, 플랫폼 중립(Claude Code/Codex/Cursor/Gemini 등).

핵심 출력:
- `GRAPH_REPORT.md` — god nodes + communities + surprising connections + suggested questions
- `graph.json` — 쿼리 가능한 persistent graph
- `graph.html` — 인터랙티브 시각화
- `cache/` — SHA256 기반 증분 업데이트

---

## 2. 차용 가치 높은 아이디어 (Phase 2 고려)

### 2.1 Evidence tagging (EXTRACTED / INFERRED / AMBIGUOUS) ★★★★★

**graphify 원형**: 모든 그래프 관계에 3개 태그 부여.
- `EXTRACTED`: 소스에서 직접 발견
- `INFERRED`: 추론 + confidence score
- `AMBIGUOUS`: 사람 검토 필요

**우리 현 상태**: Pattern frontmatter에 `source: manual | promoted_from_solution` 존재. 방향은 같으나 세밀도 부족.

**차용 방안**: taxonomy의 `related` 필드에 아래 frontmatter 추가:
```yaml
related:
  - path: "skills/aidlc-systematic-debugging/SKILL.md"
    tag: EXTRACTED
    confidence: 1.0
  - path: "docs/research/2026-04-06-skill-lifecycle-strategy.md"
    tag: INFERRED
    confidence: 0.7
    reason: "동일 BL-081 주제"
```

**ROI**: Phase 1 자산 33개 Pattern + 31개 Skill에 재라벨링 ≈ 1-2시간. 향후 graph 자동 생성 시 신뢰도 자동 반영.

### 2.2 GRAPH_REPORT.md (always-on 요약 페이지) ★★★★

**graphify 원형**: 한 페이지에 **god nodes**(가장 많이 참조되는 노드), **surprising connections**(예상 못한 연결), **suggested questions**를 자동 생성. Pre-read hook으로 매 세션 주입.

**우리 현 상태**: 없음. 사용자가 질문해야 문서 관계 파악 가능.

**차용 방안**:
- 단기(수동): `docs/research/knowledgesystem/reading-map.md` 손으로 작성 (본 작업에서 동시 생성)
- 중기(반자동): frontmatter `related` 필드 파싱 → Mermaid graph 자동 생성 스크립트
- 장기(자동): Phase 2/3에서 NetworkX + 링크 파서로 GRAPH_REPORT.md 생성

**ROI**: 단기는 즉시 가능. 자동화는 Phase 2 관측성 작업과 번들.

### 2.3 Always-on pre-read hook ★★★★

**graphify 원형**: PreToolUse hook으로 Glob/Grep 전에 `GRAPH_REPORT.md` 주입. *"grep하지 말고 graph로 navigate하라"*.

**우리 현 상태**: `hooks/session-start`는 SessionStart에만 작동. Grep/Glob 전 주입 없음.

**차용 방안**: 기존 `session-start` hook이 `devflow-state.md` + `reading-map.md` summary 함께 주입. 또는 PreToolUse hook 추가.

**ROI**: 기존 hook 확장이라 비용 낮음. Phase 2 관측 후 유효성 데이터 확보한 뒤 결정.

### 2.4 `.devflowignore` (gitignore syntax 필터) ★★★

**graphify 원형**: `.graphifyignore`로 그래프 포함·제외 경로 사용자 커스터마이징.

**우리 현 상태**: `hooks/post-tool-file-edit`의 whitelist/exclusion이 **hardcoded**.
```bash
# whitelist: devflow-docs/*|docs/*|skills/*|CLAUDE.md|README.md
# exclusion: tests/*|hooks/*|.claude-plugin/*|.git/*|.worktrees/*|devflow-docs/.archive/*|...
```

**차용 방안**: `.devflowignore` 파일로 빼내면 프로젝트별 커스터마이징 가능. nexttui 같은 consumer repo가 자체 규약 추가 가능.

**ROI**: 사용자 커스터마이징 요구가 쌓일 때 도입. 현재는 YAGNI.

---

## 3. 차용 가치 낮은 아이디어 (overkill / 범위 밖)

| 아이디어 | 이유 |
|---------|------|
| Leiden community detection | Phase 3 shared-tier 승격 판정에 쓰일 수 있으나, 현재 자산 규모(~60개)에서는 단순 `applies_to` 그룹핑으로 충분 |
| Whisper 멀티모달 (video/audio) | aidlc 맥락과 무관 |
| SHA256 cache 증분 업데이트 | 우리는 hook이 실시간 집계 → SHA256 캐시 불필요 |
| MCP 서버 exposure | Phase 3+ 고려 |
| 플랫폼 중립 (Cursor / Gemini / Codex) | aidlc는 Claude Code 전용 설계. 장기 확장 여지 |
| 3-pass extraction pipeline | 우리 자산은 Markdown + frontmatter 중심이라 AST/Whisper 불필요 |

---

## 4. 공통 철학 포인트 (간접 검증)

graphify와 우리 knowledge system은 설계 철학이 놀라울 만큼 수렴:

| 철학 | graphify | aidlc-devflow |
|------|----------|---------------|
| **Embeddings 없이 충분** | Leiden community (graph topology) | Frontmatter overlay (manual classification) |
| **결정적 parser 먼저, LLM 나중** | AST pass → Whisper → Claude subagent | Frontmatter 분류 → 필요 시 수동 review |
| **정직성 태그** | EXTRACTED / INFERRED / AMBIGUOUS | (지금은 `source`만, 확장 후보) |
| **증분 처리** | SHA256 cache | post-tool-file-edit hook의 append-only audit |
| **한 페이지 요약 + deep query** | GRAPH_REPORT.md + `query`/`path`/`explain` | (지금 없음, 차용 후보) |

**해석**: graphify가 5개월 앞서 26k stars를 받은 방향과 우리가 독립적으로 도달한 방향이 일치 → *"우리가 가는 길이 맞다"* 는 간접 검증이자, **아직 구현 안 된 차용 후보들이 우리 로드맵의 빈 칸을 정확히 채움**.

---

## 5. Phase 2 진입 시 의사결정 체크리스트

Phase 2 plan 작성 시 아래 항목 검토:

- [ ] **§2.1 Evidence tagging 확장**: 기존 `source` 필드 → `related` 필드 확장으로 트리거 가능? 비용 vs 효용 측정.
- [ ] **§2.2 GRAPH_REPORT 자동 생성**: 수동 reading-map 운영 경험 기반으로 자동화 여부 판단.
- [ ] **§2.3 Pre-read hook 확장**: baseline 관측에서 "문서 간 이동 비용" 신호가 잡히는지 먼저 확인.
- [ ] **§2.4 .devflowignore**: 사용자(nexttui 등 consumer) 요청 누적 기준 트리거.

---

## 6. 참고

- **graphify repo**: https://github.com/safishamsi/graphify
- **언급된 원문**: `aidlc-devflow-context-v2.1.md` §8 "참고 자료" — 초기부터 참조 프로젝트 중 하나로 식별됨
- **관련 내부 문서**:
  - [`knowledge-taxonomy.md`](knowledge-taxonomy.md) — 현재 `source` 필드 정의 위치
  - [`phase1-overview.md`](phase1-overview.md) — Phase 1 구현 완료 상태
  - [`phase2-observation-plan.md`](phase2-observation-plan.md) — 관측 설계
  - [`reading-map.md`](reading-map.md) — 본 제안 §2.2의 수동 첫걸음
