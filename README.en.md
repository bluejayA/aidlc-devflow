# aidlc-devflow

English | [한국어](README.md)

![version](https://img.shields.io/badge/version-1.1.0-blue)
![skills](https://img.shields.io/badge/skills-27-green)
![tests](https://img.shields.io/badge/tests-95-brightgreen)

A Claude Code development workflow plugin implementing the AI-DLC methodology with an **orchestrator-centric architecture**.

Built upon the concepts of [AI-DLC (AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows), with reference to the [Superpowers plugin](https://github.com/obra/superpowers).
A single orchestrator (`aidlc-using-devflow`) owns and drives the entire lifecycle, while all other stage skills act as pure executors.

> **New here?** [How It Works](docs/guide/how-it-works.md) — A jargon-free overview of the entire flow

> **Usage** [User Guide](docs/guide/user-guide.md) — Getting started, question patterns, gates, standalone skills

> **Customize** [Operator Guide](docs/guide/operator-guide.md) — Tech catalog, question principles, workflow defaults

> **Architecture** [Architecture](docs/guide/architecture.md) — 3-tier delegation chain, review system, 7 skill patterns

---

## How It Works

When you start a software development task, `aidlc-using-devflow` activates automatically.
The session-start hook (`hooks/session-start`) injects the `aidlc-using-devflow` context into Claude, enabling automatic detection of development requests.

The orchestrator drives the entire lifecycle according to the Stage Routing Table.
After each stage completes, the orchestrator presents an approval gate. Stage skills return their results and terminate immediately.

---

## Workflow

### INCEPTION — Decide What to Build

1. **aidlc-using-devflow** — Entry point. Checks for existing session resume, then starts orchestration
2. **aidlc-workspace-detection** — Greenfield/Brownfield detection. Collects tech stack + code structure for Brownfield
3. **aidlc-requirements-analysis** — Adaptive-depth (Minimal / Standard / Comprehensive) requirements analysis. Presents options when interpretations diverge
4. **aidlc-user-stories** _(conditional)_ — Converts requirements to INVEST-compliant user stories (Pre-Planning)
5. **aidlc-nfr-requirements** _(conditional)_ — Domain context + profile-based non-functional requirements (Pre-Planning, GENERATE/IMPORT)
6. **aidlc-workflow-planning** — Plans stages and depth, requests explicit approval
7. **aidlc-application-design** _(conditional)_ — Component/service design + NFR Design Patterns (Comprehensive)
8. **aidlc-units-generation** _(conditional)_ — Decomposes complex systems into parallel development units

### CONSTRUCTION — Decide How to Build

9. **aidlc-using-git-worktrees** _(optional)_ — Creates isolated worktree right after workflow-planning approval
10. **aidlc-functional-design** _(conditional)_ — Detailed functional design at Comprehensive depth (domain entities, business rules, data flow)
11. **aidlc-code-generation** — Plan → orchestrator approval → Generate (TDD Iron Law: RED-GREEN-REFACTOR + Self-Review)
12. **aidlc-build-and-test** — Full build + test suite execution + reference documentation generation

---

## Skills (26)

### Core AI-DLC Stages

| Skill | Role |
|-------|------|
| `aidlc-using-devflow` | Orchestrator. Owns and drives the entire lifecycle |
| `aidlc-workspace-detection` | Greenfield/Brownfield detection + tech-stack/code-structure collection |
| `aidlc-requirements-analysis` | Adaptive requirements analysis. Presents options on interpretation divergence |
| `aidlc-user-stories` | Converts requirements to INVEST-compliant user stories (conditional, Pre-Planning) |
| `aidlc-nfr-requirements` | Domain context + profile-based NFR collection (conditional, GENERATE/IMPORT) |
| `aidlc-workflow-planning` | Execution plan creation (pure executor) |
| `aidlc-application-design` | Component/service design + NFR Design Patterns (conditional, pure executor) |
| `aidlc-units-generation` | Parallel development unit decomposition (conditional, pure executor) |
| `aidlc-using-git-worktrees` | Isolated development worktree creation after workflow-planning (optional) |
| `aidlc-functional-design` | CONSTRUCTION detailed functional design — domain entities, business rules, data flow (conditional, Comprehensive only) |
| `aidlc-code-generation` | 2-phase code generation — Plan then STOP, Generate after approval (TDD Iron Law + Self-Review) |
| `aidlc-build-and-test` | Build execution + full test suite + reference documentation generation |

### Development Workflow Tools

| Skill | Role |
|-------|------|
| `aidlc-brainstorming` | Transforms ideas into design documents. HARD-GATE — no code before design approval |
| `aidlc-writing-plans` | Converts design documents into task-level implementation plans |
| `aidlc-test-driven-development` | Enforces TDD Iron Law (Rigid). RED-GREEN-REFACTOR |
| `aidlc-subagent-driven-development` | Per-task subagent execution + 2-stage review (spec → quality) |
| `aidlc-executing-plans` | Batch execution of implementation plans + session resume support |
| `aidlc-superpowers-tracking` | Session skill usage tracking + workflow improvement insights |

### Development Quality Tools

| Skill | Role |
|-------|------|
| `aidlc-systematic-debugging` | Forces root cause investigation on bugs/failures + failure history analysis |
| `aidlc-verification-before-completion` | Forces actual verification commands before completion claims + regression test RED-GREEN verification |
| `aidlc-finishing-a-development-branch` | Post-development merge/PR/keep/discard handling |
| `aidlc-requesting-code-review` | 2-stage code review request (spec compliance → code quality). Single Source of Truth for review logic |
| `aidlc-receiving-code-review` | Systematic handling of code review feedback |
| `aidlc-dispatching-parallel-agents` | Dispatches independent tasks to parallel subagents |
| `aidlc-writing-skills` | TDD-based skill development + CSO principles |

### Utilities

| Skill | Role |
|-------|------|
| `_utils/devflow-state` | `devflow-docs/devflow-state.md` read/write |
| `_utils/devflow-audit` | `devflow-docs/audit.md` append-only logging |

### Shared Convention Documents

| File | Role |
|------|------|
| `_shared/devflow-conventions.md` | YAML metadata + Complexity/Depth mapping + Return/Review conventions + HARD-GATE + TDD Iron Law + Subagent conventions |
| `_shared/tdd-protocol.md` | TDD Iron Law, RED-GREEN-REFACTOR, Self-Review, rationalization prevention, Red Flags, regression test verification |
| `_shared/gate-patterns.md` | Standard/conditional/review-linked/Hold variant/mode selection gate pattern definitions |
| `_shared/import-review-protocol.md` | GENERATE/IMPORT mode definitions + Hold/Skip signal conventions |
| `_shared/patterns/three-mode-selection.md` | Together/Import/Skip mode selection pattern |
| `_shared/patterns/hold-mechanism.md` | Mid-step Hold signal + Resume conventions |
| `_shared/patterns/brownfield-exploration.md` | Existing codebase exploration protocol |
| `_shared/patterns/session-continuity.md` | Session resume artifact auto-loading + session-summary template + re-verification protocol |
| `_shared/patterns/skill-writing-guide.md` | Skill writing principles + TDD methodology — freedom design, progressive disclosure, CSO deep-dive, pressure scenarios |
| `_shared/patterns/persuasion-principles.md` | Persuasion principles for discipline-enforcing skills — rationalization prevention table methodology |
| `_shared/patterns/skill-pattern-catalog.md` | 7 skill pattern classifications + selection guide |
| `_shared/patterns/question-format-guide.md` | Question design principles — option design, level adaptation, contradiction detection |
| `_shared/patterns/tech-stack-defaults.md` | Tech stack index — presets, policy modes, application rules |
| `_shared/patterns/tech-stack-catalog.md` | Layer-specific tech catalog — option generation data |
| `_shared/reviewers/` | 8 review subagent prompts (artifact, code-plan, code-reviewer, implementer, spec, quality, skill, spec-document, plan-document) |

#### YAML Metadata Convention

All AI-DLC stage skills use the following metadata fields.

| Field | Value | Meaning |
|-------|-------|---------|
| `invoke_mode` | `orchestrator-only` | Only invocable by the orchestrator. No direct user invocation |
| `invoke_mode` | `user-invocable` | Standalone skill invocable directly by users |
| `return_behavior` | `stop-no-gate` | Displays result and STOPs. Approval gate owned by orchestrator |
| `output_path` | `devflow-docs/...` | Stage artifact storage path |

---

## Artifact Structure

All design decisions are automatically saved to `devflow-docs/`.

```
devflow-docs/
├── inception/
│   ├── workspace.md        # Workspace analysis results
│   ├── requirements.md     # Requirements document (with confirmed interpretations)
│   ├── user-stories.md     # User stories (conditional)
│   ├── nfr-requirements.md # Non-functional requirements (conditional)
│   ├── workflow-plan.md    # Approved execution plan
│   ├── application-design.md  # Component design (conditional)
│   └── units.md            # Development unit list (conditional)
├── construction/
│   ├── {unit}/
│   │   ├── functional-design.md  # Detailed functional design (conditional, Comprehensive)
│   │   └── code-plan.md    # Code generation plan + progress checkboxes
│   └── build-and-test/
│       ├── build-instructions.md  # Build instructions
│       └── test-instructions.md   # Test instructions
├── devflow-state.md        # Current stage state (for session resume)
└── audit.md                # Full interaction log (append-only)
```

---

## Prerequisites

### Required

| Item | Min Version | Purpose |
|------|------------|---------|
| **Git** | 2.20+ | Version control, worktree-isolated development |
| **Claude Code** | 2.x | Plugin host |

### For Test Infrastructure

Additional requirements for running the test infrastructure (`tests/run-all.sh`):

| Item | Min Version | Purpose |
|------|------------|---------|
| **Node.js** | 18+ | SKILL.md meta-tag parser (`parse-skills.js`) |
| **Python** | 3.12+ | pytest-based L1/L2/L3 tests |
| **uv** | 0.4+ | Python package management + pytest execution |

### Optional (for specific skills)

| Item | Purpose | Related Skills |
|------|---------|---------------|
| **GitHub CLI (`gh`)** | PR creation, issue management | `finishing-a-development-branch`, `using-devflow` |

### Quick Check

```bash
# Verify required tools
git --version && node --version && python3 --version && uv --version

# (Optional) GitHub CLI check
gh --version

# Install test dependencies + run
uv sync && bash tests/run-all.sh
```

---

## Installation

### Option 1: Marketplace (Recommended)

Install via [devflow-marketplace](https://github.com/bluejayA/devflow-marketplace):

```bash
# 1. Install marketplace
claude plugins install https://github.com/bluejayA/devflow-marketplace.git

# 2. The aidlc plugin is included automatically
```

The marketplace includes two implementations:
- `aidlc` — This plugin (Orchestrator-Centric)
- `devflow` — Distributed implementation (Enhanced Skills)

### Option 2: Standalone Installation

Install this plugin directly:

```bash
claude plugins install https://github.com/bluejayA/aidlc-devflow.git
```

### Verify Installation

After installation, start a new session and the welcome message appears automatically:

```
🔧 AIDLC devflow plugin is installed.
To start: "devflow 시작해줘" (or describe what you want to build)
```

---

## Differentiators

### Built-in Full-Cycle Skill Development Toolchain

aidlc-devflow is not just a plugin that runs skills — it includes a **complete toolchain for creating and validating skills**.

| Phase | Tools | Description |
|-------|-------|-------------|
| **Design** | `skill-pattern-catalog` (7 behavioral) + `skill-design-patterns` (5 structural) | Decision tree auto-recommends the right pattern |
| **Author** | `aidlc-writing-skills` + `skill-writing-guide` + `persuasion-principles` | TDD-based skill development. CSO principles + progressive disclosure |
| **Review** | `skill-reviewer` subagent | Metadata consistency, pattern fitness, gate declaration verification |
| **Test** | 3-Layer static verification (0 tokens) | L1 graph validation → L2 routing simulator → L3 step order checker |
| **Operate** | Consistency checklist + impact analysis conventions | Cross-reference and dependency impact checks on skill modifications |

When adding new skills or modifying existing ones, this toolchain ensures consistent quality from design through verification.

---

## Core AI-DLC Patterns

### 1. Explicit Approval Gating

The orchestrator centrally manages all approval gates.

```
## aidlc-workspace-detection complete

A) Request changes
B) Proceed to next stage
```

### 2. Automatic Artifact Documentation

Each stage's output is automatically saved to `devflow-docs/`.

### 3. Adaptive Depth + Interpretation Divergence Resolution

Analysis depth adjusts automatically based on request complexity. When multiple equally valid interpretations exist, they are resolved before proceeding.

| Depth | Condition | Interpretation Check |
|-------|-----------|---------------------|
| **Minimal** | Simple/clear request, low risk | None |
| **Standard** | Typical complexity | Only when interpretations diverge |
| **Comprehensive** | Multi-component, high risk, external integration | Always |

---

## References

- [AWS AI-DLC Methodology Blog](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) — MIT-0 License, Copyright Amazon.com, Inc.
- [obra/superpowers](https://github.com/obra/superpowers) — MIT License, Copyright Jesse Vincent
- [Skill Guide Compliance Review](docs/analysis/2026-03-10-skill-guide-review.md)

Third-party license details: [THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES)

---

## License

[MIT License](LICENSE)
