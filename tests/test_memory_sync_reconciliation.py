"""Memory Sync Reconciliation 섹션 구조 검증 (BL-092).

finishing-a-development-branch 옵션 A/B와 using-devflow Resume Flow에
Memory Sync 관련 섹션이 회귀 없이 유지되는지 정적 검증.
"""
import pathlib

SKILLS_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills"


class TestFinishingMemorySyncReconciliation:
    """aidlc-finishing-a-development-branch SKILL.md 옵션 A/B에
    Memory Sync Reconciliation 섹션이 올바르게 추가되었는지 검증."""

    def setup_method(self):
        self.content = (
            SKILLS_DIR / "aidlc-finishing-a-development-branch" / "SKILL.md"
        ).read_text()

    def test_appears_twice_for_options_a_and_b(self):
        count = self.content.count("**Memory Sync Reconciliation**")
        assert count == 2, (
            f"Expected 2 occurrences (옵션 A + 옵션 B), got {count}"
        )

    def test_has_sync_skip_prompt(self):
        for token in ['"동기화"', '"건너뛰기"']:
            assert token in self.content, f"Missing prompt token: {token}"

    def test_has_checklist_keywords(self):
        for keyword in [
            "project_*.md",
            "feedback_*.md",
            "Next에서 완료/승격",
        ]:
            assert keyword in self.content, f"Missing checklist keyword: {keyword}"

    def test_has_no_op_clause_for_absent_auto_memory(self):
        assert "auto-memory 시스템이 구성돼 있지 않으면" in self.content
        assert "no-op" in self.content

    def test_positioned_before_state_update_markers(self):
        """Memory Sync Reconciliation 섹션이 각 옵션의 @state-update 주석 앞에 위치."""
        for marker in (
            "<!-- @state-update: 옵션 A 완료",
            "<!-- @state-update: 옵션 B PR 생성",
        ):
            marker_pos = self.content.index(marker)
            section_pos = self.content.rfind(
                "**Memory Sync Reconciliation**", 0, marker_pos
            )
            assert section_pos > 0, (
                f"Memory Sync Reconciliation section not found before {marker}"
            )


class TestUsingDevflowStalenessCheck:
    """aidlc-using-devflow SKILL.md Resume Flow에 Memory Sync
    Staleness Check step이 올바르게 추가되었는지 검증."""

    def setup_method(self):
        self.content = (
            SKILLS_DIR / "aidlc-using-devflow" / "SKILL.md"
        ).read_text()

    def test_has_staleness_check_block(self):
        assert "Memory Sync Staleness Check" in self.content

    def test_has_merge_history_check_command(self):
        assert "git log --first-parent main" in self.content

    def test_has_ahead_count_check_command(self):
        assert "git rev-list --count origin/main..HEAD" in self.content

    def test_has_no_op_clause(self):
        assert "no-op" in self.content

    def test_positioned_between_step_2_and_step_3(self):
        """Step 2 (session-summary 읽기) 이후, Step 3 (백로그 확인) 이전에 위치."""
        resume_flow_start = self.content.index("### Resume Flow")
        step_2 = self.content.index(
            "session-summary.md` 읽기 (있으면)", resume_flow_start
        )
        staleness = self.content.index("Memory Sync Staleness Check", step_2)
        step_3 = self.content.index("백로그 확인 (Lazy Loading)", staleness)
        assert step_2 < staleness < step_3, (
            "Staleness Check must be positioned between Step 2 and Step 3"
        )
