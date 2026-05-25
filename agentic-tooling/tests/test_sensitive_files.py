"""
Tests for SENSITIVE_FILES patterns in the portable security-check.sh.

These patterns block Read/Write access to credential and secret files.
"""

import pytest


class TestEnvFiles:
    """Environment files containing secrets."""

    def test_read_env_file(self, assert_blocked):
        assert_blocked("Read", file_path="/app/.env")

    def test_read_env_local(self, assert_blocked):
        assert_blocked("Read", file_path="/app/.env.local")

    def test_read_env_production(self, assert_blocked):
        assert_blocked("Read", file_path="/app/.env.production")

    def test_read_env_development(self, assert_blocked):
        assert_blocked("Read", file_path="backend/.env.development")

    def test_write_env_file(self, assert_blocked):
        assert_blocked("Write", file_path="/app/.env")

    def test_edit_env_file(self, assert_blocked):
        assert_blocked("Edit", file_path="/app/.env")

    def test_env_example_variants_still_blocked(self, assert_blocked):
        # Only exact .env.example is whitelisted, not variations.
        assert_blocked("Read", file_path="/app/.env.example.bak")

    def test_env_sample_not_whitelisted(self, assert_blocked):
        # .env.sample is NOT whitelisted (only .env.example).
        assert_blocked("Read", file_path="/app/.env.sample")


class TestAWSCredentials:
    """AWS credential files."""

    def test_read_aws_credentials(self, assert_blocked):
        assert_blocked("Read", file_path="/home/user/.aws/credentials")

    def test_read_aws_config(self, assert_blocked):
        assert_blocked("Read", file_path="/home/user/.aws/config")

    def test_write_aws_credentials(self, assert_blocked):
        assert_blocked("Write", file_path="~/.aws/credentials")


class TestSSHKeys:
    """SSH key files."""

    def test_read_ssh_private_key(self, assert_blocked):
        assert_blocked("Read", file_path="/home/user/.ssh/id_rsa")

    def test_read_ssh_ed25519(self, assert_blocked):
        assert_blocked("Read", file_path="/home/user/.ssh/id_ed25519")

    def test_read_ssh_config(self, assert_blocked):
        assert_blocked("Read", file_path="~/.ssh/config")

    def test_write_ssh_key(self, assert_blocked):
        assert_blocked("Write", file_path="/root/.ssh/id_rsa")


class TestKubeConfig:
    """Kubernetes configuration."""

    def test_read_kube_config(self, assert_blocked):
        assert_blocked("Read", file_path="/home/user/.kube/config")

    def test_read_kube_credentials(self, assert_blocked):
        assert_blocked("Read", file_path="~/.kube/credentials")


class TestGitHubConfig:
    """GitHub CLI configuration."""

    def test_read_gh_hosts(self, assert_blocked):
        assert_blocked("Read", file_path="/home/user/.config/gh/hosts.yml")

    def test_read_gh_config(self, assert_blocked):
        assert_blocked("Read", file_path="~/.config/gh/config.yml")


class TestCredentialFiles:
    """Generic credential files."""

    def test_read_credentials_json(self, assert_blocked):
        assert_blocked("Read", file_path="/app/credentials.json")

    def test_read_google_credentials(self, assert_blocked):
        assert_blocked("Read", file_path="/app/google-credentials.json")

    def test_read_service_credentials(self, assert_blocked):
        assert_blocked("Read", file_path="config/service_credentials.yaml")


class TestCertificateFiles:
    """Certificate and key files."""

    def test_read_pem_file(self, assert_blocked):
        assert_blocked("Read", file_path="/etc/ssl/private/server.pem")

    def test_read_key_file(self, assert_blocked):
        assert_blocked("Read", file_path="/etc/ssl/private/server.key")

    def test_read_private_key(self, assert_blocked):
        assert_blocked("Read", file_path="/app/certs/private.key")

    def test_write_pem_file(self, assert_blocked):
        assert_blocked("Write", file_path="./certs/cert.pem")


class TestPathTraversal:
    """Path-traversal check is disabled (was overly restrictive).

    Sensitive-file pattern matching still catches the .ssh/id_rsa path below.
    Tests kept as regression coverage in case the '..' check is re-enabled.
    """

    def test_path_traversal_simple(self, assert_allowed):
        # /etc/passwd not in SENSITIVE_FILES, no '..' check -> passes through.
        assert_allowed("Read", file_path="/app/../etc/passwd")

    def test_path_traversal_multiple(self, assert_allowed):
        assert_allowed("Read", file_path="/var/www/../../etc/shadow")

    def test_path_traversal_in_middle(self, assert_blocked):
        # Still blocked — id_rsa matches SENSITIVE_FILES regardless of '..'.
        assert_blocked("Read", file_path="/app/config/../../../root/.ssh/id_rsa")


class TestAllowedFiles:
    """Files that should be allowed."""

    def test_read_regular_python(self, assert_allowed):
        assert_allowed("Read", file_path="/app/main.py")

    def test_read_typescript(self, assert_allowed):
        assert_allowed("Read", file_path="/app/src/index.ts")

    def test_read_json_config(self, assert_allowed):
        assert_allowed("Read", file_path="/app/config.json")

    def test_read_env_example(self, assert_allowed):
        # .env.example is whitelisted — safe template without real secrets.
        assert_allowed("Read", file_path="/app/.env.example")

    def test_write_env_example(self, assert_allowed):
        assert_allowed("Write", file_path="/app/.env.example")

    def test_edit_env_example(self, assert_allowed):
        assert_allowed("Edit", file_path="/app/.env.example")

    def test_write_source_file(self, assert_allowed):
        assert_allowed("Write", file_path="/app/src/utils.ts")

    def test_edit_readme(self, assert_allowed):
        assert_allowed("Edit", file_path="/app/README.md")

    def test_read_dockerfile(self, assert_allowed):
        assert_allowed("Read", file_path="/app/Dockerfile")


class TestBashCommandsWithSensitiveFiles:
    """Bash commands should not be blocked by file patterns."""

    def test_bash_command_not_file_blocked(self, assert_allowed):
        assert_allowed("Bash", command="ls -la", file_path="")

    def test_bash_with_env_in_command(self, assert_allowed):
        assert_allowed("Bash", command="ls .env.example")
