"""Campagne VÉLOCE TEAM : essai sans publication Meta, publication unique, aucun doublon."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.publier_veloce_team as vt
from tools.diffuser_jt import DeliveryError


class FakeState:
    def __init__(self):
        self.saves = 0
        self.data = {'tokens': {
            'meta': {'page_id': '1384363904759072', 'page_token': 'x', 'ig_id': 'ig1'},
            'meta_univers': {'page_id': '1349998758205153', 'page_token': 'y', 'ig_id': 'ig2'}}}

    def save(self):
        self.saves += 1


class FakeGraph:
    calls = []

    def call(self, method, path, params):
        FakeGraph.calls.append((method, path, dict(params)))
        if method == 'GET' and params.get('fields') == 'permalink_url':
            return {'permalink_url': 'https://www.facebook.com/' + path}
        if method == 'GET' and params.get('fields') == 'permalink':
            return {'permalink': 'https://www.instagram.com/p/' + path + '/'}
        if method == 'GET':
            return {'name': 'Page', 'username': 'compte', 'status_code': 'FINISHED'}
        if path.endswith('/photos'):
            return {'id': 'photo', 'post_id': path.split('/')[0] + '_post'}
        if path.endswith('/media'):
            return {'id': 'container'}
        return {'id': 'media_' + path.split('/')[0]}


class FakeYouTube:
    def __init__(self):
        self.uploads, self.public = 0, 0

    def upload(self, file, metadata, receipt):
        assert metadata['status']['privacyStatus'] == 'public'
        if receipt.get('video_id'):
            return receipt['video_id']
        self.uploads += 1
        receipt.update(video_id='abcdefghijk', status='uploaded')

    def make_public(self, receipt):
        self.public += 1
        receipt['status'] = 'public'


class CampagneTests(unittest.TestCase):
    def setUp(self):
        FakeGraph.calls = []
        self.yt = FakeYouTube()
        self.saved = (vt.Graph, vt.youtube_client)
        vt.Graph = FakeGraph
        vt.youtube_client = lambda state: self.yt
        self.env = dict(vt.os.environ)
        vt.os.environ.update(VM_AUTO_YOUTUBE='true', VM_YOUTUBE_PUBLIC='true')

    def tearDown(self):
        vt.Graph, vt.youtube_client = self.saved
        vt.os.environ.clear()
        vt.os.environ.update(self.env)

    def test_essai_publishes_nothing_anywhere(self):
        state = FakeState()
        vt.essai(state)
        self.assertFalse([c for c in FakeGraph.calls if c[0] == 'POST'])
        self.assertEqual((self.yt.uploads, self.yt.public), (0, 0))
        self.assertEqual(state.data[vt.KEY]['essai']['status'], 'ok')

    def test_publier_requires_successful_essai(self):
        with self.assertRaises(DeliveryError):
            vt.publier(FakeState())
        self.assertFalse(FakeGraph.calls)

    def test_publication_once_with_public_links_then_no_duplicate(self):
        state = FakeState()
        vt.essai(state)
        vt.publier(state)
        posts = [c for c in FakeGraph.calls if c[0] == 'POST' and (c[1].endswith('/photos') or c[1].endswith('/media_publish'))]
        self.assertEqual(len(posts), 6)  # 2 Pages × (photo Facebook + photo Instagram + story)
        self.assertEqual((self.yt.uploads, self.yt.public), (1, 0))
        bilan = state.data[vt.KEY]
        self.assertEqual(bilan['youtube/short']['url'], 'https://www.youtube.com/shorts/abcdefghijk')
        self.assertTrue(bilan['meta/facebook/photo']['url'].startswith('https://www.facebook.com/'))
        self.assertTrue(bilan['meta_univers/instagram/photo']['url'].startswith('https://www.instagram.com/'))
        FakeGraph.calls = []
        vt.essai(state)
        vt.publier(state)
        self.assertFalse([c for c in FakeGraph.calls if c[0] == 'POST'])
        self.assertEqual((self.yt.uploads, self.yt.public), (1, 0))

    def test_existing_private_short_is_never_reuploaded(self):
        state = FakeState()
        vt.essai(state)
        state.data['promos'] = {'veloce-team-short': {'video_id': '_3CM-P0wqJg', 'status': 'private'}}
        with self.assertRaises(DeliveryError):
            vt.publier(state)
        self.assertEqual(self.yt.uploads, 0)
        self.assertIn('studio.youtube.com/video/_3CM-P0wqJg', state.data[vt.KEY]['youtube/short']['raison'])

    def test_unknown_outcome_is_never_resent(self):
        state = FakeState()
        vt.essai(state)
        state.data[vt.KEY]['meta/facebook/photo'] = {'status': 'envoi'}
        vt.publier(state)
        self.assertFalse([c for c in FakeGraph.calls if c[1] == '1384363904759072/photos'])

    def test_wrong_page_id_blocks_everything(self):
        state = FakeState()
        state.data['tokens']['meta']['page_id'] = '999'
        with self.assertRaises(DeliveryError):
            vt.essai(state)
        self.assertFalse([c for c in FakeGraph.calls if c[0] == 'POST'])

    def test_captions_point_to_both_sites(self):
        for site in ('https://velocemercato.fr/', 'https://vmunivers.fr/'):
            self.assertIn(site, vt.CAPTION)
            self.assertIn(site, vt.YT_META['snippet']['description'])
        self.assertNotIn('https://', vt.IG_CAPTION)
        self.assertIn('vmunivers.fr', vt.IG_CAPTION)


if __name__ == '__main__':
    unittest.main()
