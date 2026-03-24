"""Tests for BL-043: Code Review Agent Teams.

Validates agent files, review team protocol, and R3 mode integration.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
SHARED_PATTERNS = REPO_ROOT / "skills" / "_shared" / "patterns"
SKILL_DIR = REPO_ROOT / "skills" / "aidlc-requesting-code-review"

REVIEWER_AGENTS = [
    "spec-reviewer",
    "quality-reviewer",
    "security-reviewer",
    "maintainability-reviewer",
]

REQUIRED_AGENT_SECTIONS = [
    "## 역할",
    "## 팀 소통 프로토콜",
    "## 출력 형식",
]


class TestReviewerAgents:
    """Step 1: 역할별 리뷰어 에이전트 파일 검증."""

    @pytest.mark.parametrize("agent_name", REVIEWER_AGENTS)
    def test_agent_file_exists(self, agent_name):
        path = AGENTS_DIR / f"{agent_name}.md"
        assert path.exists(), f"Agent file missing: {path}"

    @pytest.mark.parametrize("agent_name", REVIEWER_AGENTS)
    def test_agent_has_required_sections(self, agent_name):
        path = AGENTS_DIR / f"{agent_name}.md"
        if not path.exists():
            pytest.skip(f"Agent file not yet created: {agent_name}")
        content = path.read_text()
        for section in REQUIRED_AGENT_SECTIONS:
            assert section in content, (
                f"{agent_name}.md missing section: {section}"
            )

    @pytest.mark.parametrize("agent_name", REVIEWER_AGENTS)
    def test_agent_references_reviewer_prompt(self, agent_name):
        """에이전트가 대응하는 _shared/reviewers/ 프롬프트를 참조하는지."""
        path = AGENTS_DIR / f"{agent_name}.md"
        if not path.exists():
            pytest.skip(f"Agent file not yet created: {agent_name}")
        content = path.read_text()
        assert "_shared/reviewers/" in content, (
            f"{agent_name}.md should reference its reviewer prompt"
        )


PROTOCOL_REQUIRED_SECTIONS = [
    "## 팀 생성",
    "## 리뷰어 Spawn",
    "## 소통 규칙",
    "## 결과 종합",
    "## 팀 정리",
]


class TestReviewTeamProtocol:
    """Step 2: review-team-protocol.md 검증."""

    def test_protocol_file_exists(self):
        path = SHARED_PATTERNS / "review-team-protocol.md"
        assert path.exists(), f"Protocol file missing: {path}"

    def test_protocol_has_required_sections(self):
        path = SHARED_PATTERNS / "review-team-protocol.md"
        if not path.exists():
            pytest.skip("Protocol file not yet created")
        content = path.read_text()
        for section in PROTOCOL_REQUIRED_SECTIONS:
            assert section in content, (
                f"review-team-protocol.md missing section: {section}"
            )

    def test_protocol_references_team_tools(self):
        """프로토콜이 TeamCreate, Agent, SendMessage, TeamDelete를 참조하는지."""
        path = SHARED_PATTERNS / "review-team-protocol.md"
        if not path.exists():
            pytest.skip("Protocol file not yet created")
        content = path.read_text()
        for tool in ["TeamCreate", "SendMessage", "TeamDelete"]:
            assert tool in content, (
                f"review-team-protocol.md should reference {tool}"
            )


class TestR3ModeInSkill:
    """Step 3: SKILL.md에 R3 모드 존재 검증."""

    def test_skill_has_r3_option(self):
        path = SKILL_DIR / "SKILL.md"
        content = path.read_text()
        assert "R3)" in content, "SKILL.md should define R3 option"

    def test_skill_has_teams_review_step(self):
        path = SKILL_DIR / "SKILL.md"
        content = path.read_text()
        assert "Agent Teams" in content, (
            "SKILL.md should reference Agent Teams"
        )

    def test_skill_references_protocol(self):
        path = SKILL_DIR / "SKILL.md"
        content = path.read_text()
        assert "review-team-protocol" in content, (
            "SKILL.md should reference review-team-protocol.md"
        )


class TestR3Integration:
    """Step 4: R3 모드 통합 검증."""

    def test_r3_graceful_degradation_documented(self):
        """프로토콜에 graceful degradation이 문서화되었는지."""
        path = SHARED_PATTERNS / "review-team-protocol.md"
        content = path.read_text()
        assert "Graceful Degradation" in content

    def test_all_reviewer_agents_referenced_in_protocol(self):
        """프로토콜이 모든 리뷰어 에이전트를 참조하는지."""
        path = SHARED_PATTERNS / "review-team-protocol.md"
        content = path.read_text()
        for agent in REVIEWER_AGENTS:
            assert agent in content, (
                f"Protocol should reference {agent}"
            )

    def test_skill_r3_mentions_explore_type(self):
        """R3 모드가 Explore 타입을 사용하는지 명시."""
        path = SKILL_DIR / "SKILL.md"
        content = path.read_text()
        assert "Explore" in content, (
            "R3 mode should specify Explore agent type"
        )
