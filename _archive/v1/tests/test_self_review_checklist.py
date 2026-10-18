"""Self-Review Checklist 존재 및 항목 검증 (BL-079)"""
import pathlib

SKILLS_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills"


class TestBrainstormingSelfReview:
    """brainstorming SKILL.md에 Self-Review Checklist가 올바르게 삽입되었는지 검증"""

    def setup_method(self):
        self.content = (SKILLS_DIR / "aidlc-brainstorming" / "SKILL.md").read_text()

    def test_has_self_review_section(self):
        assert "Self-Review Checklist" in self.content

    def test_has_4_items(self):
        items = ["Placeholder scan", "Internal consistency", "Scope check", "Ambiguity check"]
        for item in items:
            assert item in self.content, f"Missing checklist item: {item}"

    def test_positioned_before_spec_review(self):
        """셀프리뷰가 Spec Review Loop 이전에 위치해야 함"""
        self_review_pos = self.content.index("Self-Review Checklist")
        spec_review_pos = self.content.index("Spec Review Loop")
        assert self_review_pos < spec_review_pos, "Self-Review must come before Spec Review"


class TestWritingPlansSelfReview:
    """writing-plans SKILL.md에 Self-Review Checklist가 올바르게 삽입되었는지 검증"""

    def setup_method(self):
        self.content = (SKILLS_DIR / "aidlc-writing-plans" / "SKILL.md").read_text()

    def test_has_self_review_section(self):
        assert "Self-Review Checklist" in self.content

    def test_has_3_items(self):
        items = ["Spec coverage", "Placeholder scan", "Type consistency"]
        for item in items:
            assert item in self.content, f"Missing checklist item: {item}"

    def test_positioned_before_plan_review_loop(self):
        """셀프리뷰가 Plan Review Loop 이전에 위치해야 함"""
        self_review_pos = self.content.index("Self-Review Checklist")
        plan_review_pos = self.content.index("Plan Review Loop")
        assert self_review_pos < plan_review_pos, "Self-Review must come before Plan Review Loop"
