"""
Fixtures for the portable security-check.sh hook tests.

These tests verify the behavior of the genericized security hook by invoking it
directly with mocked JSON input and checking exit codes and output.

The hook under test lives at agentic-tooling/hooks/security-check.sh (resolved
relative to this file, so the suite is location-independent).

PERFORMANCE NOTE:
Each invocation of security-check.sh spawns jq + multiple grep processes
internally, so the full suite takes a few seconds. Options to speed up:
1. Run tests in parallel: pytest -n auto (requires pytest-xdist)
2. Run a subset during dev: pytest -k "hard_block" --tb=short

HOOK MODE:
There is one active security hook (HOOK_MODE="active"). The `hook_mode` fixture
remains for diagnostic purposes.
"""

import json
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest


# Path to the security hook relative to this test file:
#   agentic-tooling/tests/conftest.py -> agentic-tooling/hooks/security-check.sh
SECURITY_HOOK = Path(__file__).parent.parent / "hooks" / "security-check.sh"


def _detect_hook_mode() -> str:
    """Detect which hook variant is active by reading HOOK_MODE from the script."""
    try:
        content = SECURITY_HOOK.read_text()
        for line in content.splitlines():
            if line.startswith("HOOK_MODE="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "unknown"


ACTIVE_HOOK_MODE = _detect_hook_mode()


class HookResult(NamedTuple):
    """Result from running the security hook."""
    returncode: int
    stdout: str
    stderr: str


@pytest.fixture
def run_security_hook():
    """
    Invoke security-check.sh with mocked JSON input.

    Returns a callable that takes tool_name and optional command/file_path,
    and returns (exit_code, stdout, stderr).

    Usage:
        result = run_security_hook("Bash", command="git push")
        assert result.returncode == 0  # allowed (or force ask with JSON)

        result = run_security_hook("Bash", command="git rebase main")
        assert result.returncode == 2  # hard blocked
    """
    def _run(
        tool_name: str,
        command: str = "",
        file_path: str = ""
    ) -> HookResult:
        input_json = json.dumps({
            "tool_name": tool_name,
            "tool_input": {
                "command": command,
                "file_path": file_path
            }
        })

        result = subprocess.run(
            ["bash", str(SECURITY_HOOK)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=5
        )

        return HookResult(
            returncode=result.returncode,
            stdout=result.stdout.rstrip('\n'),
            stderr=result.stderr.rstrip('\n')
        )

    return _run


@pytest.fixture
def assert_blocked(run_security_hook):
    """
    Assert that a command is hard blocked (exit code 2).

    Usage:
        assert_blocked("Bash", command="git rebase main")
    """
    def _assert(tool_name: str, command: str = "", file_path: str = ""):
        result = run_security_hook(tool_name, command=command, file_path=file_path)
        assert result.returncode == 2, (
            f"Expected exit code 2 (blocked) but got {result.returncode}\n"
            f"Command: {command or file_path}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "BLOCKED" in result.stderr, (
            f"Expected 'BLOCKED' in stderr but got: {result.stderr}"
        )
        return result

    return _assert


@pytest.fixture
def assert_allowed(run_security_hook):
    """
    Assert that a command is allowed (exit code 0, no JSON output).

    Usage:
        assert_allowed("Bash", command="ls -la")
    """
    def _assert(tool_name: str, command: str = "", file_path: str = ""):
        result = run_security_hook(tool_name, command=command, file_path=file_path)
        assert result.returncode == 0, (
            f"Expected exit code 0 (allowed) but got {result.returncode}\n"
            f"Command: {command or file_path}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        # No JSON output means truly allowed (not force ask)
        assert not result.stdout.strip() or "permissionDecision" not in result.stdout, (
            f"Expected no permission JSON but got: {result.stdout}"
        )
        return result

    return _assert


@pytest.fixture
def assert_force_ask(run_security_hook):
    """
    Assert that a command triggers force ask (exit code 0 with JSON output).

    Usage:
        assert_force_ask("Bash", command="git push --force origin main")
    """
    def _assert(tool_name: str, command: str = "", file_path: str = ""):
        result = run_security_hook(tool_name, command=command, file_path=file_path)
        assert result.returncode == 0, (
            f"Expected exit code 0 (force ask) but got {result.returncode}\n"
            f"Command: {command or file_path}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        # Check for force ask JSON output.
        # Note: the JSON may contain raw regex patterns with backslashes which
        # aren't valid JSON escapes, so we check for key strings instead.
        stdout = result.stdout.strip()
        assert stdout, "Expected JSON output but got empty stdout"
        assert "hookSpecificOutput" in stdout, (
            f"Expected hookSpecificOutput in output but got: {stdout}"
        )
        assert '"permissionDecision":"ask"' in stdout or '"permissionDecision": "ask"' in stdout, (
            f"Expected permissionDecision='ask' but got: {stdout}"
        )

        return result

    return _assert


@pytest.fixture
def hook_path():
    """Return the path to the security hook script."""
    return SECURITY_HOOK


@pytest.fixture
def hook_mode():
    """Return the active hook mode."""
    return ACTIVE_HOOK_MODE
