"""
Tests for HARD_BLOCK_PATTERNS in the portable security-check.sh.

These commands should ALWAYS be blocked (exit code 2) by the universal
default rules — no project configuration required.
"""

import pytest


class TestGitDestructiveOperations:
    """Git destructive operations.

    Only `git rebase` remains hard-blocked. push --force, reset --hard,
    clean -f, branch -D all moved to force-ask (recoverable via reflog).
    """

    def test_git_rebase_main(self, assert_blocked):
        assert_blocked("Bash", command="git rebase main")

    def test_git_rebase_interactive(self, assert_blocked):
        assert_blocked("Bash", command="git rebase -i HEAD~3")

    def test_git_rebase_onto(self, assert_blocked):
        assert_blocked("Bash", command="git rebase --onto main feature")

    def test_git_push_force(self, assert_force_ask):
        assert_force_ask("Bash", command="git push -f origin main")

    def test_git_push_force_long(self, assert_force_ask):
        assert_force_ask("Bash", command="git push --force origin main")

    def test_git_push_force_with_lease(self, assert_force_ask):
        assert_force_ask("Bash", command="git push --force-with-lease origin main")

    def test_git_reset_hard(self, assert_force_ask):
        assert_force_ask("Bash", command="git reset --hard HEAD~1")

    def test_git_reset_hard_origin(self, assert_force_ask):
        assert_force_ask("Bash", command="git reset --hard origin/main")

    def test_git_clean_force(self, assert_force_ask):
        assert_force_ask("Bash", command="git clean -f")

    def test_git_clean_force_directories(self, assert_force_ask):
        assert_force_ask("Bash", command="git clean -fd")

    def test_git_clean_force_ignored(self, assert_force_ask):
        assert_force_ask("Bash", command="git clean -fxd")

    def test_git_branch_delete_force(self, assert_force_ask):
        assert_force_ask("Bash", command="git branch -D feature-branch")


class TestSystemDestructiveOperations:
    """System-level commands that can cause irreversible local-machine damage."""

    def test_rm_rf_root(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /")

    def test_rm_rf_root_trailing_space(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf / --no-preserve-root")

    def test_rm_rf_home(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf ~")

    def test_rm_rf_home_expanded(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf ~/")

    def test_rm_rf_usr(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /usr")

    def test_rm_rf_etc(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /etc")

    def test_rm_rf_var(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /var")

    def test_rm_rf_home_dir(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /home")

    def test_rm_rf_users_macos(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /Users")

    def test_rm_rf_system_macos(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /System")

    def test_rm_rf_applications_macos(self, assert_blocked):
        assert_blocked("Bash", command="rm -rf /Applications")

    def test_sudo_any_command(self, assert_blocked):
        assert_blocked("Bash", command="sudo apt-get install package")

    def test_sudo_rm(self, assert_blocked):
        # sudo rm -rf is caught by the sudo hard-block.
        assert_blocked("Bash", command="sudo rm -rf /var/log")

    def test_su_switch_user(self, assert_blocked):
        assert_blocked("Bash", command="su - root")

    def test_mkfs_format(self, assert_blocked):
        # Pattern catches both mkfs.ext4 and mkfs -t ext4.
        assert_blocked("Bash", command="mkfs.ext4 /dev/sda1")

    def test_mkfs_with_flags(self, assert_blocked):
        assert_blocked("Bash", command="mkfs -t ext4 /dev/sda1")

    def test_dd_write_device(self, assert_blocked):
        assert_blocked("Bash", command="dd if=/dev/zero of=/dev/sda bs=1M")

    def test_redirect_to_raw_disk(self, assert_blocked):
        # > /dev/sda — overwrite a raw block device.
        assert_blocked("Bash", command="cat image.iso > /dev/sda")


class TestRepoAwareRmBlocking:
    """rm commands outside the repo are blocked.

    Exception: /tmp, /private/tmp, and /var/folders are allowed (Claude's
    scratch space). Other outside-repo paths are still blocked.
    """

    def test_rm_outside_repo_absolute_path(self, assert_allowed):
        # /tmp/* is allowed (scratch space).
        assert_allowed("Bash", command="rm -rf /tmp/outside_repo_folder/")

    def test_rm_outside_repo_other_project(self, assert_blocked):
        # Trying to delete another project should still be blocked.
        assert_blocked("Bash", command="rm -rf /Users/someone/other-project/")

    def test_rm_parent_directory_escape(self, assert_blocked):
        # Attempting to escape repo via .. should be blocked.
        assert_blocked("Bash", command="rm -rf ../../other-repo/")


class TestDatabaseDestruction:
    """Datastore destruction commands (case-insensitive hard blocks).

    `DROP DATABASE` SQL, redis FLUSHALL, and redis FLUSHDB remain hard-blocked.
    (DB migration / dropdb tooling lives in the OPTIONAL cloud rules.)
    """

    def test_drop_database_sql(self, assert_blocked):
        assert_blocked("Bash", command="psql -c 'DROP DATABASE mydb'")

    def test_drop_database_uppercase(self, assert_blocked):
        # Case-insensitive matching.
        assert_blocked("Bash", command="DROP DATABASE production")

    def test_redis_flushall(self, assert_blocked):
        assert_blocked("Bash", command="redis-cli FLUSHALL")

    def test_redis_flushdb(self, assert_blocked):
        assert_blocked("Bash", command="redis-cli FLUSHDB")


class TestHardBlocksNotTriggeredBySubstrings:
    """Ensure patterns don't match unintended substrings."""

    def test_git_rebase_in_message(self, assert_allowed):
        # The word "rebase" in a log grep should not trigger the block.
        assert_allowed("Bash", command="git log --grep='rebase'")

    def test_delete_in_filename(self, assert_allowed):
        # A file named "delete_user.py" should not trigger any block.
        assert_allowed("Bash", command="cat delete_user.py")

    def test_force_as_variable(self, assert_allowed):
        # Variable named 'force' should not trigger -f/--force block.
        assert_allowed("Bash", command="echo $force")
