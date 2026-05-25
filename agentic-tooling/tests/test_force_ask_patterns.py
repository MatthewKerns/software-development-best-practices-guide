"""
Tests for FORCE_ASK_PATTERNS in the portable security-check.sh.

These commands should trigger a permission prompt (exit code 0 + JSON output)
under the universal default rules.

NOTE: branch-aware push protection (CHECK 4) is OPT-IN via the PROTECTED_BRANCHES
config array, which is EMPTY by default. So in the default configuration:
  - git push to any branch (including main) is allowed silently
  - git push --force / --force-with-lease is force-asked regardless of branch
    (it matches the universal FORCE_ASK git-destructive patterns)
See test_optional_cloud_rules.py for the branch-protection behavior when enabled.
"""

import pytest


class TestGitDestructiveForceAsk:
    """Universal git-destructive force-asks (recoverable via reflog).

    These are in FORCE_ASK_PATTERNS by default — no project config needed.
    """

    def test_git_push_force_short(self, assert_force_ask):
        assert_force_ask("Bash", command="git push -f origin main")

    def test_git_push_force_long(self, assert_force_ask):
        assert_force_ask("Bash", command="git push --force origin feature")

    def test_git_push_force_with_lease(self, assert_force_ask):
        assert_force_ask("Bash", command="git push --force-with-lease origin main")

    def test_git_reset_hard(self, assert_force_ask):
        assert_force_ask("Bash", command="git reset --hard HEAD~1")

    def test_git_clean_force(self, assert_force_ask):
        assert_force_ask("Bash", command="git clean -fd")

    def test_git_branch_delete_force(self, assert_force_ask):
        assert_force_ask("Bash", command="git branch -D feature-branch")


class TestGitPushDefaultAllowed:
    """With PROTECTED_BRANCHES empty (default), non-force pushes pass silently."""

    def test_git_push_origin_main(self, assert_allowed):
        """Push to main is allowed by default (enable PROTECTED_BRANCHES to gate it)."""
        assert_allowed("Bash", command="git push origin main")

    def test_git_push_feature_branch(self, assert_allowed):
        assert_allowed("Bash", command="git push origin feature/my-feature")

    def test_git_push_upstream_feature(self, assert_allowed):
        assert_allowed("Bash", command="git push -u origin feature-branch")

    def test_git_push_bare(self, assert_allowed):
        assert_allowed("Bash", command="git push")


class TestGitMergeAllowed:
    """git merge is not gated by the portable hook — always allowed."""

    def test_git_merge(self, assert_allowed):
        assert_allowed("Bash", command="git merge feature-branch")

    def test_git_merge_no_ff(self, assert_allowed):
        assert_allowed("Bash", command="git merge --no-ff feature-branch")


class TestGitHubCLIAllowed:
    """gh pr/issue/release commands pass through silently by default."""

    def test_gh_pr_create(self, assert_allowed):
        assert_allowed("Bash", command="gh pr create --title 'My PR'")

    def test_gh_pr_merge(self, assert_allowed):
        assert_allowed("Bash", command="gh pr merge 123")

    def test_gh_issue_create(self, assert_allowed):
        assert_allowed("Bash", command="gh issue create --title 'Bug report'")

    def test_gh_release_create(self, assert_allowed):
        assert_allowed("Bash", command="gh release create v1.0.0")


class TestNetworkRequestsAllowed:
    """curl and wget pass through silently — routine for diagnostics."""

    def test_curl_simple(self, assert_allowed):
        assert_allowed("Bash", command="curl https://example.com")

    def test_curl_with_data(self, assert_allowed):
        assert_allowed("Bash", command="curl -X POST -d 'data' https://api.example.com")

    def test_wget_simple(self, assert_allowed):
        assert_allowed("Bash", command="wget https://example.com/file.zip")


class TestForceAskPriority:
    """git push --force is force-asked (recoverable via reflog when caught)."""

    def test_git_push_force_is_ask_not_block(self, assert_force_ask):
        assert_force_ask("Bash", command="git push -f origin main")

    def test_git_push_force_with_lease_is_ask(self, assert_force_ask):
        assert_force_ask("Bash", command="git push --force-with-lease origin main")
