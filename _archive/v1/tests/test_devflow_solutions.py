"""devflow-solutions skill structural validation tests. (FR-2 + FR-3)

Validates that:
- skills/_utils/devflow-solutions/SKILL.md exists with correct frontmatter
- SKILL.md defines Solution-Writer and Knowledge-Librarian inline sub-agents
- YAML frontmatter schema is documented with all 6 required fields
- Privacy Scrubbing patterns are present
- Markdown body required sections are defined
- File naming convention is documented
- invoke_mode is orchestrator-only
- Output language is Korean
"""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent / "skills"
SKILL_PATH = SKILLS_DIR / "_utils" / "devflow-solutions" / "SKILL.md"


def read_skill() -> str:
    """Read devflow-solutions SKILL.md content."""
    return SKILL_PATH.read_text(encoding="utf-8")


# --- File existence ---


class TestSkillFileExists:
    """SKILL.md must exist at the expected path."""

    def test_skill_file_exists(self):
        assert SKILL_PATH.exists(), (
            f"SKILL.md not found at {SKILL_PATH}"
        )


# --- Frontmatter ---


class TestFrontmatter:
    """SKILL.md frontmatter must have required metadata fields."""

    def test_has_name_field(self):
        content = read_skill()
        assert re.search(r"^name:\s+devflow-solutions", content, re.MULTILINE), (
            "frontmatter must have 'name: devflow-solutions'"
        )

    def test_has_invoke_mode_orchestrator_only(self):
        content = read_skill()
        assert re.search(r"invoke_mode:\s+orchestrator-only", content, re.MULTILINE), (
            "frontmatter must have 'invoke_mode: orchestrator-only'"
        )

    def test_has_return_behavior(self):
        content = read_skill()
        assert re.search(r"return_behavior:\s+\S+", content, re.MULTILINE), (
            "frontmatter must have a return_behavior field"
        )

    def test_has_version(self):
        content = read_skill()
        assert re.search(r"version:\s+\d+\.\d+\.\d+", content, re.MULTILINE), (
            "frontmatter must have a semantic version"
        )


# --- Sub-agent definitions ---


class TestSubAgentDefinitions:
    """SKILL.md must define Solution-Writer and Knowledge-Librarian sub-agents."""

    def test_has_solution_writer(self):
        content = read_skill()
        assert "Solution-Writer" in content, (
            "SKILL.md must define Solution-Writer inline sub-agent"
        )

    def test_has_knowledge_librarian(self):
        content = read_skill()
        assert "Knowledge-Librarian" in content, (
            "SKILL.md must define Knowledge-Librarian inline sub-agent"
        )

    def test_solution_writer_has_no_tools(self):
        """Solution-Writer must not have tool access — privacy scrubbing only."""
        content = read_skill()
        # Find Solution-Writer section and verify it states no tools
        # Accept either explicit "Tools: 없음" / "Tools: none" or equivalent
        assert re.search(r"Solution-Writer.*?없음|Solution-Writer.*?no tools|Tools.*없음",
                         content, re.IGNORECASE | re.DOTALL), (
            "Solution-Writer must specify it has no tools (tool-less sub-agent)"
        )

    def test_knowledge_librarian_has_glob_read_write_tools(self):
        content = read_skill()
        # Knowledge-Librarian section must mention Glob, Read, Write tools
        assert "Glob" in content and "Read" in content and "Write" in content, (
            "Knowledge-Librarian must list Glob, Read, Write as its tools"
        )


# --- STORE interface inputs ---


class TestStoreInterface:
    """STORE interface must document all 5 required input fields."""

    REQUIRED_FIELDS = [
        "root_cause",
        "fix_summary",
        "regression_test",
        "test_result",
        "error_message",
    ]

    def test_has_store_interface(self):
        content = read_skill()
        assert re.search(r"STORE", content), (
            "SKILL.md must define a STORE() interface"
        )

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_store_has_required_field(self, field):
        content = read_skill()
        assert field in content, (
            f"STORE interface must document required field: {field}"
        )


# --- YAML frontmatter schema ---


class TestYamlSchema:
    """YAML frontmatter schema for solution files must define all 6 fields."""

    REQUIRED_SCHEMA_FIELDS = [
        "title",
        "error_signature",
        "category",
        "project_type",
        "stack",
        "created",
    ]

    @pytest.mark.parametrize("field", REQUIRED_SCHEMA_FIELDS)
    def test_yaml_schema_has_field(self, field):
        content = read_skill()
        assert field in content, (
            f"YAML frontmatter schema must document field: {field}"
        )

    def test_category_values_defined(self):
        content = read_skill()
        # Must document at least build, test, runtime, config, dependency
        for val in ["build", "test", "runtime", "config", "dependency"]:
            assert val in content, (
                f"category field must document value: {val}"
            )


# --- Markdown body sections ---


