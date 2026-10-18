# Task: aidlc v1.9.0 Knowledge System Integration (Phase 1)

## Objective

Do NOT implement the provided SPEC v0.3 directly.

Instead, redesign the knowledge system by:

1) Defining a clear knowledge taxonomy
2) Mapping existing aidlc assets into that taxonomy
3) Proposing an integration plan with executable first steps

The goal is NOT to add a new system, but to:

**restructure existing knowledge into a coherent system**

---

## Context

aidlc v1.9.0 already contains fragmented knowledge components:
- devflow-state (session continuity)
- devflow-solutions (solution accumulation)
- devflow-audit (execution/evidence logs)
- existing skills (28+)
- backlog items (BL-057, BL-058, BL-081, BL-084, etc.)

The provided SPEC v0.3 introduces:
- session-state SSOT
- ADR (Decision layer)
- ingest L1/L2
- provenance
- thread model
- promotion_candidate

However:

**The system MUST integrate with existing structures, not replace them.**

---

## Step 1 — Discover Current State (MANDATORY)

Analyze the current aidlc codebase and document:

1. **Existing directories and files** related to:
   - devflow-state
   - devflow-solutions
   - devflow-audit
   - hooks
   - skills
   - docs storage (devflow-docs)

2. **Current data flows:**
   - Where session state is stored
   - How solutions are accumulated
   - How audit/evidence is logged

3. **Existing classification attempts:**
   - BL-081 (skill_nature tagging) — check if taxonomy work already started
   - Any existing type/category fields in skills or solutions
   - Any tagging, labeling, or categorization conventions already in use

4. **Existing implicit knowledge types**

5. **Actual file sizes** (sample-based):
   - Measure token count of key files (devflow-state, solution files, hook outputs)
   - This is the baseline for token budget analysis later

---

## Step 2 — Define Knowledge Taxonomy (CRITICAL)

Define a clear taxonomy with the following base types:
- Decision
- Solution
- Pattern
- Skill
- Evidence
- SessionState

### Important Rules

1. **This is a classification system, NOT a pipeline.**
   - DO NOT enforce a directional flow like:
     Decision → Solution → Pattern → Skill
   - In reality, relationships are many-to-many

2. **DO NOT force Decision (ADR) to be the central type.**
   - aidlc is solution-heavy and execution-heavy
   - Solution and Evidence may exist independently of Decision
   - Decision is one type among six, not the hub

3. **Define relationships explicitly**, e.g.:
   - Solution supports Decision
   - Pattern generalizes Solution
   - Skill operationalizes Solution or Pattern
   - Evidence validates Decision or Solution
   - SessionState references active Decision/Solution

4. **Each type must define:**
   - purpose
   - scope (project/shared/org)
   - storage location
   - lifecycle

5. **Integrate with existing classification attempts** found in Step 1.
   - If BL-081 skill_nature or other taxonomy work exists, build on top of it
   - Do not create a parallel classification system

6. **DO NOT introduce additional knowledge types beyond the 6 defined above.**
   Subtypes are NOT allowed in Phase 1. No meta-patterns, micro-patterns, evidence subcategories, etc.

---

## Step 3 — Map Existing Assets to Taxonomy

Map current aidlc structures:
- devflow-state → SessionState
- devflow-solutions → Solution
- devflow-audit → Evidence
- existing skills → Skill

Also identify:
- Pattern candidates (repeated solutions)
- Decision gaps (where ADR is missing but needed)

**Every existing asset must have ONE primary type, but MAY reference additional types. Do NOT split existing files just to enforce type purity.**

---

## Step 4 — Integrate SPEC v0.3 (Selective)

ONLY integrate the following principles:
- SSOT (single source of truth)
- Ingest Level 1 / Level 2 separation
- Provenance extension
- Thread is non-authoritative
- Forgetting based on code linkage (not time)
- promotion_candidate at Decision (ADR) level ONLY

