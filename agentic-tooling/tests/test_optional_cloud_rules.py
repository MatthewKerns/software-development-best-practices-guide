"""
Tests for the OPTIONAL cloud / infra guardrails in security-check.sh.

These rules are COMMENTED OUT by default to keep the hook portable. This module
verifies they behave correctly WHEN ENABLED. To do that without mutating the
real hook, each test runs against a temporary copy of security-check.sh with the
OPTIONAL block uncommented (and PROTECTED_BRANCHES set for the branch tests).

This is the home for the AWS / CDK / Terraform / Pulumi / kubectl / DB-migration /
package-publishing / container-registry rules that were domain-specific in the
source project. If you enable these rules in your own copy, this module is your
regression coverage.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest


SECURITY_HOOK = Path(__file__).parent.parent / "hooks" / "security-check.sh"


def _enable_optional_rules(source: str) -> str:
    """Uncomment the `FORCE_ASK_PATTERNS+=(...)` lines in the OPTIONAL block.

    Matches lines like `# FORCE_ASK_PATTERNS+=('...')` (with leading whitespace)
    and strips the leading `# `. Leaves prose comments untouched.
    """
    out_lines = []
    for line in source.splitlines():
        m = re.match(r'^(\s*)#\s(FORCE_ASK_PATTERNS\+=\(.*)$', line)
        if m:
            out_lines.append(m.group(1) + m.group(2))
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def _set_protected_branches(source: str, branches) -> str:
    """Replace the empty PROTECTED_BRANCHES=() with a populated array."""
    joined = " ".join(f'"{b}"' for b in branches)
    return re.sub(
        r'^PROTECTED_BRANCHES=\(\)\s*$',
        f'PROTECTED_BRANCHES=({joined})',
        source,
        count=1,
        flags=re.MULTILINE,
    )


@pytest.fixture
def patched_hook(tmp_path):
    """Return a callable building a temp hook with chosen modifications.

    Usage:
        hook = patched_hook(enable_optional=True)
        hook = patched_hook(protected_branches=["main", "staging"])
    """
    source = SECURITY_HOOK.read_text()

    def _build(enable_optional: bool = False, protected_branches=None) -> Path:
        content = source
        if enable_optional:
            content = _enable_optional_rules(content)
        if protected_branches:
            content = _set_protected_branches(content, protected_branches)
        dest = tmp_path / "security-check.sh"
        dest.write_text(content)
        dest.chmod(0o755)
        return dest

    return _build


def _run(hook_path: Path, tool_name: str, command: str = "", file_path: str = ""):
    payload = json.dumps({
        "tool_name": tool_name,
        "tool_input": {"command": command, "file_path": file_path},
    })
    result = subprocess.run(
        ["bash", str(hook_path)],
        input=payload, capture_output=True, text=True, timeout=5,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _assert_force_ask(hook_path, command):
    code, out, err = _run(hook_path, "Bash", command=command)
    assert code == 0, f"expected exit 0 for {command!r}, got {code} (stderr: {err})"
    assert "hookSpecificOutput" in out and '"permissionDecision":"ask"' in out, (
        f"expected force-ask JSON for {command!r}, got: {out}"
    )


def _assert_blocked(hook_path, command):
    code, out, err = _run(hook_path, "Bash", command=command)
    assert code == 2, f"expected exit 2 for {command!r}, got {code}"
    assert "BLOCKED" in err


class TestSanityWhenDisabled:
    """When the OPTIONAL block is left commented (default), these pass through."""

    def test_cdk_destroy_allowed_when_disabled(self, patched_hook):
        hook = patched_hook(enable_optional=False)
        code, out, _ = _run(hook, "Bash", command="cdk destroy MyStack")
        assert code == 0 and "permissionDecision" not in out


class TestAWSDestructiveWhenEnabled:
    def test_aws_s3_delete(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws s3 delete-object --bucket b --key k")

    def test_aws_s3_rm(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws s3 rm s3://my-bucket/file.txt")

    def test_aws_s3_rb(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws s3 rb s3://my-bucket --force")

    def test_aws_ec2_terminate(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws ec2 terminate-instances --instance-ids i-12345")

    def test_aws_cloudformation_delete(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws cloudformation delete-stack --stack-name s")

    def test_aws_iam_delete_user(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws iam delete-user --user-name u")

    def test_aws_lambda_delete(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "aws lambda delete-function --function-name f")


class TestIaCWhenEnabled:
    def test_cdk_destroy(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "cdk destroy MyStack")

    def test_terraform_destroy(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "terraform destroy")

    def test_terraform_destroy_auto_approve(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "terraform destroy -auto-approve")

    def test_pulumi_destroy(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "pulumi destroy")

    def test_kubectl_delete_namespace(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "kubectl delete namespace production")

    def test_kubectl_delete_all(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "kubectl delete --all pods")

    def test_cdk_deploy(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "cdk deploy")

    def test_terraform_apply(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "terraform apply")

    def test_pulumi_up(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "pulumi up")


class TestCITriggersWhenEnabled:
    def test_gh_workflow_run(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "gh workflow run deploy.yml")

    def test_gh_run_rerun(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "gh run rerun 12345")


class TestDatabaseMigrationsWhenEnabled:
    def test_dropdb(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "dropdb mydb")

    def test_alembic_upgrade(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "alembic upgrade head")

    def test_alembic_downgrade(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "alembic downgrade -1")

    def test_alembic_revision(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "alembic revision --autogenerate -m 'add table'")


class TestPublishingWhenEnabled:
    def test_npm_publish(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "npm publish")

    def test_pip_upload(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "pip upload dist/*")

    def test_twine_upload(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "twine upload dist/*")

    def test_docker_push(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True),
                          "docker push myimage:latest")

    def test_docker_login(self, patched_hook):
        _assert_force_ask(patched_hook(enable_optional=True), "docker login")


class TestBranchProtectionWhenEnabled:
    """PROTECTED_BRANCHES gates pushes and Write/Edit on those branches."""

    def test_push_to_protected_branch_force_asks(self, patched_hook):
        _assert_force_ask(patched_hook(protected_branches=["main"]),
                          "git push origin main")

    def test_push_to_unprotected_branch_allowed(self, patched_hook):
        hook = patched_hook(protected_branches=["main"])
        code, out, _ = _run(hook, "Bash", command="git push origin feature/x")
        assert code == 0 and "permissionDecision" not in out
