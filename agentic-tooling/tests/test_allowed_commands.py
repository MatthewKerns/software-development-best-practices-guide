"""
Tests for commands that should be ALLOWED through the portable security-check.sh.

These are negative tests to ensure safe commands pass through under the default
configuration (no optional cloud/infra guardrails enabled).
"""

import pytest


class TestBasicFileOperations:
    """Basic file listing and viewing commands."""

    def test_ls(self, assert_allowed):
        assert_allowed("Bash", command="ls")

    def test_ls_la(self, assert_allowed):
        assert_allowed("Bash", command="ls -la")

    def test_ls_path(self, assert_allowed):
        assert_allowed("Bash", command="ls /app/src")

    def test_pwd(self, assert_allowed):
        assert_allowed("Bash", command="pwd")

    def test_tree(self, assert_allowed):
        assert_allowed("Bash", command="tree -L 2")

    def test_find_name(self, assert_allowed):
        assert_allowed("Bash", command="find . -name '*.py'")


class TestGitSafeOperations:
    """Git commands that don't modify remote or history."""

    def test_git_status(self, assert_allowed):
        assert_allowed("Bash", command="git status")

    def test_git_log(self, assert_allowed):
        assert_allowed("Bash", command="git log --oneline -10")

    def test_git_diff(self, assert_allowed):
        assert_allowed("Bash", command="git diff")

    def test_git_diff_staged(self, assert_allowed):
        assert_allowed("Bash", command="git diff --staged")

    def test_git_branch_list(self, assert_allowed):
        assert_allowed("Bash", command="git branch")

    def test_git_branch_verbose(self, assert_allowed):
        assert_allowed("Bash", command="git branch -v")

    def test_git_branch_delete_lowercase(self, assert_allowed):
        # -d (lowercase) only deletes fully merged branches; -D force-deletes.
        # The force-ask grep is case-sensitive so `-D\b` does NOT match `-d`.
        assert_allowed("Bash", command="git branch -d merged-branch")

    def test_git_show(self, assert_allowed):
        assert_allowed("Bash", command="git show HEAD")

    def test_git_stash_list(self, assert_allowed):
        assert_allowed("Bash", command="git stash list")

    def test_git_fetch(self, assert_allowed):
        assert_allowed("Bash", command="git fetch origin")

    def test_git_pull(self, assert_allowed):
        assert_allowed("Bash", command="git pull origin main")

    def test_git_checkout(self, assert_allowed):
        assert_allowed("Bash", command="git checkout feature-branch")

    def test_git_switch(self, assert_allowed):
        assert_allowed("Bash", command="git switch -c new-feature")

    def test_git_add(self, assert_allowed):
        assert_allowed("Bash", command="git add src/file.py")

    def test_git_commit(self, assert_allowed):
        assert_allowed("Bash", command="git commit -m 'Add feature'")

    def test_git_remote(self, assert_allowed):
        assert_allowed("Bash", command="git remote -v")


class TestGitHubCLISafeOperations:
    """GitHub CLI read-only operations."""

    def test_gh_pr_list(self, assert_allowed):
        assert_allowed("Bash", command="gh pr list")

    def test_gh_pr_view(self, assert_allowed):
        assert_allowed("Bash", command="gh pr view 123")

    def test_gh_issue_list(self, assert_allowed):
        assert_allowed("Bash", command="gh issue list")

    def test_gh_repo_view(self, assert_allowed):
        assert_allowed("Bash", command="gh repo view")

    def test_gh_run_list(self, assert_allowed):
        assert_allowed("Bash", command="gh run list")

    def test_gh_run_view(self, assert_allowed):
        assert_allowed("Bash", command="gh run view 12345")


class TestDockerSafeOperations:
    """Docker commands that don't push or login (push/login are optional rules)."""

    def test_docker_ps(self, assert_allowed):
        assert_allowed("Bash", command="docker ps")

    def test_docker_images(self, assert_allowed):
        assert_allowed("Bash", command="docker images")

    def test_docker_build(self, assert_allowed):
        assert_allowed("Bash", command="docker build -t myimage .")

    def test_docker_run(self, assert_allowed):
        assert_allowed("Bash", command="docker run -it myimage")

    def test_docker_logs(self, assert_allowed):
        assert_allowed("Bash", command="docker logs container_name")

    def test_docker_exec(self, assert_allowed):
        assert_allowed("Bash", command="docker exec -it container bash")

    def test_docker_compose_up(self, assert_allowed):
        assert_allowed("Bash", command="docker-compose up -d")

    def test_docker_compose_down(self, assert_allowed):
        assert_allowed("Bash", command="docker-compose down")


class TestPackageManagement:
    """Package manager install commands (publish is an optional rule)."""

    def test_npm_install(self, assert_allowed):
        assert_allowed("Bash", command="npm install")

    def test_npm_install_package(self, assert_allowed):
        assert_allowed("Bash", command="npm install lodash")

    def test_npm_run(self, assert_allowed):
        assert_allowed("Bash", command="npm run build")

    def test_npm_ci(self, assert_allowed):
        assert_allowed("Bash", command="npm ci")

    def test_pip_install(self, assert_allowed):
        assert_allowed("Bash", command="pip install requests")

    def test_pip_install_requirements(self, assert_allowed):
        assert_allowed("Bash", command="pip install -r requirements.txt")

    def test_pip_list(self, assert_allowed):
        assert_allowed("Bash", command="pip list")


