# workflow-planning

<!-- 워크플로우 계획: 어떤 스테이지를 실행할지 결정하고 사용자 승인을 받음 -->
<!-- ALWAYS 실행 — 반드시 명시적 사용자 승인 후 진행 -->

## Purpose

Determine which stages to execute and at what depth, then present the plan for explicit user approval.

## Always Execute

This stage always runs. User can override recommendations.

## Execution Steps

### Step 1: Load prior context

Read (if they exist):
- `devflow-docs/inception/workspace.md`
- `devflow-docs/inception/requirements.md`

### Step 2: Recommend stages

Based on the requirements, recommend which Construction stages to include:

| Stage | Include if |
|-------|-----------|
| `application-design` | New components or services needed |
| `units-generation` | System needs decomposition into parallel units |
| `code-generation` | **Always** |
| `build-and-test` | **Always** |

For each included stage, also recommend depth: Minimal / Standard / Comprehensive.

### Step 3: Generate workflow visualization

Create a simple text-based workflow diagram showing:
- Included stages in order
- Depth level for each stage
- Conditional stages marked with (?)

Example:
```
INCEPTION
  ✅ workspace-detection (완료)
  ✅ requirements-analysis (완료)
  ⏭ workflow-planning (현재)

CONSTRUCTION
  ➡ application-design [Standard] (?)
  ➡ units-generation [Minimal] (?)
  ➡ code-generation [Standard]
  ➡ build-and-test [Standard]
```

### Step 4: Present plan for approval

Display the plan and explicitly state:
```
위 계획을 검토해주세요. 스테이지를 추가하거나 제외할 수 있습니다.

A) 변경 요청 (포함/제외할 스테이지 또는 깊이 조정)
B) 계획 승인 후 진행
```

**MANDATORY**: Do NOT proceed until user explicitly selects B.

### Step 5: Save workflow plan

Create `devflow-docs/inception/workflow-plan.md` with approved plan.

### Step 6: Update state

Use devflow-state to record approved stages list.
Use devflow-audit to log approval.
