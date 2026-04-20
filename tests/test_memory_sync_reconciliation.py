"""Memory Sync Reconciliation 섹션 구조 검증 (BL-092).

finishing-a-development-branch 옵션 A/B와 using-devflow Resume Flow에
Memory Sync 관련 섹션이 회귀 없이 유지되는지 정적 검증.

L3 관측 hint는 만료일(2026-04-28) 이후 warning 모드로 전환되며,
HARD_FAIL_DATE(2026-05-05, +7일 유예) 이후에만 fail하여 제거 강제.
"""
import datetime
import pathlib
import warnings

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

    def test_has_cwd_scoped_memory_path(self):
        """M2: 메모리 대상은 현재 repo(cwd) 디렉토리로만 한정됨을 명시."""
        assert "현재 repo(cwd)에 매핑되는" in self.content, (
            "Missing cwd-scoping clause (M2 fix)"
        )
        assert "<dashed-cwd>" in self.content, (
            "Missing dashed-cwd path pattern (M2 fix)"
        )
        assert "다른 프로젝트 memory는 건드리지 않는다" in self.content, (
            "Missing cross-project isolation clause (M2 fix)"
        )

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

    def test_uses_upstream_based_ahead_check(self):
        """H1: upstream 대비 ahead check (origin/main 고정 비교가 아님)."""
        assert "git rev-list --count @{upstream}..HEAD" in self.content, (
            "Must use @{upstream}..HEAD (not origin/main..HEAD) for ahead check"
        )
        assert "upstream이 미설정이면 이 신호는 스킵" in self.content, (
            "Missing upstream-absent skip clause"
        )

    def test_merge_history_signal_removed(self):
        """H2: 불안정한 PR/BL 번호 비교 signal은 제거됨."""
        assert "git log --first-parent main" not in self.content, (
            "Merge history comparison signal should be removed (H2)"
        )

    def test_has_audit_log_on_skip(self):
        """M1: B 선택 시 audit.md에 override 이벤트 기록."""
        assert "memory-sync-staleness-skipped" in self.content, (
            "Missing audit log event name for skipped override (M1)"
        )

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
    """BL-092 L3 관측 hint의 lifecycle을 2단계로 관리:

    - 2026-04-28 (EXPIRY_DATE) 이전: hint 존재 보장 (회귀 방지)
    - 2026-04-28 ~ 2026-05-04: warning 모드 (통과하되 제거 알림)
    - 2026-05-05 (HARD_FAIL_DATE) 이후: hard fail로 제거 강제

    Codex adversarial review (H3) 권고 반영: 즉시 hard-fail 대신 7일 유예로
    긴급/핫픽스 작업 중 pipeline block 위험 완화.
    """

    EXPIRY_DATE = datetime.date(2026, 4, 28)
    HARD_FAIL_DATE = datetime.date(2026, 5, 5)
    HINT_MARKER = "관측 요청 (BL-092 L3"

    def setup_method(self):
        self.finishing = (
            SKILLS_DIR / "aidlc-finishing-a-development-branch" / "SKILL.md"
        ).read_text()
        self.using = (
            SKILLS_DIR / "aidlc-using-devflow" / "SKILL.md"
        ).read_text()

    def _hint_present(self):
        return (
            self.HINT_MARKER in self.finishing
            or self.HINT_MARKER in self.using
        )

    def _removal_guide(self, phase):
        return (
            f"\n\n=== BL-092 L3 hint {phase} ===\n"
            f"다음 파일에서 '{self.HINT_MARKER}' 블록 제거 필요:\n"
            f"  - skills/aidlc-finishing-a-development-branch/SKILL.md "
            f"(2곳: 옵션 A/B Memory Sync Reconciliation 섹션 말미)\n"
            f"  - skills/aidlc-using-devflow/SKILL.md "
            f"(Step 2.5 Memory Sync Staleness Check 말미)\n"
            f"제거 후 이 test 클래스(TestL3ObservationHintExpiry)도 함께 삭제."
        )

    def test_hints_lifecycle(self):
        today = datetime.date.today()

        if today < self.EXPIRY_DATE:
            # Phase 1: 만료 전 — hint 존재 보장
            assert self.HINT_MARKER in self.finishing, (
                f"L3 hint missing from finishing SKILL.md before expiry "
                f"{self.EXPIRY_DATE} (today={today})"
            )
            assert self.HINT_MARKER in self.using, (
                f"L3 hint missing from using-devflow SKILL.md before expiry "
                f"{self.EXPIRY_DATE} (today={today})"
            )
            assert self.finishing.count(self.HINT_MARKER) == 2, (
                "Expected hint in both 옵션 A and 옵션 B of finishing SKILL.md"
            )
        elif today < self.HARD_FAIL_DATE:
            # Phase 2: 만료 ~ +7일 — warning만, test는 통과
            if self._hint_present():
                days_over = (today - self.EXPIRY_DATE).days
                warnings.warn(
                    f"⚠️ BL-092 L3 hint 만료 경과 {days_over}일. "
                    f"{self.HARD_FAIL_DATE}부터 test hard-fail. 즉시 제거 권장."
                    + self._removal_guide(f"만료 경과 (현재 warning, {self.HARD_FAIL_DATE}부터 fail)"),
                    stacklevel=2,
                )
        else:
            # Phase 3: HARD_FAIL_DATE 이후 — hint 제거 강제
            guide = self._removal_guide(f"만료 + 유예 초과 ({self.HARD_FAIL_DATE})")
            assert self.HINT_MARKER not in self.finishing, guide
            assert self.HINT_MARKER not in self.using, guide
