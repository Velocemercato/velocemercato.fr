"""Tests hors ligne : aucun appel réel à Facebook, aucun contenu publié."""
import ast
import contextlib
import datetime as dt
import io
import os
from pathlib import Path
import re
import unittest
from unittest.mock import Mock, patch


class DeliveryError(Exception):
    pass


class State:
    def __init__(self, data=None):
        self.data = data or {"tokens": {}}
        self.saves = 0

    def save(self):
        self.saves += 1


def load_functions(path, names, extra=None):
    source = Path(__file__).resolve().parents[1] / path
    parsed = ast.parse(source.read_text(encoding="utf-8"))
    nodes = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in names]
    env = {"os": os, "re": re, "dt": dt, "DeliveryError": DeliveryError,
           "VALID_POST": re.compile(r"^[0-9]+_[0-9]+$"),
           "VALID_URL": re.compile(r"^https://(?:www\.|m\.)?facebook\.com/[^\s]+$")}
    env.update(extra or {})
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), env)
    return env


class PronosTest(unittest.TestCase):
    PAGE = "112294796981981"

    def test_connected_by_exact_page_id_and_no_instagram(self):
        code = load_functions("tools/publier_meta.py", ["connect"])
        graph = Mock()
        graph.call.side_effect = [
            {"access_token": "TEST_TOKEN"},
            {"data": [{"id": "111111111111111", "name": "Other", "access_token": "OTHER"},
                      {"id": self.PAGE, "name": "RQ Pronos", "access_token": "TEST_PAGE",
                       "instagram_business_account": {"id": "IGNORED", "username": "ignored"}}]},
        ]
        state = State({"tokens": {"meta": {"page_id": "999999999999", "page_token": "OLD"},
                                  "meta_univers": {"page_id": "888888888888", "page_token": "OLD2"}}})
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": self.PAGE}):
            with contextlib.redirect_stdout(io.StringIO()):
                code["connect"](state, graph, "123456789012", "TEST_SECRET", "TEST_USER", scope="pronos")
        self.assertEqual(state.data["tokens"]["meta"]["page_id"], "999999999999")
        self.assertEqual(state.data["tokens"]["meta_univers"]["page_id"], "888888888888")
        self.assertEqual(state.data["tokens"]["meta_pronos"]["page_id"], self.PAGE)
        self.assertFalse(state.data["tokens"]["meta_pronos"]["ig_id"])
        self.assertEqual(state.saves, 1)

    def test_absent_page_refuses_and_never_uses_first_page(self):
        code = load_functions("tools/publier_meta.py", ["connect"])
        state = State()
        graph = Mock()
        graph.call.side_effect = [{"access_token": "TEST_TOKEN"}, {
            "data": [{"id": "999999999999", "name": "Other", "access_token": "OTHER"}]}]
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": self.PAGE}):
            with self.assertRaises(DeliveryError):
                code["connect"](state, graph, "1", "2", "3", scope="pronos")
        self.assertEqual(state.saves, 0)
        self.assertNotIn("meta_pronos", state.data["tokens"])

    def test_connection_dry_run_is_read_only(self):
        code = load_functions("tools/publier_meta.py", ["connect"])
        state = State()
        graph = Mock()
        graph.call.side_effect = [{"access_token": "TEST_TOKEN"}, {
            "data": [{"id": self.PAGE, "name": "RQ Pronos", "access_token": "TEST_PAGE"}]}]
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": self.PAGE}):
            with contextlib.redirect_stdout(io.StringIO()):
                code["connect"](state, graph, "1", "2", "3", scope="pronos", dry_run=True)
        self.assertEqual(state.saves, 0)
        self.assertNotIn("meta_pronos", state.data["tokens"])

    def sample(self):
        return State({"tokens": {
            "meta": {"page_id": "999999999999"},
            "meta_univers": {"page_id": "888888888888"},
            "meta_pronos": {"page_id": self.PAGE, "page_token": "TEST_PAGE", "ig_id": "", "ig_username": ""}}})

    def test_diagnostic_never_posts(self):
        code = load_functions("tools/pronos_facebook.py", ["page_access", "execute"], {
            "plan": lambda now: [{"key": "foot/test", "text": "Test", "link": "https://velocemercato.fr"}],
            "PARIS": dt.timezone.utc, "UTC": dt.timezone.utc})
        graph, state = Mock(), self.sample()
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": self.PAGE}):
            with contextlib.redirect_stdout(io.StringIO()):
                code["execute"](state, graph, "diagnostic")
        self.assertEqual(graph.call.call_count, 0)
        self.assertEqual(state.saves, 0)

    def test_single_test_post_and_verified_url(self):
        code = load_functions("tools/pronos_facebook.py", ["page_access", "execute", "verify"], {
            "plan": lambda now: [{"key": "foot/test", "text": "Test", "link": "https://velocemercato.fr"}],
            "PARIS": dt.timezone.utc, "UTC": dt.timezone.utc})
        graph, state = Mock(), self.sample()
        post_id = self.PAGE + "_987654"
        url = "https://www.facebook.com/" + post_id
        graph.call.side_effect = [{"id": post_id}, {"id": post_id, "from": {"id": self.PAGE}, "permalink_url": url}]
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": self.PAGE,
                                     "VM_PRONOS_TEST_APPROVED": "true"}):
            with contextlib.redirect_stdout(io.StringIO()):
                code["execute"](state, graph, "test")
            with self.assertRaises(DeliveryError):
                code["execute"](state, graph, "test")
        self.assertEqual(graph.call.call_count, 2)
        self.assertEqual(graph.call.call_args_list[0].args[1], self.PAGE + "/feed")
        self.assertEqual(state.data["meta_pronos_accuses"]["test/unique"]["url"], url)

    def test_wrong_page_response_cannot_be_confirmed(self):
        code = load_functions("tools/pronos_facebook.py", ["verify"])
        graph = Mock()
        with self.assertRaises(DeliveryError):
            code["verify"](graph, "TEST_PAGE", self.PAGE, "999999999999_123")
        graph.call.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
