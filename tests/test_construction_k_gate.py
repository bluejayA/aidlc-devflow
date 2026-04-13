"""construction-orchestrator 게이트 변경 테스트.

FR-1 (Distrust by Default): 구현 게이트 R→S 전환 검증
FR-4 (Knowledge Compounding): Debugging 라우팅 verdict 소비 검증
Phase 1 Change 2 (2026-04-13): STORE ownership을 systematic-debugging으로 이관.
construction-orchestrator K-gate는 사용자 선택(K)) 대신 verdict를 자동 소비한다.

검증 항목:
1. 구현 게이트에서 R 옵션 제거, S 옵션 추가, 자동 리뷰 실행 명시
2. Debugging 라우팅에 직접 STORE 호출 없음 (writer = systematic-debugging 단독)
3. solution_verdict 소비 명시
4. verdict별 안내 (SAVE / DUPLICATE / REJECT) 존재
5. 재진입 방지 언급
6. audit prefix 규약 (solution-store / solution-duplicate / solution-reject)
7. error_message가 systematic-debugging 경유 보존 지시
8. Step 1.5 재검증 경로에는 K 게이트 미적용 명시
"""

import re
from pathlib import Path

SKILL_PATH = (
    Path(__file__).parent.parent
    / "skills"
    / "aidlc-construction-orchestrator"
    / "SKILL.md"
)


def read_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


# --- 파일 존재 확인 ---

class TestSkillFileExists:
    def test_skill_file_exists(self):
        assert SKILL_PATH.exists(), f"SKILL.md not found at {SKILL_PATH}"


# --- writer ownership = systematic-debugging 단독 ---

class TestNoDirectStoreCall:
    """construction-orchestrator는 STORE를 직접 호출하지 않는다 (옵션 α)."""

    def test_no_direct_store_call(self):
        content = read_skill()
        assert not re.search(r"devflow-solutions.*STORE\s*\(", content), (
            "K-gate에 devflow-solutions STORE 직접 호출이 남아있음 "
            "(writer ownership = systematic-debugging 단독이어야 함)"
        )

    def test_systematic_debugging_store_referenced(self):
        content = read_skill()
        assert re.search(r"systematic-debugging", content), (
            "systematic-debugging 참조가 없음 (STORE owner 명시 필요)"
        )


# --- verdict 소비 ---

class TestVerdictConsumption:
    """systematic-debugging Return의 solution_verdict를 소비해야 한다."""

    def test_solution_verdict_field(self):
        content = read_skill()
        assert "solution_verdict" in content, (
            "solution_verdict 필드 소비 언급이 없음"
        )

    def test_devflow_solutions_referenced(self):
        content = read_skill()
        assert "devflow-solutions" in content, (
            "devflow-solutions 언급이 없음 (설계 맥락 표시 필요)"
        )


# --- verdict별 안내 ---

class TestVerdictGuidance:
    """SAVE / DUPLICATE / REJECT 각 verdict에 대한 안내가 있어야 한다."""

    def test_save_verdict_guidance(self):
        content = read_skill()
        assert "SAVE" in content, "SAVE verdict 안내가 없음"

    def test_duplicate_verdict_guidance(self):
        content = read_skill()
        assert "DUPLICATE" in content, "DUPLICATE verdict 안내가 없음"

    def test_reject_verdict_guidance(self):
        content = read_skill()
        assert "REJECT" in content, "REJECT verdict 안내가 없음"

    def test_save_shows_saved_path(self):
        content = read_skill()
        assert "solution_saved_path" in content, (
            "SAVE verdict 시 solution_saved_path 표시 안내가 없음"
        )

    def test_duplicate_shows_similar_to(self):
        content = read_skill()
        assert "solution_similar_to" in content, (
            "DUPLICATE verdict 시 solution_similar_to 표시 안내가 없음"
        )

    def test_reject_shows_reason(self):
        content = read_skill()
        assert "solution_reject_reason" in content, (
            "REJECT verdict 시 solution_reject_reason 표시 안내가 없음"
        )


# --- 재진입 방지 ---

class TestReentryPrevention:
    """K 게이트 재진입 방지 조건이 있어야 한다."""

    def test_reentry_prevention_mentioned(self):
        content = read_skill()
        assert re.search(r"재진입 방지|재진입|reentry", content, re.IGNORECASE), (
            "재진입 방지 언급이 없음"
        )

    def test_devflow_audit_check_for_reentry(self):
        content = read_skill()
        assert re.search(r"devflow-audit", content), (
            "재진입 방지를 위한 devflow-audit 확인 언급이 없음"
        )


# --- Audit prefix 규약 (taxonomy §2.5) ---

class TestAuditPrefix:
    """verdict별 audit prefix를 명시해야 한다 (solution-store/duplicate/reject)."""

    def test_solution_store_prefix(self):
        content = read_skill()
        assert "solution-store" in content, (
            "audit prefix solution-store 명시가 없음 (taxonomy §2.5)"
        )

    def test_solution_duplicate_prefix(self):
        content = read_skill()
        assert "solution-duplicate" in content, (
            "audit prefix solution-duplicate 명시가 없음"
        )

    def test_solution_reject_prefix(self):
        content = read_skill()
        assert "solution-reject" in content, (
            "audit prefix solution-reject 명시가 없음"
        )


# --- error_message 보존 ---

class TestErrorMessagePreservation:
    """build-and-test 실패 시 error_message를 systematic-debugging에 전달해야 한다."""

    def test_error_message_preservation_instruction(self):
        content = read_skill()
        assert re.search(r"error_message|에러 메시지|에러메시지", content, re.IGNORECASE), (
            "error_message 보존 지시가 없음"
        )


# --- Step 1.5 재검증 경로에 K 미적용 ---

class TestStep15NoKGate:
    """Step 1.5 재검증 Debugging에는 K 게이트를 적용하지 않는다."""

    def test_step_15_k_gate_exclusion_mentioned(self):
        content = read_skill()
        assert re.search(
            r"Step 1\.5.*K|1\.5.*K 게이트|K 게이트.*1\.5|K 게이트는.*본 Debugging",
            content, re.IGNORECASE | re.DOTALL
        ), (
            "Step 1.5 재검증 경로에는 K 게이트를 미적용한다는 명시가 없음"
        )


# --- FR-1: 구현 게이트 R→S 전환 (Distrust by Default) ---

class TestFR1ReviewAutoExecution:
    """FR-1: 구현 게이트에서 R 옵션 제거, S(스킵) 추가, 리뷰 자동 실행."""

    def test_r_option_removed(self):
        content = read_skill()
        assert not re.search(r"^R\)", content, re.MULTILINE), (
            "구현 게이트에서 R 옵션이 아직 존재함 — FR-1에 따라 제거되어야 함"
        )

    def test_review_skip_via_interrupt(self):
        content = read_skill()
        assert re.search(r"리뷰 스킵.*자유 발화|리뷰 스킵.*요청", content), (
            "구현 게이트에 리뷰 스킵(자유 발화) 안내가 없음"
        )

    def test_auto_review_execution(self):
        content = read_skill()
        assert re.search(r"자동 실행|자동 호출|auto.*review", content, re.IGNORECASE), (
            "코드 리뷰 자동 실행 명시가 없음"
        )

    def test_all_depth_auto_review(self):
        content = read_skill()
        assert re.search(r"모든 depth|R1.*단일 리뷰.*자동 호출.*모든|R1.*모드로 자동 호출", content), (
            "모든 depth에서 자동 리뷰 실행 명시가 없음"
        )
