---
type: pattern
applies_to: [aidlc-inception-orchestrator, aidlc-requesting-code-review]
status: active
source: manual
last_validated: 2026-04-13
---

# Council CLI Detection

리뷰 시작 시 외부 AI CLI 설치 여부를 감지하고, 사용자에게 참여 AI를 확인받는다.

## CLI 감지 절차

```bash
command -v codex 2>/dev/null && echo "codex: $(which codex)" || echo "codex: 미설치"
command -v gemini 2>/dev/null && echo "gemini: $(which gemini)" || echo "gemini: 미설치"
```

## 가용 AI 표시 + 사용자 확인

CLI 감지 후, 가용한 AI 목록을 표시하고 사용자에게 참여 범위를 확인받는다.

### 2개 이상 가용 시

```
## 리뷰 환경 확인

가용한 외부 AI:
✅ codex: [경로]
✅ gemini: [경로]

A) 전부 사용 (council-full: Codex + Gemini + Claude 의장)
B) 일부만 선택 → 어떤 AI를 사용할지 알려주세요
C) 외부 AI 없이 진행 (Claude 단일 리뷰)
```

A 선택 → council-full 모드 확정
B 선택 → 사용자가 지정한 AI만으로 council-lite 모드 확정
C 선택 → single 모드 확정

### 1개만 가용 시

```
## 리뷰 환경 확인

가용한 외부 AI:
✅ [설치된 CLI]: [경로]
⚠️ [미설치 CLI]: 미설치

A) [설치된 CLI명] 사용 (council-lite: [CLI명] + Claude 의장)
B) 외부 AI 없이 진행 (Claude 단일 리뷰)
```

A 선택 → council-lite 모드 확정
B 선택 → single 모드 확정

### 0개 가용 시 (자동 진행)

```
## 리뷰 환경 확인

⚠️ codex: 미설치
⚠️ gemini: 미설치

→ Claude 단일 리뷰로 진행합니다.
```

single 모드 자동 확정 — 사용자 확인 불필요

## 모드 정의

| 모드 | 참여 에이전트 | 설명 |
|------|------------|------|
| **single** | Claude 서브에이전트 | 기존 단일 리뷰 (artifact-reviewer 또는 code-quality-reviewer) |
| **council-lite** | Claude 의장 + 외부 AI 1개 | 외부 AI가 두 관점(Codex+Gemini)을 병합 수행 |
| **council-full** | Claude 의장 + Codex + Gemini | 각 에이전트가 전담 관점 수행 |

## 리뷰 모드 선택 (모드 확정 후)

사용자가 참여 AI를 확정한 후, 리뷰 실행 방식을 선택한다:

```
리뷰 모드:
R1) 단일 리뷰 (Claude만) — council 선택과 무관하게 항상 가용
R2) Council 리뷰 ([확정된 모드])
Ra) 자동 선택 (risk score 기반) ← 기본
```

R1은 사용자가 참여 AI를 확정했더라도 단일 리뷰로 전환 가능 (마음 변경 허용).

## agent-council 플러그인 미설치 시

agent-council 플러그인 자체가 없는 경우 single 모드로 폴백:

```
⚠️ agent-council 플러그인이 설치되어 있지 않습니다.
→ Claude 단일 리뷰로 진행합니다.
```