class TestMarkdownBodySections:
    """Solution Markdown body must define 4 required sections."""

    REQUIRED_SECTIONS = ["Problem", "Root Cause", "Solution", "Prevention"]

    @pytest.mark.parametrize("section", REQUIRED_SECTIONS)
    def test_required_section_documented(self, section):
        content = read_skill()
        assert section in content, (
            f"Markdown body must document required section: {section}"
        )


# --- Privacy Scrubbing ---


class TestPrivacyScrubbing:
    """Privacy scrubbing rules must be documented."""

    def test_has_user_home_scrubbing(self):
        content = read_skill()
        assert re.search(r"/Users/|/home/", content), (
            "Privacy scrubbing must cover /Users/ and /home/ paths"
        )

    def test_has_token_scrubbing(self):
        content = read_skill()
        assert re.search(r"token=|Bearer ", content), (
            "Privacy scrubbing must cover token= and Bearer patterns"
        )

    def test_has_redacted_placeholder(self):
        content = read_skill()
        assert "<REDACTED>" in content, (
            "Privacy scrubbing must use <REDACTED> as replacement placeholder"
        )

    def test_has_user_home_placeholder(self):
        content = read_skill()
        assert "<USER_HOME>" in content, (
            "Privacy scrubbing must use <USER_HOME> as path replacement"
        )

    def test_knowledge_librarian_rejects_on_privacy_fail(self):
        content = read_skill()
        assert "REJECT" in content, (
            "Knowledge-Librarian must support REJECT verdict for privacy violations"
        )


# --- Knowledge-Librarian verdict ---


class TestKnowledgeLibrarianVerdict:
    """Knowledge-Librarian must define SAVE, DUPLICATE, REJECT verdicts."""

    def test_has_save_verdict(self):
        content = read_skill()
        assert "SAVE" in content, "Knowledge-Librarian must define SAVE verdict"

    def test_has_duplicate_verdict(self):
        content = read_skill()
        assert "DUPLICATE" in content, "Knowledge-Librarian must define DUPLICATE verdict"

    def test_has_reject_verdict(self):
        content = read_skill()
        assert "REJECT" in content, "Knowledge-Librarian must define REJECT verdict"

    def test_has_similar_to_field(self):
        content = read_skill()
        assert "similar_to" in content, (
            "Return value must include similar_to for partial duplicate detection"
        )


class TestTagValidation:
    """Knowledge-Librarian Tag Validation must verify category, project_type, and stack."""

    def test_tag_validation_covers_project_type(self):
        content = read_skill()
        assert re.search(r"Tag Validation.*project_type", content, re.DOTALL), (
            "Knowledge-Librarian Tag Validation must verify project_type values"
        )

    def test_tag_validation_covers_stack(self):
        content = read_skill()
        assert re.search(r"Tag Validation.*stack", content, re.DOTALL), (
            "Knowledge-Librarian Tag Validation must verify stack values"
        )

    def test_project_type_allowed_values(self):
        content = read_skill()
        for val in ["plugin", "web", "api", "cli"]:
            assert val in content, (
                f"project_type allowed values must include: {val}"
            )

    def test_stack_allowed_values(self):
        content = read_skill()
        for val in ["python", "node", "go", "rust", "markdown"]:
            assert val in content, (
                f"stack allowed values must include: {val}"
            )


# --- File naming and storage ---


class TestFileNamingAndStorage:
    """Solution storage conventions must be documented."""

    def test_has_solutions_storage_path(self):
        content = read_skill()
        assert "devflow-docs/solutions" in content, (
            "SKILL.md must define storage path as devflow-docs/solutions/{category}/"
        )

    def test_has_slug_naming_convention(self):
        content = read_skill()
        assert re.search(r"slug|YYYY-MM-DD", content), (
            "SKILL.md must document {YYYY-MM-DD}-{slug} naming convention"
        )


# --- Return value ---


class TestReturnValue:
    """STORE() must document return fields."""

    RETURN_FIELDS = ["saved_path", "verdict", "reason", "similar_to"]

    @pytest.mark.parametrize("field", RETURN_FIELDS)
    def test_return_field_documented(self, field):
        content = read_skill()
        assert field in content, (
            f"Return value must document field: {field}"
        )


# --- Output language ---


class TestOutputLanguage:
    """SKILL.md must specify Korean as output language."""

    def test_output_language_korean(self):
        content = read_skill()
        assert re.search(r"한국어|Korean", content, re.IGNORECASE), (
            "SKILL.md must specify Korean as output language (NFR-4)"
        )


class TestNFR3LineLimit:
    """SKILL.md must not exceed 200-line Progressive Disclosure limit."""

    def test_skill_line_count_under_200(self):
        content = read_skill()
        line_count = len(content.splitlines())
        assert line_count <= 200, (
            f"SKILL.md is {line_count} lines, exceeds 200-line NFR-3 limit"
        )
