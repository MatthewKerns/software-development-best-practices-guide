"""
Tests for edge cases in the portable security-check.sh pattern matching.

Tests case sensitivity, whitespace handling, boundary conditions, and priority
ordering against the universal default rules.
"""

import pytest


class TestCaseSensitivity:
    """Verify case handling in pattern matching.

    Most patterns are case-sensitive (Unix commands and git flags are
    case-sensitive). SQL keywords use case-insensitive matching.
    """

    def test_git_rebase_lowercase(self, assert_blocked):
        assert_blocked("Bash", command="git rebase main")

    def test_git_rebase_uppercase_allowed(self, assert_allowed):
        # Uppercase GIT won't work on Unix anyway — case-sensitive matching.
        assert_allowed("Bash", command="GIT REBASE main")

    def test_drop_database_lowercase(self, assert_blocked):
        assert_blocked("Bash", command="drop database mydb")

    def test_drop_database_mixed(self, assert_blocked):
        assert_blocked("Bash", command="Drop Database mydb")

    def test_drop_database_uppercase(self, assert_blocked):
        assert_blocked("Bash", command="DROP DATABASE mydb")

    def test_sudo_lowercase(self, assert_blocked):
        assert_blocked("Bash", command="sudo rm file")

    def test_curl_lowercase(self, assert_allowed):
        # curl is not force-asked under the portable hook.
        assert_allowed("Bash", command="curl https://example.com")


class TestWhitespaceHandling:
    """Test commands with various whitespace patterns."""

    def test_git_rebase_extra_spaces(self, assert_blocked):
        assert_blocked("Bash", command="git  rebase  main")

    def test_git_rebase_tab(self, assert_blocked):
        assert_blocked("Bash", command="git\trebase main")

    def test_leading_whitespace(self, assert_blocked):
        assert_blocked("Bash", command="  git rebase main")

    def test_trailing_whitespace(self, assert_blocked):
        assert_blocked("Bash", command="git rebase main  ")

    def test_curl_multiple_spaces(self, assert_allowed):
        assert_allowed("Bash", command="curl   https://example.com")


class TestPatternPriority:
    """Verify pattern priority for overlapping patterns."""

    def test_git_push_force_force_asked(self, assert_force_ask):
        # git push -f is in FORCE_ASK_PATTERNS (not hard-blocked).
        assert_force_ask("Bash", command="git push -f")

    def test_hard_block_wins_over_force_ask(self, assert_blocked):
        # `git rebase` (hard block) is checked before force-ask patterns.
        assert_blocked("Bash", command="git push -f origin main && git rebase main")


class TestBoundaryConditions:
    """Test pattern boundaries to avoid over-matching."""

    def test_git_without_rebase(self, assert_allowed):
        assert_allowed("Bash", command="git status")

    def test_rebase_without_git(self, assert_allowed):
        assert_allowed("Bash", command="echo rebase")

    def test_push_without_git(self, assert_allowed):
        assert_allowed("Bash", command="echo push")

    def test_force_without_push(self, assert_allowed):
        # --force alone shouldn't trigger git push --force.
        assert_allowed("Bash", command="npm install --force")

    def test_destroy_without_cdk(self, assert_allowed):
        # destroy alone shouldn't match anything.
        assert_allowed("Bash", command="echo destroy")

    def test_sudo_as_substring(self, assert_allowed):
        # "pseudo" contains "sudo" but shouldn't match.
        assert_allowed("Bash", command="echo pseudo")


class TestWordBoundaries:
    """Test word boundary handling in patterns."""

    def test_branch_d_lowercase_allowed(self, assert_allowed):
        # -d (lowercase) is the safe merged-only delete; force-ask matches -D only.
        assert_allowed("Bash", command="git branch -d merged")

    def test_clean_without_force(self, assert_allowed):
        assert_allowed("Bash", command="git clean -n")

    def test_reset_without_hard(self, assert_allowed):
        assert_allowed("Bash", command="git reset HEAD~1")

    def test_reset_soft(self, assert_allowed):
        assert_allowed("Bash", command="git reset --soft HEAD~1")


class TestEmptyAndMalformed:
    """Test handling of empty or unusual inputs."""

    def test_empty_command(self, assert_allowed):
        assert_allowed("Bash", command="")

    def test_whitespace_only(self, assert_allowed):
        assert_allowed("Bash", command="   ")

    def test_unknown_tool(self, assert_allowed):
        assert_allowed("Unknown", command="anything")

    def test_read_empty_path(self, assert_allowed):
        assert_allowed("Read", file_path="")


class TestSpecialCharacters:
    """Test handling of special characters in commands."""

    def test_quoted_command_blocked(self, assert_blocked):
        # Quote bypass is FIXED — commands are normalized before matching.
        # 'git' 'rebase' main -> git rebase main (after stripping quotes)
        assert_blocked("Bash", command="'git' 'rebase' main")

    def test_double_quoted_blocked(self, assert_blocked):
        assert_blocked("Bash", command='"git" "rebase" main')

    def test_env_file_with_quotes_blocked(self, assert_blocked):
        # File paths are normalized — quotes stripped.
        # "/app/.env" -> /app/.env (matches .env$ pattern)
        assert_blocked("Read", file_path='"/app/.env"')


class TestMultiplePatternMatches:
    """Test commands that could match multiple patterns."""

    def test_chained_destructive_commands(self, assert_blocked):
        # sudo is blocked even when chained.
        assert_blocked("Bash", command="git status && sudo rm -rf /")

    def test_curl_with_chaining(self, assert_allowed):
        # curl is not force-asked; chaining with && doesn't change that.
        assert_allowed("Bash", command="curl https://example.com && echo done")

    def test_git_push_with_pipe(self, assert_allowed):
        # Pipe-to-interpreter checks are disabled, so this is allowed.
        assert_allowed("Bash", command="echo 'git push' | bash")


class TestSensitiveFilePaths:
    """Test various sensitive file path formats."""

    def test_env_absolute_path(self, assert_blocked):
        assert_blocked("Read", file_path="/absolute/path/.env")

    def test_env_relative_path(self, assert_blocked):
        assert_blocked("Read", file_path="./relative/.env")

    def test_env_home_relative(self, assert_blocked):
        assert_blocked("Read", file_path="~/.env")

    def test_aws_absolute(self, assert_blocked):
        assert_blocked("Read", file_path="/Users/user/.aws/credentials")

    def test_ssh_various_keys(self, assert_blocked):
        assert_blocked("Read", file_path="/root/.ssh/id_ed25519")

    def test_credentials_anywhere_in_path(self, assert_blocked):
        assert_blocked("Read", file_path="/some/path/credentials/file.json")


class TestToolNameVariations:
    """Test different tool names are handled correctly."""

    def test_read_tool(self, assert_blocked):
        assert_blocked("Read", file_path="/app/.env")

    def test_write_tool(self, assert_blocked):
        assert_blocked("Write", file_path="/app/.env")

    def test_edit_tool(self, assert_blocked):
        assert_blocked("Edit", file_path="/app/.env")

    def test_bash_ignores_file_path(self, assert_allowed):
        # Bash tool should ignore file_path, only check command.
        assert_allowed("Bash", command="ls", file_path="/app/.env")

    def test_non_file_tool_ignores_patterns(self, assert_allowed):
        # Tools that aren't Read/Write/Edit/Bash should pass through.
        assert_allowed("Glob", file_path="/app/.env")
