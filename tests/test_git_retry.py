"""Envoi des accusés : nouvelles tentatives sur coupure, jamais sur refus, message sans secret."""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tools.diffuser_jt as D  # noqa: E402


def failure(stderr):
    return subprocess.CalledProcessError(1, ['git', '-c', 'credential.helper=x', 'push', '--quiet', 'origin', 'HEAD:x'],
                                         stderr=stderr)


class GitRetryTests(unittest.TestCase):
    def test_transient_failure_is_retried_then_succeeds(self):
        calls, sleeps = [], []
        def run(*args, **kwargs):
            calls.append(args)
            if len(calls) < 3:
                raise failure(b'fatal: unable to access https://x-access-token:SECRET@github.com/: Could not resolve host')
        with patch.object(D.subprocess, 'run', side_effect=run):
            D.git_push_with_retry('.', 'HEAD:broadcast-state', attempts=3, sleep=sleeps.append)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [2, 4])

    def test_rejected_push_is_not_retried_nor_forced(self):
        calls = []
        def run(cmd, **kwargs):
            calls.append(cmd)
            raise failure(b' ! [rejected] HEAD -> broadcast-state (non-fast-forward)')
        with patch.object(D.subprocess, 'run', side_effect=run), self.assertRaises(subprocess.CalledProcessError):
            D.git_push_with_retry('.', 'HEAD:broadcast-state', attempts=3, sleep=lambda s: None)
        self.assertEqual(len(calls), 1)
        self.assertNotIn('--force', calls[0])

    def test_gives_up_after_last_attempt(self):
        with patch.object(D.subprocess, 'run', side_effect=failure(b'fatal: early EOF')), \
                self.assertRaises(subprocess.CalledProcessError):
            D.git_push_with_retry('.', 'HEAD:x', attempts=3, sleep=lambda s: None)

    def test_description_hides_tokens_and_urls(self):
        text = D.describe_called_process(failure(
            b'remote: ghp_ABCDEF1234567890 denied\nfatal: https://x-access-token:SECRET@github.com/repo.git not found'))
        self.assertIn('git push', text)
        self.assertIn('code 1', text)
        self.assertNotIn('SECRET', text)
        self.assertNotIn('github.com', text)
        self.assertNotIn('ghp_', text)


if __name__ == '__main__':
    unittest.main()
