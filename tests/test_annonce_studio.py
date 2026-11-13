"""Lancement VM Studio : rien avant la date, Facebook + Instagram sur les deux Pages, jamais deux fois (mocks, hors ligne)."""
import ast
import contextlib
import datetime as dt
import io
from pathlib import Path
import subprocess
import time
import unittest
from unittest.mock import Mock
from zoneinfo import ZoneInfo


class DeliveryError(Exception):
    pass


class FakeState:
    def __init__(self):
        self.data = {'tokens': {
            'meta': {'page_id': 'PAGE_VM', 'page_token': 'JETON_FICTIF', 'ig_id': 'IG_VM'},
            'meta_univers': {'page_id': 'PAGE_UNIV', 'page_token': 'JETON_FICTIF', 'ig_id': 'IG_UNIV'},
            'meta_pronos': {'page_id': 'PAGE_PRONOS', 'page_token': 'JETON_FICTIF'}}}

    def save(self):
        pass


class AnnonceStudioTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parents[1] / 'tools' / 'publier_meta.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name == 'annonce_studio')
                or (isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') in ('STUDIO_DEBUT', 'STUDIO_IMAGE', 'ANNONCE_STUDIO'))]
        self.image = Mock(return_value='IG_ID')
        ns = {'dt': dt, 'ZoneInfo': ZoneInfo, 'time': time, 'subprocess': subprocess, 'DeliveryError': DeliveryError,
              'instagram_image': self.image, 'ROOT': Path('.')}
        exec(compile(ast.Module(body=keep, type_ignores=[]), str(source), 'exec'), ns)
        self.f, self.debut, self.texte = ns['annonce_studio'], ns['STUDIO_DEBUT'], ns['ANNONCE_STUDIO']
        self.graph = Mock(); self.graph.call.return_value = {'id': 'FB'}
        self.state = FakeState()

    def go(self, now):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.f(self.state, self.graph, now=now, sleep=lambda _: None, image='https://example.org/carte.jpg')

    def test_rien_avant_la_date(self):
        self.assertEqual(self.go(self.debut - dt.timedelta(minutes=1)), [])
        self.graph.call.assert_not_called(); self.image.assert_not_called()

    def test_publie_sur_les_deux_pages_puis_jamais_deux_fois(self):
        self.assertEqual(self.go(self.debut + dt.timedelta(minutes=5)), [])
        self.assertEqual([c.args[1] for c in self.graph.call.call_args_list], ['PAGE_VM/photos', 'PAGE_UNIV/photos'])
        self.assertEqual(self.image.call_count, 2)
        self.go(self.debut + dt.timedelta(hours=1))
        self.assertEqual(self.graph.call.call_count, 2); self.assertEqual(self.image.call_count, 2)

    def test_jamais_sur_la_page_pronos_et_contenu_conforme(self):
        self.go(self.debut + dt.timedelta(minutes=5))
        self.assertNotIn('PAGE_PRONOS/photos', [c.args[1] for c in self.graph.call.call_args_list])
        for interdit in ('prono', 'cote', 'pari', 'Véloce Universe'):
            self.assertNotIn(interdit.lower(), self.texte.lower())

    def test_echec_non_renvoye(self):
        self.graph.call.side_effect = DeliveryError('refus')
        self.assertTrue(self.go(self.debut + dt.timedelta(minutes=5)))
        self.graph.call.side_effect = None
        self.go(self.debut + dt.timedelta(hours=2))
        self.assertEqual([c.args[1] for c in self.graph.call.call_args_list], ['PAGE_VM/photos', 'PAGE_UNIV/photos'])


if __name__ == '__main__':
    unittest.main()
