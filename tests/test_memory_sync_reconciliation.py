"""Memory Sync Reconciliation 섹션 구조 검증 (BL-092).

finishing-a-development-branch 옵션 A/B와 using-devflow Resume Flow에
Memory Sync 관련 섹션이 회귀 없이 유지되고, audit.md 이벤트 로깅 포맷이
일관되게 유지되는지 정적 검증.

Codex Round 2 리뷰 반영: L3 hint + 만료 강제 접근은 폐기. 관측은 audit.md
이벤트 로깅으로 대체. T+14 재평가 사항은 project_bl092_observation.md memory.
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
        for keyword in ["project_*.md", "feedback_*.md", "Next에서 완료/승격"]:
            assert keyword in self.content, f"Missing checklist keyword: {keyword}"

    def test_has_no_op_clause_for_absent_auto_memory(self):
        assert "auto-memory 시스템이 구성돼 있지 않으면" in self.content
        assert "no-op" in self.content

    def test_has_cwd_scoped_memory_path(self):
        """M2: 메모리 대상은 현재 repo(cwd) 디렉토리로만 한정됨을 명시."""
        assert "현재 repo(cwd)에 매핑되는" in self.content
        assert "<dashed-cwd>" in self.content
        assert "다른 프로젝트 memory는 건드리지 않는다" in self.content

    def test_has_reconciliation_prompted_event(self):
        """M1: audit 이벤트 이름 지정 (고정 포맷)."""
        assert "memory-sync-reconciliation-prompted" in self.content, (
            "Missing reconciliation-prompted audit event"
        )

    def test_reconciliation_audit_has_option_and_choice_fields(self):
        """audit 이벤트 포맷 필드 검증: option, choice."""
        for field in ["option=<A|B>", "choice=<sync|skip>"]:
            assert field in self.content, f"Missing audit field: {field}"

    def test_audit_writes_to_devflow_docs_audit_md(self):
        """audit.md append 지시 포함."""
        assert "devflow-docs/audit.md" in self.content

    def test_l3_hint_removed(self):
        """Codex Round 2 반영: 임시 L3 hint 블록은 제거됨."""
        assert "관측 요청 (BL-092 L3" not in self.content, (
            "L3 observation hint should be removed (superseded by audit logging)"
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

    def test_has_upstream_preflight(self):
        """H1: upstream 존재를 ahead check 이전에 확인."""
        assert "git rev-parse --abbrev-ref --symbolic-full-name @{upstream}" in self.content, (
            "Missing upstream preflight command"
        )
        # Preflight 실패(미설정) 시 step 종료 지시
        assert "upstream 미설정" in self.content
        assert "staleness check 비활성" in self.content

    def test_uses_upstream_based_ahead_check(self):
        """H1: ahead check는 @{upstream} 기준 (origin/main 고정 아님)."""
        assert "git rev-list --count @{upstream}..HEAD" in self.content

    def test_merge_history_signal_removed(self):
        """H2: 불안정한 PR/BL 번호 비교 signal은 영구히 제거됨."""
        assert "git log --first-parent main" not in self.content, (
            "Merge history comparison signal should stay removed"
        )

    def test_has_staleness_check_run_event(self):
        """M1 확장: preflight 통과 시 항상 실행 기록."""
        assert "memory-sync-staleness-check-run" in self.content

    def test_has_staleness_skipped_event(self):
        """M1: B 선택 시 skipped 이벤트 기록."""
        assert "memory-sync-staleness-skipped" in self.content

    def test_audit_events_have_required_fields(self):
        """포맷 필드 검증: branch, ahead, prompted (check-run) / reason (skipped)."""
        for field in [
            "branch=<name>",
            "ahead=<N>",
            "prompted=<true|false>",
            "reason=<optional>",
        ]:
            assert field in self.content, f"Missing audit field spec: {field}"

    def test_has_no_op_clause(self):
        assert "no-op" in self.content

    def test_l3_hint_removed(self):
        """Codex Round 2 반영: 임시 L3 hint 블록은 제거됨."""
        assert "관측 요청 (BL-092 L3" not in self.content, (
            "L3 observation hint should be removed (superseded by audit logging)"
        )

    def test_positioned_between_step_2_and_step_3(self):
        """Step 2 이후, Step 3 이전에 위치."""
        resume_flow_start = self.content.index("### Resume Flow")
        step_2 = self.content.index(
            "session-summary.md` 읽기 (있으면)", resume_flow_start
        )
        staleness = self.content.index("Memory Sync Staleness Check", step_2)
        step_3 = self.content.index("백로그 확인 (Lazy Loading)", staleness)
        assert step_2 < staleness < step_3, (
            "Staleness Check must be positioned between Step 2 and Step 3"
        )