DO NOT blindly introduce:
- new directory structures that conflict with existing ones
- redundant storage layers
- duplicate knowledge systems

### Conflict Resolution Rule

When integration conflicts with existing structure:
- **Prefer reclassification over duplication** — relabel existing files, don't create copies
- **Prefer modifying existing structure over adding new parallel structure**
- **DO NOT create shadow directories** (e.g., no `.devflow/wiki/` alongside existing `devflow-docs/`)

---

## Step 5 — Design Integration

### 5a. Read Path Definition (MANDATORY)

Define the minimal read path for each operation:

**Session start:**
- which files are read, in what order, why
- estimated token cost (based on actual file sizes from Step 1)

**File edit:**
- which files are read/written
- estimated token cost per edit

**ADR creation:**
- which files are read/written

**Ingest L2:**
- which files are read/written

### 5b. Hook Design (MANDATORY)

For each hook, define:
- purpose
- exact responsibility
- order of execution (knowledge first, workflow second)
- interaction with existing hooks (extend, not duplicate)

Hooks to cover:
- session start
- file edit
- ADR update
- session end

### 5c. Structure Proposal

Propose:
1. Updated directory structure (minimal change from current)
2. Where ADR (Decision) layer should be added
3. How existing solutions integrate (no duplication)
4. How ingest L1/L2 fits into current hooks
5. How knowledge types coexist in existing devflow-docs

---

## Step 6 — Output Required

Produce THREE documents:

### 1. knowledge-taxonomy.md

Must include:
- definitions of each knowledge type (6 types only, no subtypes)
- relationships (non-linear, many-to-many)
- examples from actual aidlc codebase
- mapping table (existing asset → primary type)

### 2. aidlc-knowledge-integration-plan.md

Must include:
- current state summary
- integration strategy (A + C approach)
- directory plan (minimal changes)
- hook integration plan (with execution order)
- read path for each operation (with token estimates)
- migration approach (incremental; small breaking changes acceptable if explicitly documented and scoped)
- **token budget analysis**: based on actual file sizes measured in Step 1. Per session start, per file edit, per ingest. Comparison with current baseline. Optimization strategies (lazy loading, summary-only reads, metadata-first access). Avoid generic estimates — use real numbers.

### 3. executable-next-steps.md

Must include:
- first 5 concrete changes to apply in repo
- exact file paths
- minimal diffs (before/after)
- order of execution
- expected result of each change

**This document must be directly executable — not a proposal, but a patch plan.**

---

## Constraints

- DO NOT break existing devflow behavior
- DO NOT introduce parallel systems
- DO NOT assume greenfield design
- DO NOT introduce new top-level directories
- DO NOT expand taxonomy beyond 6 types in Phase 1
- MUST work incrementally on top of v1.9.0
- **Prioritize minimal viable structure over completeness.** If a simpler design satisfies 80% of the requirement, choose it over a complete design.
- **MUST evaluate token efficiency at every design decision.** Every file that hooks/skills read at session start, every file edit, every ingest operation consumes tokens. For each proposed structure, estimate: how many tokens does this add per session? Per file edit? Can the same goal be achieved with fewer reads? Prefer summarized/structured output over full-file reads. Lazy loading (read title/metadata first, full content only when needed) over eager loading.

---

## Success Criteria

- [ ] No duplicate storage for the same knowledge
- [ ] Every existing asset has exactly one primary type (additional type references allowed)
- [ ] No new top-level directory introduced
- [ ] Session start token overhead does not exceed +20% vs current baseline
- [ ] Existing workflows continue without modification, or changes are explicitly documented
- [ ] Read path is defined for every operation
- [ ] Hook execution order is explicitly defined

---

## Final Goal

Transform aidlc into a system where:
- knowledge is structured
- decisions are traceable
- solutions accumulate
- patterns emerge
- execution produces evidence
- sessions never lose context

---

## One-line Principle

**This is not building a new system.
This is organizing what already exists into a coherent knowledge architecture.**
