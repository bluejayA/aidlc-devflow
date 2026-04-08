"""session-start 훅 서브에이전트 게이트 검증 (BL-080)"""
import pathlib
import subprocess

HOOKS_DIR = pathlib.Path(__file__).resolve().parent.parent / "hooks"


class TestSessionStartSubagentGate:
    """session-start 훅이 서브에이전트 모드를 감지하고 온보딩을 스킵하는지 검증"""

    def setup_method(self):
        self.hook_path = HOOKS_DIR / "session-start"
        self.content = self.hook_path.read_text()

    def test_has_subagent_gate(self):
        """CLAUDE_AGENT_ID 환경 변수 감지 로직이 존재하는지"""
        assert "CLAUDE_AGENT_ID" in self.content

    def test_skips_onboarding_for_subagent(self):
        """서브에이전트 모드에서 온보딩 메시지가 출력되지 않는지"""
        result = subprocess.run(
            ["bash", str(self.hook_path)],
            env={"CLAUDE_AGENT_ID": "test-subagent", "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "AIDLC devflow" not in result.stdout

    def test_shows_onboarding_for_main_session(self):
        """메인 세션에서는 온보딩 메시지가 정상 출력되는지"""
        result = subprocess.run(
            ["bash", str(self.hook_path)],
            env={"PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "AIDLC devflow" in result.stdout
