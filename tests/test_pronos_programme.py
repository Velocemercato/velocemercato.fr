"""Tests isolés : interdiction d'envoyer un vrai post depuis ces essais."""
import ast
import datetime as dt
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo


class DeliveryError(RuntimeError):
    pass


class FakeState:
    def __init__(self, confirmed=True):
        self.saves = 0
        self.data = {"meta_pronos_accuses": {}}
        if confirmed:
            self.data["meta_pronos_accuses"]["test/unique"] = {
                "status": "publie_confirme",
                "id": "112294796981981_1234",
                "url": "https://www.facebook.com/112294796981981_1234",
            }

    def save(self):
        self.saves += 1


def load_publish_slot(candidates=None):
    source = Path(__file__).resolve().parents[1] / "tools" / "pronos_programme.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "publish_slot")
    graph = Mock()
    mock_verification = Mock(return_value="https://www.facebook.com/112294796981981_9876")
    env = {
        "os": os, "dt": dt, "UTC": dt.timezone.utc, "PARIS": ZoneInfo("Europe/Paris"),
        "SLOTS": {18: "actus"},
        "DeliveryError": DeliveryError,
        "page_access": lambda state: {
            "page_id": "112294796981981", "page_token": "TOKEN_TEST"},
        "candidates": lambda now, kind: candidates if candidates is not None else [{
            "key": "actus/id-a",
            "text": "Une actualité avec ses faits vérifiés.",
            "link": "https://velocemercato.fr/actus/"}],
        "safe_url": lambda url: str(url).startswith("https://"),
        "verify": mock_verification,
    }
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), "exec"), env)
    return env["publish_slot"], graph, mock_verification


class PublicationTests(unittest.TestCase):
    NOW = dt.datetime(2026, 10, 31, 17, 35, tzinfo=dt.timezone.utc)  # 18h35 Paris

    def test_off_does_not_post(self):
        fn, graph, _ = load_publish_slot()
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "false"}):
            self.assertFalse(fn(FakeState(), graph, self.NOW))
        graph.call.assert_not_called()

    def test_unconfirmed_test_does_not_post(self):
        fn, graph, _ = load_publish_slot()
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(confirmed=False), graph, self.NOW))
        graph.call.assert_not_called()

    def test_one_post_only_and_no_repeat_on_same_slot(self):
        fn, graph, verify = load_publish_slot()
        state = FakeState()
        graph.call.return_value = {"id": "112294796981981_9876"}
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertTrue(fn(state, graph, self.NOW))
            self.assertFalse(fn(state, graph, self.NOW))
        self.assertEqual(graph.call.call_count, 1)
        self.assertEqual(graph.call.call_args.args[1], "112294796981981/feed")
        self.assertEqual(verify.call_count, 1)
        self.assertEqual(state.data["meta_pronos_accuses"]["post/actus/id-a"]["status"], "publie_confirme")

    def test_failed_post_is_never_resent_blindly(self):
        fn, graph, _ = load_publish_slot()
        state = FakeState()
        graph.call.side_effect = DeliveryError("erreur fictive")
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            with self.assertRaises(DeliveryError):
                fn(state, graph, self.NOW)
            self.assertFalse(fn(state, graph, self.NOW))
        self.assertEqual(graph.call.call_count, 1)
        self.assertEqual(state.data["meta_pronos_accuses"]["post/actus/id-a"]["status"], "envoi")

    def test_no_new_content_does_not_post(self):
        fn, graph, _ = load_publish_slot(candidates=[])
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(), graph, self.NOW))
        graph.call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
