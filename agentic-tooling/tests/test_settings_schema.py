"""
Tests for the example settings.json wiring and hook file health.

Validates the structure of hooks/settings.example.json (the wiring template a
project copies into .claude/settings.json) and that the hook scripts exist and
are executable.
"""

import json
import os
from pathlib import Path

import pytest


HOOKS_DIR = Path(__file__).parent.parent / "hooks"
SETTINGS_PATH = HOOKS_DIR / "settings.example.json"
SECURITY_HOOK_PATH = HOOKS_DIR / "security-check.sh"
STATUSLINE_HOOK_PATH = HOOKS_DIR / "statusline.sh"
CHECK_PROFILE_HOOK_PATH = HOOKS_DIR / "check-profile.sh"


class TestHookFilesExist:
    """Verify hook files exist and are executable."""

    def test_settings_example_exists(self):
        assert SETTINGS_PATH.exists(), f"settings.example.json not found at {SETTINGS_PATH}"

    def test_security_hook_exists(self):
        assert SECURITY_HOOK_PATH.exists(), f"security-check.sh not found at {SECURITY_HOOK_PATH}"

    def test_statusline_hook_exists(self):
        assert STATUSLINE_HOOK_PATH.exists(), f"statusline.sh not found at {STATUSLINE_HOOK_PATH}"

    def test_check_profile_hook_exists(self):
        assert CHECK_PROFILE_HOOK_PATH.exists(), f"check-profile.sh not found at {CHECK_PROFILE_HOOK_PATH}"

    @pytest.mark.parametrize("hook", [
        SECURITY_HOOK_PATH, STATUSLINE_HOOK_PATH, CHECK_PROFILE_HOOK_PATH,
    ])
    def test_hook_executable(self, hook):
        """
        CRITICAL: hooks must be executable.

        Claude Code invokes hooks directly, so the executable bit is REQUIRED.
        Without it the hook silently fails and provides no protection.
        Fix: chmod +x <hook>
        """
        assert os.access(hook, os.X_OK), (
            f"CRITICAL: {hook.name} is NOT executable!\n"
            f"Fix: chmod +x {hook}"
        )


class TestSettingsSchema:
    """Validate settings.example.json schema structure."""

    @pytest.fixture
    def settings(self):
        with open(SETTINGS_PATH) as f:
            return json.load(f)

    def test_has_hooks_section(self, settings):
        assert "hooks" in settings, "settings must have a 'hooks' section"

    def test_hooks_has_pre_tool_use(self, settings):
        assert "PreToolUse" in settings["hooks"], (
            "hooks must have a 'PreToolUse' section for security enforcement"
        )

    def test_pre_tool_use_is_list(self, settings):
        assert isinstance(settings["hooks"]["PreToolUse"], list), (
            "PreToolUse must be a list of hook configurations"
        )

    def test_security_hook_configured(self, settings):
        found = False
        for hook_config in settings["hooks"]["PreToolUse"]:
            for hook in hook_config.get("hooks", []):
                if "security-check.sh" in hook.get("command", ""):
                    found = True
        assert found, "security-check.sh must be configured in PreToolUse hooks"

    def test_security_hook_matches_bash_read_write_edit(self, settings):
        for hook_config in settings["hooks"]["PreToolUse"]:
            for hook in hook_config.get("hooks", []):
                if "security-check.sh" in hook.get("command", ""):
                    matcher = hook_config.get("matcher", "")
                    assert "Bash" in matcher, "Security hook must match Bash"
                    assert "Read" in matcher, "Security hook must match Read"
                    assert "Write" in matcher, "Security hook must match Write"
                    assert "Edit" in matcher, "Security hook must match Edit"

    def test_statusline_configured(self, settings):
        assert "statusLine" in settings, "settings should wire the statusLine hook"
        assert "statusline.sh" in settings["statusLine"].get("command", "")

    def test_check_profile_session_start(self, settings):
        found = False
        for hook_config in settings["hooks"].get("SessionStart", []):
            for hook in hook_config.get("hooks", []):
                if "check-profile.sh" in hook.get("command", ""):
                    found = True
        assert found, "check-profile.sh should be wired as a SessionStart hook"


class TestHookConfiguration:
    """Validate hook configuration details."""

    @pytest.fixture
    def settings(self):
        with open(SETTINGS_PATH) as f:
            return json.load(f)

    def test_security_hook_has_timeout(self, settings):
        for hook_config in settings["hooks"]["PreToolUse"]:
            for hook in hook_config.get("hooks", []):
                if "security-check.sh" in hook.get("command", ""):
                    assert "timeout" in hook, "Security hook should have a timeout"
                    assert hook["timeout"] <= 30, "Timeout should be reasonable (<=30s)"

    def test_security_hook_type_is_command(self, settings):
        for hook_config in settings["hooks"]["PreToolUse"]:
            for hook in hook_config.get("hooks", []):
                if "security-check.sh" in hook.get("command", ""):
                    assert hook.get("type") == "command", "Security hook type must be 'command'"


class TestSecurityHookContent:
    """Validate the security hook contains its universal guardrails."""

    @pytest.fixture
    def content(self):
        return SECURITY_HOOK_PATH.read_text()

    def test_universal_hard_blocks_present(self, content):
        for needle in ["git\\s+rebase", "sudo\\s+", "mkfs", "of=/dev/", "DROP\\s+DATABASE"]:
            assert needle in content, f"security-check.sh should hard-block {needle!r}"

    def test_optional_block_present_and_commented(self, content):
        assert "OPTIONAL: cloud / infra guardrails" in content, (
            "security-check.sh should document the OPTIONAL guardrails block"
        )
        # Optional cloud rules must be commented out by default.
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("FORCE_ASK_PATTERNS+=("):
                pytest.fail(
                    f"OPTIONAL cloud rule appears enabled by default: {stripped}"
                )

    def test_protected_branches_disabled_by_default(self, content):
        assert "PROTECTED_BRANCHES=()" in content, (
            "PROTECTED_BRANCHES should be empty (disabled) by default"
        )

    def test_branch_protection_logic_present(self, content):
        assert "protected branch" in content.lower(), (
            "security-check.sh should retain the protected-branch logic"
        )
