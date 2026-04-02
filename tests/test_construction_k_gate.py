"""construction-orchestrator 게이트 변경 테스트.

FR-1 (Distrust by Default): 구현 게이트 R→S 전환 검증
FR-4 (Knowledge Compounding): Debugging 라우팅 K 게이트 검증

검증 항목:
1. 구현 게이트에서 R 옵션 제거, S 옵션 추가, 자동 리뷰 실행 명시
2. Debugging 라우팅에 K 선택지 존재
3. devflow-solutions 호출 언급
4. verdict별 안내 (SAVE / DUPLICATE / REJECT) 존재
5. 재진입 방지 언급
6. audit 기록 형식 (compound 타입)
7. error_message 보존 지시
8. Step 1.5 재검증 경로에는 K 게이트 미적용 명시
"""

import re
from pathlib import Path

import pytest

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


# --- K 선택지 존재 ---

class TestKGateOption:
    """Debugging 라우팅 내에 K 선택지가 정의되어야 한다."""

    def test_k_option_exists_in_debugging_routing(self):
        content = read_skill()
        # K) 또는 K gate 텍스트
        assert re.search(r"K\)", content), (
            "Debugging 라우팅에 K) 선택지가 없음"
        )

    def test_k_option_references_learning_record(self):
        content = read_skill()
        # 학습 기록 저장 언급
        assert re.search(r"학습 기록|Knowledge|knowledge", content), (
            "K 선택지에 학습 기록 저장 관련 언급이 없음"
        )

    def test_default_option_is_arrow(self):
        content = read_skill()
        # →) 기본 선택지가 존재해야 함
        assert re.search(r"→\)", content), (
            "Debugging 라우팅에 →) 기본(바로 재실행) 선택지가 없음"
        )


# --- devflow-solutions 호출 ---

class TestDevflowSolutionsCall:
    """K 선택 시 devflow-solutions STORE를 호출해야 한다."""

    def test_devflow_solutions_mentioned(self):
        content = read_skill()
        assert "devflow-solutions" in content, (
            "K 게이트에 devflow-solutions 호출 언급이 없음"
        )

    def test_store_call_mentioned(self):
        content = read_skill()
        assert re.search(r"STORE", content), (
            "devflow-solutions STORE 호출 언급이 없음"
        )


# --- verdict별 안내 ---

class TestVerdictGuidance:
    """SAVE / DUPLICATE / REJECT 각 verdict에 대한 안내가 있어야 한다."""

    def test_save_verdict_guidance(self):
        content = read_skill()
        assert re.search(r"SAVE", content), (
            "SAVE verdict 안내가 없음"
        )

    def test_duplicate_verdict_guidance(self):
        content = read_skill()
        assert re.search(r"DUPLICATE", content), (
            "DUPLICATE verdict 안내가 없음"
        )

    def test_reject_verdict_guidance(self):
        content = read_skill()
        assert re.search(r"REJECT", content), (
            "REJECT verdict 안내가 없음"
        )

    def test_save_shows_saved_path(self):
        content = read_skill()
        assert "saved_path" in content, (
            "SAVE verdict 시 saved_path 표시 안내가 없음"
        )

    def test_duplicate_shows_similar_to(self):
        content = read_skill()
        assert "similar_to" in content, (
            "DUPLICATE verdict 시 similar_to 표시 안내가 없음"
        )

    def test_reject_shows_reason(self):
        content = read_skill()
        # REJECT 시 reason 또는 이유 표시
        assert re.search(r"reason|이유|Privacy|privacy", content, re.IGNORECASE), (
            "REJECT verdict 시 reason/이유 표시 안내가 없음"
        )


# --- 재진입 방지 ---

class TestReentryPrevention:
    """K 게이트는 재진입 방지 조건이 있어야 한다."""

    def test_reentry_prevention_mentioned(self):
        content = read_skill()
        assert re.search(r"재진입 방지|재진입|reentry", content, re.IGNORECASE), (
            "K 게이트 재진입 방지 언급이 없음"
        )

    def test_devflow_audit_check_for_reentry(self):
        content = read_skill()
        # devflow-audit에서 로그 존재 여부 확인
        assert re.search(r"devflow-audit", content), (
            "재진입 방지를 위한 devflow-audit 확인 언급이 없음"
        )

    def test_compound_log_type_in_reentry_check(self):
        content = read_skill()
        assert re.search(r"compound", content), (
            "재진입 방지 조건에 compound 로그 타입 언급이 없음"
        )


# --- Audit 기록 형식 ---

class TestAuditLogging:
    """K 선택/스킵 모두 devflow-audit에 compound 타입으로 기록해야 한다."""

    def test_audit_type_compound(self):
        content = read_skill()
        assert re.search(r"type:\s*compound|compound", content), (
            "audit 기록에 type: compound가 없음"
        )

    def test_audit_action_save_or_skip(self):
        content = read_skill()
        # action: save 또는 action: skip
        assert re.search(r"action:.*save|action:.*skip|save.*skip", content, re.IGNORECASE), (
            "audit 기록에 action: save/skip 필드가 없음"
        )

    def test_audit_verdict_field(self):
        content = read_skill()
        assert re.search(r"verdict", content), (
            "audit 기록에 verdict 필드가 없음"
        )

    def test_audit_path_field(self):
        content = read_skill()
        assert re.search(r"path:", content), (
            "audit 기록에 path 필드가 없음"
        )


# --- error_message 보존 ---

class TestErrorMessagePreservation:
    """build-and-test 실패 시 error_message를 컨텍스트에 보존해야 한다."""

    def test_error_message_preservation_instruction(self):
        content = read_skill()
        assert re.search(r"error_message|에러 메시지|에러메시지", content, re.IGNORECASE), (
            "error_message 보존 지시가 없음"
        )

    def test_error_message_passed_to_devflow_solutions(self):
        content = read_skill()
        # devflow-solutions에 error_message 전달 언급
        assert re.search(r"error_message.*devflow-solutions|devflow-solutions.*error_message",
                         content, re.IGNORECASE | re.DOTALL), (
            "error_message를 devflow-solutions에 전달한다는 언급이 없음"
        )


# --- Step 1.5 재검증 경로에 K 미적용 ---

class TestStep15NoKGate:
    """Step 1.5 재검증 Debugging에는 K 게이트를 적용하지 않는다."""

    def test_step_15_k_gate_exclusion_mentioned(self):
        content = read_skill()
        # K 게이트를 Step 1.5에 적용하지 않는다는 명시
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
        # 구현 게이트 영역에서 R) 옵션이 없어야 함
        assert not re.search(r"^R\)", content, re.MULTILINE), (
            "구현 게이트에서 R 옵션이 아직 존재함 — FR-1에 따라 제거되어야 함"
        )

    def test_s_option_exists(self):
        content = read_skill()
        assert re.search(r"S\).*무시.*진행|S\).*스킵|S\).*skip", content, re.IGNORECASE), (
            "구현 게이트에 S(스킵/무시) 옵션이 없음"
        )

    def test_auto_review_execution(self):
        content = read_skill()
        assert re.search(r"자동 실행|자동 호출|auto.*review", content, re.IGNORECASE), (
            "코드 리뷰 자동 실행 명시가 없음"
        )

    def test_minimal_depth_no_review(self):
        content = read_skill()
        assert re.search(r"Minimal.*리뷰 없음|Minimal depth.*리뷰|Minimal.*S 옵션 없이", content), (
            "Minimal depth에서 리뷰 없음 예외 명시가 없음"
        )
