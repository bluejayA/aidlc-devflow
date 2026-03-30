"""Quantitative Rubric and Structured Feedback validation tests.

Validates that:
- review-feedback-schema.md exists with required sections
- 4 code reviewer prompts reference the schema
- requesting-code-review uses Verdict system (PASS/CONDITIONAL/FAIL)
- construction-orchestrator has SDD mode gate for multi-unit
- SDD skill supports units.md input + orchestrator delegation mode
"""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent / "skills"


def read_skill(name: str) -> str:
    """Read a SKILL.md file content."""
    path = SKILLS_DIR / name / "SKILL.md"
    return path.read_text(encoding="utf-8")


def read_shared(relative_path: str) -> str:
    """Read a file from _shared directory."""
    path = SKILLS_DIR / "_shared" / relative_path
    return path.read_text(encoding="utf-8")


# --- Step 1: review-feedback-schema.md existence and required sections ---


class TestReviewFeedbackSchema:
    """review-feedback-schema.md must exist with all required sections."""

    def test_schema_file_exists(self):
        path = SKILLS_DIR / "_shared" / "patterns" / "review-feedback-schema.md"
        assert path.exists(), "review-feedback-schema.md must exist in _shared/patterns/"

    def test_schema_has_verdict_criteria(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert "PASS" in content and "CONDITIONAL" in content and "FAIL" in content, \
            "Schema must define PASS/CONDITIONAL/FAIL verdict criteria"

    def test_schema_has_issues_table_format(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert "Severity" in content and "File:Line" in content, \
            "Schema must define Issues table format with Severity and File:Line columns"

    def test_schema_has_score_table(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert "🟢" in content and "🟡" in content and "🔴" in content, \
            "Schema must define 3-level score (🟢/🟡/🔴)"

    def test_schema_has_context_section(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert "Context" in content, \
            "Schema must define Context section for domain-specific summaries"

    def test_schema_has_pass_criteria(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert "Pass Criteria" in content, \
            "Schema must define Pass Criteria checklist format"

    def test_schema_has_rubric_for_all_reviewers(self):
        content = read_shared("patterns/review-feedback-schema.md")
        for reviewer in ["spec", "quality", "security", "maintainability"]:
            assert reviewer.lower() in content.lower(), \
                f"Schema must include rubric items for {reviewer} reviewer"

    def test_schema_has_scoring_guidelines(self):
        """Each rubric item must have scoring guidelines (what is Good vs Needs Work)."""
        content = read_shared("patterns/review-feedback-schema.md")
        assert re.search(r"Good|Acceptable|Needs Work", content), \
            "Schema must include scoring guidelines for rubric items"


# --- Step 2: 4 code reviewer prompts reference the schema ---

REVIEWER_PROMPTS = [
    "reviewers/spec-reviewer-prompt.md",
    "reviewers/code-quality-reviewer-prompt.md",
    "reviewers/security-reviewer-prompt.md",
    "reviewers/maintainability-reviewer-prompt.md",
]


class TestReviewerSchemaReference:
    """All 4 code reviewer prompts must reference review-feedback-schema.md."""

    @pytest.mark.parametrize("prompt_path", REVIEWER_PROMPTS)
    def test_reviewer_references_schema(self, prompt_path):
        content = read_shared(prompt_path)
        assert "review-feedback-schema.md" in content, \
            f"{prompt_path} must reference review-feedback-schema.md"

    @pytest.mark.parametrize("prompt_path", REVIEWER_PROMPTS)
    def test_reviewer_has_verdict_output(self, prompt_path):
        content = read_shared(prompt_path)
        assert "Verdict" in content, \
            f"{prompt_path} must use Verdict in output format"

    @pytest.mark.parametrize("prompt_path", REVIEWER_PROMPTS)
    def test_reviewer_has_rubric_items(self, prompt_path):
        content = read_shared(prompt_path)
        assert re.search(r"🟢|🟡|🔴|Rubric|Score", content, re.IGNORECASE), \
            f"{prompt_path} must include rubric scoring items"

    def test_quality_reviewer_no_basic_security_check(self):
        """code-quality-reviewer must NOT have basic security check (moved to security)."""
        content = read_shared("reviewers/code-quality-reviewer-prompt.md")
        assert "기본 보안 체크" not in content, \
            "Basic security check must be removed from quality reviewer (moved to security)"

    def test_security_reviewer_has_context_section(self):
        """security-reviewer must have Context section (moved from Threat Surface)."""
        content = read_shared("reviewers/security-reviewer-prompt.md")
        # Should NOT have standalone Threat Surface as a report section
        # Should reference Context section from schema
        assert "review-feedback-schema.md" in content

    def test_maintainability_reviewer_has_context_section(self):
        """maintainability-reviewer must have Context section (moved from Change Impact Summary)."""
        content = read_shared("reviewers/maintainability-reviewer-prompt.md")
        assert "review-feedback-schema.md" in content


# --- Step 3: requesting-code-review Verdict system ---


class TestRequestingCodeReviewVerdict:
    """requesting-code-review must use Verdict system."""

    def test_has_verdict_in_result_format(self):
        content = read_skill("aidlc-requesting-code-review")
        assert "Verdict" in content, \
            "requesting-code-review must use Verdict in result format"

    def test_has_pass_conditional_fail(self):
        content = read_skill("aidlc-requesting-code-review")
        assert "PASS" in content and "CONDITIONAL" in content and "FAIL" in content, \
            "requesting-code-review must define PASS/CONDITIONAL/FAIL verdicts"

    def test_references_schema(self):
        content = read_skill("aidlc-requesting-code-review")
        assert "review-feedback-schema.md" in content, \
            "requesting-code-review must reference review-feedback-schema.md"

    def test_verdict_replaces_assessment(self):
        """Verdict should replace old 'Ready to merge | Needs fixes' assessment."""
        content = read_skill("aidlc-requesting-code-review")
        # The result return section should use Verdict, not the old Assessment
        assert re.search(r"Verdict.*PASS.*CONDITIONAL.*FAIL", content, re.DOTALL), \
            "Result return must use Verdict system"


# --- Step 4: construction-orchestrator SDD mode gate ---


class TestConstructionOrchestratorSDDGate:
    """construction-orchestrator must have SDD mode gate for multi-unit."""

    def test_has_sdd_mode_gate(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"sdd.*mode|SDD.*모드", content, re.IGNORECASE), \
            "construction-orchestrator must have SDD mode gate"

    def test_has_sdd_gate_meta_tag(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert "sdd-mode" in content, \
            "construction-orchestrator must have @gate for sdd-mode"

    def test_sdd_gate_has_options(self):
        """SDD gate must have A (SDD) and B (inline) options."""
        content = read_skill("aidlc-construction-orchestrator")
        has_sdd_option = re.search(r"A\).*SDD", content)
        has_inline_option = re.search(r"B\).*인라인|B\).*inline", content, re.IGNORECASE)
        assert has_sdd_option and has_inline_option, \
            "SDD gate must offer A) SDD and B) inline options"

    def test_sdd_references_subagent_driven_development(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert "subagent-driven-development" in content, \
            "SDD mode must reference aidlc-subagent-driven-development skill"

    def test_sdd_gate_positioned_after_units(self):
        """SDD gate must come after units-generation gate."""
        content = read_skill("aidlc-construction-orchestrator")
        units_pos = content.find("units-generation")
        sdd_pos = content.find("sdd-mode")
        assert units_pos > 0 and sdd_pos > 0 and sdd_pos > units_pos, \
            "SDD gate must be positioned after units-generation gate"


# --- Step 5: SDD skill units.md input mode ---


class TestSDDUnitsInputMode:
    """SDD skill must support units.md input and orchestrator delegation mode."""

    def test_sdd_has_units_input_mode(self):
        content = read_skill("aidlc-subagent-driven-development")
        assert "units.md" in content, \
            "SDD must support units.md as input source"

    def test_sdd_has_orchestrator_delegation_mode(self):
        content = read_skill("aidlc-subagent-driven-development")
        assert re.search(r"orchestrator.*위임|delegation.*mode|위임.*모드", content, re.IGNORECASE), \
            "SDD must have orchestrator delegation mode"

    def test_sdd_disables_finishing_branch_in_delegation(self):
        content = read_skill("aidlc-subagent-driven-development")
        assert re.search(r"finishing.*비활성|finishing.*disable|finishing.*skip", content, re.IGNORECASE), \
            "SDD must disable finishing-branch in delegation mode"

    def test_sdd_has_signal_interface(self):
        """SDD must parse the orchestrator signal format."""
        content = read_skill("aidlc-subagent-driven-development")
        assert "SDD:" in content and "units=" in content, \
            "SDD must parse 'SDD: units=[path]' signal format"

    def test_sdd_has_context_isolation(self):
        """SDD must enforce context isolation between units."""
        content = read_skill("aidlc-subagent-driven-development")
        assert re.search(r"격리|isolation|전달.*제한|전달.*금지", content, re.IGNORECASE), \
            "SDD must enforce context isolation between units"


# --- Third-party review: additional tests ---


class TestVerdictCriteriaMapping:
    """Verify precise verdict determination rules from FR-4."""

    def test_schema_verdict_pass_criteria(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert re.search(r"PASS.*0.*Critical.*0.*🔴", content, re.DOTALL), \
            "Schema must define PASS = 0 Critical + 0 🔴"

    def test_schema_verdict_fail_criteria(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert re.search(r"FAIL.*1\+.*Critical", content, re.DOTALL), \
            "Schema must define FAIL = 1+ Critical"

    def test_worst_of_aggregation(self):
        content = read_skill("aidlc-requesting-code-review")
        assert "worst-of" in content, \
            "requesting-code-review must define worst-of verdict aggregation"


class TestSDDSignalAndGateDetails:
    """Verify SDD signal format and gate details from FR-1/FR-2."""

    def test_orchestrator_sdd_signal_format(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert "SDD:" in content and "units=" in content and "summary=" in content, \
            "Orchestrator must define SDD signal format with units= and summary="

    def test_single_unit_auto_inline(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"unit.*1.*게이트.*없이.*인라인|unit.*1.*인라인.*자동", content, re.IGNORECASE), \
            "Single unit must skip SDD gate and auto-apply inline mode"

    def test_sdd_disables_unit_gates(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"게이트.*비활성|gate.*disable", content, re.IGNORECASE), \
            "SDD mode must disable code-plan and implementation gates"

    def test_sdd_functional_design_before_sdd(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"functional-design.*SDD.*전|SDD.*호출.*전.*functional-design", content, re.DOTALL), \
            "Functional design must be executed before SDD handoff"

    def test_single_unit_scenario_has_no_sdd_gate(self):
        scenario = Path(__file__).parent / "scenarios" / "construction-single-unit.yaml"
        content = scenario.read_text()
        assert "sdd-mode" not in content, \
            "Single-unit scenario must not include sdd-mode gate"


class TestSchemaCompleteness:
    """Verify schema preserves both severity and rubric systems."""

    def test_schema_has_context_heading_in_template(self):
        content = read_shared("patterns/review-feedback-schema.md")
        assert "### Context" in content, \
            "Schema output template must include ### Context heading"

    def test_schema_preserves_severity_alongside_rubric(self):
        content = read_shared("patterns/review-feedback-schema.md")
        has_severity = "Critical" in content and "Important" in content and "Minor" in content
        has_rubric = "🟢" in content and "🟡" in content and "🔴" in content
        assert has_severity and has_rubric, \
            "Schema must preserve Critical/Important/Minor alongside 🟢/🟡/🔴 rubric"

    @pytest.mark.parametrize("prompt_path", REVIEWER_PROMPTS)
    def test_reviewer_has_read_instruction(self, prompt_path):
        content = read_shared(prompt_path)
        assert re.search(r"Read|읽", content) and "review-feedback-schema.md" in content, \
            f"{prompt_path} must instruct reading review-feedback-schema.md"