class TestTestingCommands:
    """Test runner commands."""

    def test_pytest(self, assert_allowed):
        assert_allowed("Bash", command="pytest")

    def test_pytest_verbose(self, assert_allowed):
        assert_allowed("Bash", command="pytest -v tests/")

    def test_npm_test(self, assert_allowed):
        assert_allowed("Bash", command="npm test")

    def test_jest(self, assert_allowed):
        assert_allowed("Bash", command="npx jest")


class TestLintingFormatting:
    """Linting and formatting commands."""

    def test_npm_lint(self, assert_allowed):
        assert_allowed("Bash", command="npm run lint")

    def test_eslint(self, assert_allowed):
        assert_allowed("Bash", command="npx eslint src/")

    def test_prettier(self, assert_allowed):
        assert_allowed("Bash", command="npx prettier --write src/")

    def test_black(self, assert_allowed):
        assert_allowed("Bash", command="black backend/")

    def test_ruff(self, assert_allowed):
        assert_allowed("Bash", command="ruff check backend/")


class TestCloudReadOnlySafe:
    """Cloud CLI read-only ops are safe even when no optional rules are enabled."""

    def test_aws_s3_ls(self, assert_allowed):
        assert_allowed("Bash", command="aws s3 ls")

    def test_aws_sts_get_caller_identity(self, assert_allowed):
        assert_allowed("Bash", command="aws sts get-caller-identity")

    def test_cdk_list(self, assert_allowed):
        assert_allowed("Bash", command="cdk list")

    def test_cdk_diff(self, assert_allowed):
        assert_allowed("Bash", command="cdk diff")

    def test_terraform_plan(self, assert_allowed):
        assert_allowed("Bash", command="terraform plan")

    def test_alembic_history(self, assert_allowed):
        assert_allowed("Bash", command="alembic history")

    def test_alembic_current(self, assert_allowed):
        assert_allowed("Bash", command="alembic current")


class TestCloudDestructiveAllowedByDefault:
    """With the OPTIONAL cloud rules disabled, these pass through.

    Enable the relevant lines in the OPTIONAL block of security-check.sh to gate
    them (then see test_optional_cloud_rules.py). These tests document the
    default-off behavior.
    """

    def test_cdk_destroy_allowed_by_default(self, assert_allowed):
        assert_allowed("Bash", command="cdk destroy MyStack")

    def test_terraform_destroy_allowed_by_default(self, assert_allowed):
        assert_allowed("Bash", command="terraform destroy")

    def test_aws_ec2_terminate_allowed_by_default(self, assert_allowed):
        assert_allowed("Bash", command="aws ec2 terminate-instances --instance-ids i-12345")

    def test_npm_publish_allowed_by_default(self, assert_allowed):
        assert_allowed("Bash", command="npm publish")

    def test_docker_push_allowed_by_default(self, assert_allowed):
        assert_allowed("Bash", command="docker push myimage:latest")


class TestMiscSafeCommands:
    """Other safe commands."""

    def test_echo(self, assert_allowed):
        assert_allowed("Bash", command="echo 'hello world'")

    def test_date(self, assert_allowed):
        assert_allowed("Bash", command="date")

    def test_env(self, assert_allowed):
        assert_allowed("Bash", command="env")

    def test_which(self, assert_allowed):
        assert_allowed("Bash", command="which python")

    def test_whoami(self, assert_allowed):
        assert_allowed("Bash", command="whoami")

    def test_cat_safe_file(self, assert_allowed):
        assert_allowed("Bash", command="cat README.md")

    def test_grep(self, assert_allowed):
        assert_allowed("Bash", command="grep -r 'TODO' src/")


class TestRepoAwareRmAllowed:
    """rm commands within the repo should be allowed (git-protected)."""

    def test_rm_single_file_in_repo(self, assert_allowed):
        assert_allowed("Bash", command="rm backend/temp_file.py")

    def test_rm_rf_folder_in_repo_relative(self, assert_allowed):
        assert_allowed("Bash", command="rm -rf .claude/skills/old-skill/")

    def test_rm_rf_folder_in_repo_dot_prefix(self, assert_allowed):
        assert_allowed("Bash", command="rm -rf ./temp_folder/")

    def test_rm_r_folder_without_force(self, assert_allowed):
        assert_allowed("Bash", command="rm -r docs/temp/")

    def test_rm_multiple_files_in_repo(self, assert_allowed):
        assert_allowed("Bash", command="rm file1.txt file2.txt file3.txt")

    def test_rm_with_glob_pattern(self, assert_allowed):
        assert_allowed("Bash", command="rm -f *.pyc")

    def test_rm_with_find_in_repo(self, assert_allowed):
        assert_allowed("Bash", command="find . -name '*.pyc' -delete")
