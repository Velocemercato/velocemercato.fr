"""Tests exclusivement hors ligne : sécurisation destination exacte Meta.

Aucun jeton réel, réseau, effet sur Facebook/Instagram ni diffusion.
"""
import ast
import contextlib
import io
import os
import re
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class DeliveryError(Exception):
    pass


class State:
    def __init__(self, data=None):
        self.data = data or {"tokens": {}}
        self.saves = 0

    def save(self):
        self.saves += 1


def code(names):
    src = Path(__file__).resolve().parents[1] / "tools" / "publier_meta.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {"DeliveryError": DeliveryError, "os": os, "re": re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(src), "exec"), ns)
    return ns


IDS = {"meta": "1384363904759072", "meta_univers": "1349998758205153", "meta_pronos": "112294796981981"}


class Safety(unittest.TestCase):
    def tokens(self):
        return {
            key: {"page_id": value, "page_token": "TOKEN_FAKE",
                  "ig_id": "" if key == "meta_pronos" else "IG_FAKE",
                  "ig_username": "" if key == "meta_pronos" else "name"}
            for key, value in IDS.items()
        }

    def test_all_three_exact_ids_allowed_without_mutation(self):
        state = State({"tokens": self.tokens()})
        code(["ensure_meta_targets"])["ensure_meta_targets"](state)
        self.assertEqual(state.saves, 0)

    def test_wrong_account_id_blocks_broadcast(self):
        s = State({"tokens": self.tokens()})
        s.data["tokens"]["meta"]["page_id"] = IDS["meta_univers"]
        with self.assertRaises(DeliveryError):
            code(["ensure_meta_targets"])["ensure_meta_targets"](s)
        self.assertEqual(s.saves, 0)

    def test_wrong_pronos_id_blocks_broadcast(self):
        s = State({"tokens": self.tokens()})
        s.data["tokens"]["meta_pronos"]["page_id"] = "111111111111111"
        with self.assertRaises(DeliveryError):
            code(["ensure_meta_targets"])["ensure_meta_targets"](s)

    def test_instagram_on_pronos_blocks_broadcast(self):
        s = State({"tokens": self.tokens()})
        s.data["tokens"]["meta_pronos"]["ig_id"] = "123"
        with self.assertRaises(DeliveryError):
            code(["ensure_meta_targets"])["ensure_meta_targets"](s)

    def test_connect_selects_explicit_id_not_first_api_entry(self):
        graph = Mock()
        graph.call.side_effect = [
            {"access_token": "LONG_FAKE"},
            {"data": [
                {"id": "000000000000000", "access_token": "WRONG", "name": "Other"},
                {"id": IDS["meta_pronos"], "access_token": "RIGHT", "name": "RQ",
                 "instagram_business_account": {"id": "must-not-use"}},
            ]},
        ]
        state = State({"tokens": {}})
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": IDS["meta_pronos"]}, clear=True):
            with contextlib.redirect_stdout(io.StringIO()):
                ret = code(["connect"])["connect"](state, graph, "123", "X", "USER", scope="pronos")
        self.assertEqual(ret, {"meta_pronos": IDS["meta_pronos"]})
        self.assertEqual(state.data["tokens"]["meta_pronos"]["page_token"], "RIGHT")
        self.assertEqual(state.data["tokens"]["meta_pronos"]["ig_id"], "")
        self.assertEqual(state.saves, 1)

    def test_connect_wrong_explicit_id_fails_even_if_first_page(self):
        graph, state = Mock(), State()
        with patch.dict(os.environ, {"VM_FACEBOOK_PRONOS_PAGE_ID": "222222222222222"}, clear=True):
            with self.assertRaises(DeliveryError):
                code(["connect"])["connect"](state, graph, "123", "X", "USER", scope="pronos")
        graph.call.assert_not_called()
        self.assertEqual(state.saves, 0)

    def test_publish_wrong_account_and_wrong_page_refused_before_api(self):
        src = Path(__file__).resolve().parents[1] / "tools" / "publier_meta.py"
        tree = ast.parse(src.read_text(encoding="utf-8"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "publish")
        import datetime as dt
        import time
        from zoneinfo import ZoneInfo
        ns = {"DeliveryError": DeliveryError, "dt": dt, "time": time,
              "ROOT": src.parents[1],
              "UTC": dt.timezone.utc, "PARIS": ZoneInfo("Europe/Paris"), "os": os}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), str(src), "exec"), ns)
        state = State({"tokens": self.tokens()})
        state.data["tokens"]["meta"]["page_id"] = IDS["meta_univers"]
        graph = Mock()
        with self.assertRaises(DeliveryError):
            ns["publish"](state, graph, account="meta")
        with self.assertRaises(DeliveryError):
            ns["publish"](state, graph, account="meta_pronos")
        graph.call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
