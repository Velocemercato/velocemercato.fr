"""Tests hors ligne du lancement : aucune publication ni dépendance multimédia.

On charge la vraie fonction par AST pour isoler ce parcours des imports vidéo
du module principal. Les appels aux deux réseaux sont des mocks.
"""
import ast
import contextlib
import io
from pathlib import Path
import subprocess
import time
import unittest
from unittest.mock import Mock


class DeliveryError(Exception):
    pass


class FakeState:
    def __init__(self, instagram=True):
        self.data = {'tokens': {'meta_univers': {
            'page_id': 'PAGE_TEST', 'page_token': 'JETON_FICTIF',
            'ig_id': 'IG_TEST' if instagram else ''}}}
        self.saves = 0

    def save(self):
        self.saves += 1


class LancementTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parents[1] / 'tools' / 'publier_meta.py'
        parsed = ast.parse(source.read_text(encoding='utf-8'))
        function = next(node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name == 'lancement')
        self.reel = Mock(return_value='IG_VIDEO_TEST')
        self.image = Mock(return_value='IG_IMAGE_TEST')
        self.items = [
            {'type': 'video', 'name': 'VM Univers', 'url': 'https://example.org/', 'video': 'https://example.org/video.mp4'},
            {'type': 'carte', 'name': 'VM Studio', 'url': 'https://example.org/studio', 'icon': 'studio', 'pitch': 'Test'},
        ]
        namespace = {'time': time, 'subprocess': subprocess, 'DeliveryError': DeliveryError,
                     'LANCEMENT': self.items, 'texte_univers': lambda item: 'Test 👉 ' + item['url'],
                     'instagram_reel': self.reel, 'instagram_image': self.image,
                     'instagram_projet_card': Mock(return_value='https://example.org/test.jpg')}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
        self.launch = namespace['lancement']
        self.graph = Mock()
        self.graph.call.return_value = {'id': 'FB_TEST'}
        self.state = FakeState()

    def run_launch(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.launch(self.state, self.graph, sleep=lambda _: None)

    def test_new_launch_targets_facebook_and_instagram(self):
        self.assertEqual(self.run_launch(), [])
        self.assertEqual([call.args[1] for call in self.graph.call.call_args_list], ['PAGE_TEST/videos', 'PAGE_TEST/feed'])
        self.reel.assert_called_once()
        self.image.assert_called_once()
        receipts = self.state.data['meta_univers_accuses']
        self.assertEqual(len(receipts), 4)
        self.assertTrue(all(item['status'] == 'publie' and item['post_id'] for item in receipts.values()))

    def test_repeated_launch_never_duplicates(self):
        self.run_launch()
        before = (self.graph.call.call_count, self.reel.call_count, self.image.call_count)
        self.run_launch()
        self.assertEqual((self.graph.call.call_count, self.reel.call_count, self.image.call_count), before)

    def test_legacy_instagram_does_not_suppress_missing_facebook(self):
        self.state.data['meta_univers_accuses'] = {
            'lancement/' + item['name']: {'status': 'publie'} for item in self.items}
        self.assertEqual(self.run_launch(), [])
        self.assertEqual(self.graph.call.call_count, 2)
        self.reel.assert_not_called()
        self.image.assert_not_called()

    def test_ambiguous_legacy_instagram_is_not_resent(self):
        self.state.data['meta_univers_accuses'] = {
            'lancement/VM Univers': {'status': 'envoi'},
            'lancement/VM Studio': {'status': 'echec'}}
        self.run_launch()
        self.reel.assert_not_called()
        self.image.assert_not_called()
        self.assertEqual(self.graph.call.call_count, 2)

    def test_page_without_instagram_still_receives_facebook(self):
        self.state = FakeState(instagram=False)
        self.assertEqual(self.run_launch(), [])
        self.assertEqual(self.graph.call.call_count, 2)
        self.reel.assert_not_called()
        self.image.assert_not_called()

    def test_missing_page_cannot_target_another_account(self):
        self.state.data['tokens'] = {'meta': {'page_id': 'OTHER_PAGE', 'page_token': 'OTHER_TEST'}}
        with self.assertRaises(DeliveryError):
            self.run_launch()
        self.graph.call.assert_not_called()
        self.reel.assert_not_called()
        self.image.assert_not_called()

    def test_facebook_error_does_not_block_instagram(self):
        self.graph.call.side_effect = DeliveryError('échec fictif')
        self.assertEqual(len(self.run_launch()), 2)
        self.reel.assert_called_once()
        self.image.assert_called_once()
        self.assertEqual(self.state.data['meta_univers_accuses']['lancement/facebook/VM Univers']['status'], 'echec')

    def test_instagram_error_does_not_block_facebook(self):
        self.reel.side_effect = DeliveryError('échec fictif')
        self.assertEqual(len(self.run_launch()), 1)
        self.assertEqual(self.graph.call.call_count, 2)
        self.assertEqual(self.state.data['meta_univers_accuses']['lancement/facebook/VM Univers']['status'], 'publie')

    def test_missing_facebook_confirmation_is_not_success(self):
        self.graph.call.return_value = {}
        self.assertEqual(len(self.run_launch()), 2)
        self.assertEqual(self.state.data['meta_univers_accuses']['lancement/facebook/VM Studio']['status'], 'echec')

    def test_missing_instagram_confirmation_is_not_success(self):
        self.image.return_value = None
        self.assertEqual(len(self.run_launch()), 1)
        self.assertEqual(self.state.data['meta_univers_accuses']['lancement/instagram/VM Studio']['status'], 'echec')

    def test_failed_or_inflight_new_attempt_is_not_resent(self):
        self.state.data['meta_univers_accuses'] = {
            'lancement/facebook/VM Univers': {'status': 'envoi'},
            'lancement/instagram/VM Univers': {'status': 'echec'}}
        self.run_launch()
        self.assertEqual(self.graph.call.call_count, 1)
        self.reel.assert_not_called()
        self.image.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
