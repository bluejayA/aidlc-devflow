"""Memory Sync Reconciliation 섹션 구조 검증 (BL-092).

finishing-a-development-branch 옵션 A/B와 using-devflow Resume Flow에
Memory Sync 관련 섹션이 회귀 없이 유지되는지 정적 검증.

추가로 L3 관측 hint의 만료일(2026-04-28) 경과 시 자동 fail하여 제거를 강제.
"""
import datetime
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


class TestL3ObservationHintExpiry:
    """BL-092 L3 관측 hint는 2026-04-28 T+14 만료.

    만료일 이후 hint가 남아있으면 이 test가 fail하여 제거를 강제한다.
    만료 전에는 hint 존재를 보장해 회귀를 방지한다.
    """

    EXPIRY_DATE = datetime.date(2026, 4, 28)
    HINT_MARKER = "관측 요청 (BL-092 L3"

    def setup_method(self):
        self.finishing = (
            SKILLS_DIR / "aidlc-finishing-a-development-branch" / "SKILL.md"
        ).read_text()
        self.using = (
            SKILLS_DIR / "aidlc-using-devflow" / "SKILL.md"
        ).read_text()

    def test_hints_lifecycle(self):
        today = datetime.date.today()
        if today < self.EXPIRY_DATE:
            # 만료 전: hint 존재 보장 (실수로 삭제되면 fail)
            assert self.HINT_MARKER in self.finishing, (
                f"L3 hint missing from finishing SKILL.md before expiry "
                f"{self.EXPIRY_DATE} (today={today})"
            )
            assert self.HINT_MARKER in self.using, (
                f"L3 hint missing from using-devflow SKILL.md before expiry "
                f"{self.EXPIRY_DATE} (today={today})"
            )
            # 옵션 A와 B 두 곳에 모두 존재해야 함
            assert self.finishing.count(self.HINT_MARKER) == 2, (
                "Expected hint in both 옵션 A and 옵션 B of finishing SKILL.md"
            )
        else:
            # 만료 후: hint 제거돼야 함
            removal_guide = (
                f"\n\n=== BL-092 L3 hint 만료 ({self.EXPIRY_DATE}) ===\n"
                f"다음 파일에서 '{self.HINT_MARKER}' 블록 제거 필요:\n"
                f"  - skills/aidlc-finishing-a-development-branch/SKILL.md "
                f"(2곳: 옵션 A/B의 Memory Sync Reconciliation 섹션 말미)\n"
                f"  - skills/aidlc-using-devflow/SKILL.md "
                f"(Step 2.5 Memory Sync Staleness Check 말미)\n"
                f"제거 후 이 test 클래스(TestL3ObservationHintExpiry)도 함께 삭제."
            )
            assert self.HINT_MARKER not in self.finishing, removal_guide
            assert self.HINT_MARKER not in self.using, removal_guide
