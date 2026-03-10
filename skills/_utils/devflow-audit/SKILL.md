---
name: devflow-audit
description: Appends interaction logs to devflow-docs/audit.md in append-only mode. Never overwrite — always append.
metadata:
  version: 0.3.0
  author: Jay
  category: ai-dlc-workflow
  invoke_mode: orchestrator-only
---

# devflow-audit

<!-- devflow-audit: devflow-docs/audit.md에 append-only로 모든 상호작용을 기록 -->
<!-- 사용자 입력과 AI 응답을 원문 그대로 보존 -->

## Purpose

Append interaction logs to `devflow-docs/audit.md`. This file is APPEND-ONLY — never overwrite its contents.

## Critical Rules

1. **ALWAYS append** — never use tools that overwrite the entire file
2. **Read first, then edit** — use Edit tool to append, never Write tool on the full file
3. **Raw input only** — never summarize or paraphrase user input
4. **ISO 8601 timestamps** — always include full timestamp

## Log Entry Format

Each entry must follow this exact format:

```markdown
## [Stage Name]
**Timestamp**: [YYYY-MM-DDTHH:MM:SSZ]
**User Input**: "[Complete raw user input — never summarized]"
**AI Response**: "[Action taken or response given]"
**Context**: [Stage name, decision made, or notable event]

---
```

## When to Log

Log at these moments:
- When user sends any message during a devflow workflow
- When a stage completes (log the completion)
- When a stage is skipped (log the skip + reason)
- When user approves or requests changes at a gate

## How to Append

<!-- 올바른 방법: Read 후 Edit으로 추가 -->
1. Check if `devflow-docs/audit.md` exists
2. If not: create with header `# devflow Audit Log\n\n`
3. Append the new entry using Edit tool at end of file
4. NEVER use Write tool to rewrite the entire file

## Correct Tool Usage

✅ CORRECT:
1. Read `devflow-docs/audit.md`
2. Use Edit tool to append new entry at end

❌ WRONG:
1. Read `devflow-docs/audit.md`
2. Use Write tool with old content + new content (this is a full overwrite)
