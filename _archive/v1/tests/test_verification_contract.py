"""Verification Contract and Self-Healing Loop validation tests.

Validates that:
- code-generation Plan template includes Verification Contract section
- code-plan-reviewer checks Verification Contract existence/completeness
- build-and-test references Verification Contract from code-plan
- construction-orchestrator includes auto-fix preprocessing before completion gate
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


# --- FR-1: Verification Contract in code-generation Plan template ---


class TestVerificationContractTemplate:
    """code-generation Plan template must include Verification Contract section."""

    def test_plan_template_has_verification_contract_section(self):
        content = read_skill("aidlc-code-generation")
        assert "## Verification Contract" in content, (
            "code-generation SKILL.md must include '## Verification Contract' in Plan template"
        )

    def test_verification_contract_has_completion_criteria(self):
        content = read_skill("aidlc-code-generation")
        assert re.search(r"완료 조건|completion criteria", content, re.IGNORECASE), (
            "Verification Contract must include completion criteria"
        )

    def test_verification_contract_has_verification_commands(self):
        content = read_skill("aidlc-code-generation")
        assert re.search(r"검증 명령|verification command", content, re.IGNORECASE), (
            "Verification Contract must include verification commands"
        )

    def test_verification_contract_has_risk_tags(self):
        content = read_skill("aidlc-code-generation")
        assert re.search(r"리스크 태그|risk tag", content, re.IGNORECASE), (
            "Verification Contract must include risk tags"
        )


# --- FR-1a: code-plan-reviewer checks Verification Contract ---


class TestCodePlanReviewerContract:
    """code-plan-reviewer must check Verification Contract existence."""

    def test_reviewer_checks_verification_contract(self):
        content = read_shared("reviewers/code-plan-reviewer-prompt.md")
        assert "Verification Contract" in content, (
            "code-plan-reviewer must check Verification Contract section"
        )


# --- FR-2: build-and-test references Verification Contract ---


class TestBuildAndTestContractReference:
    """build-and-test must reference Verification Contract from code-plan."""

    def test_references_verification_contract(self):
        content = read_skill("aidlc-build-and-test")
        assert "Verification Contract" in content, (
            "build-and-test must reference Verification Contract"
        )

    def test_graceful_fallback_when_no_contract(self):
        content = read_skill("aidlc-build-and-test")
        assert re.search(r"없으면|fallback|기존 동작", content), (
            "build-and-test must have graceful fallback when no Verification Contract"
        )

    def test_rerun_full_verification_on_auto_fix(self):
        """auto-fix 후 재실행 시에도 검증 명령 전체를 다시 실행해야 한다."""
        content = read_skill("aidlc-build-and-test")
        assert re.search(r"auto-fix.*재실행|다시 실행|전체를 다시", content), (
            "build-and-test must mention re-running full verification after auto-fix"
        )


# --- FR-3: code-generation auto-fix signal ---


class TestCodeGenerationAutoFixSignal:
    """code-generation must accept auto-fix error context in GENERATE signal."""

    def test_auto_fix_signal_format_documented(self):
        content = read_skill("aidlc-code-generation")
        assert re.search(r"auto-fix for \[unit-name\]", content), (
            "code-generation must document auto-fix signal format"
        )

    def test_partial_fix_behavior_documented(self):
        """에러 컨텍스트가 있으면 해당 부분만 수정해야 한다."""
        content = read_skill("aidlc-code-generation")
        assert re.search(r"해당 부분만 수정|fix only the failing", content), (
            "code-generation must document partial fix behavior for auto-fix"
        )


# --- FR-3/FR-4: Self-Healing Loop in construction-orchestrator ---


class TestSelfHealingLoop:
    """construction-orchestrator must include auto-fix preprocessing."""

    def test_auto_fix_section_exists(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"auto-fix|Self-Healing|자동 수정", content), (
            "construction-orchestrator must include auto-fix/Self-Healing section"
        )

    def test_max_retry_defined(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"max.?retry|최대.*재시도|3회", content), (
            "construction-orchestrator must define max retry count"
        )

    def test_plateau_detection_defined(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"plateau|동일.*에러.*패턴", content), (
            "construction-orchestrator must define plateau detection"
        )

    def test_structural_problem_escalation(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"빌드 실패|구조적 문제|즉시.*에스컬레이션|structural", content), (
            "construction-orchestrator must escalate structural problems immediately"
        )

    def test_existing_gate_structure_preserved(self):
        """Existing 3-branch completion gate must be preserved."""
        content = read_skill("aidlc-construction-orchestrator")
        assert "systematic-debugging" in content, (
            "Existing debugging routing must be preserved"
        )
        assert re.search(r"CONSTRUCTION.*완료.*승인|CONSTRUCTION-complete", content), (
            "Existing completion approval must be preserved"
        )

    def test_audit_logging_for_auto_fix(self):
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"auto-fix.*audit|audit.*auto-fix|자동 수정.*기록", content), (
            "Auto-fix attempts must be logged to audit"
        )

    def test_environment_problem_escalation(self):
        """환경 문제(missing binary, permission denied)는 즉시 에스컬레이션."""
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"환경 문제|missing binary|permission denied", content), (
            "construction-orchestrator must escalate environment problems immediately"
        )

    def test_auth_security_risk_tag_escalation(self):
        """auth/security 리스크 태그가 있는 unit은 auto-fix를 시도하지 않는다."""
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"auth/security", content), (
            "construction-orchestrator must mention auth/security risk tag escalation"
        )

    def test_auto_fix_success_message_format(self):
        """auto-fix 성공 시 '(auto-fix [N]회 적용됨)' 안내가 있어야 한다."""
        content = read_skill("aidlc-construction-orchestrator")
        assert re.search(r"auto-fix.*회.*적용", content), (
            "construction-orchestrator must show auto-fix count on success"
        )
