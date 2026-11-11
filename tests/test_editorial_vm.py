import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from tools import editorial_vm as mod

NOW = dt.datetime(2026, 11, 11, 9, 5, tzinfo=dt.timezone.utc)


class State:
    def __init__(self):
        self.data = {'tokens': {'meta': {'page_id': '1384363904759072', 'page_token': 'test', 'ig_id': '123'}}}
        self.saves = 0
    def save(self):
        self.saves += 1


class Graph:
    def __init__(self, state, fail=False, quota=0, username='veloce.mercato'):
        self.state, self.fail, self.quota, self.username = state, fail, quota, username
        self.posts = []
    def call(self, method, path, params):
        if method == 'POST':
            self.posts.append((path, params))
            assert any(isinstance(v, dict) and v.get('status') == 'envoi' for v in self.state.data.get('meta', {}).values())
            if self.fail:
                raise TimeoutError('Réponse perdue après envoi')
            return {'id': '1384363904759072_99'}
        if path.endswith('/published_posts') or path.endswith('/media'):
            return {'data': []}
        if path.endswith('/content_publishing_limit'):
            return {'data': [{'quota_usage': self.quota, 'config': {'quota_total': 100}}]}
        if path == '123':
            return {'id': '123', 'username': self.username}
        if path == '1384363904759072':
            return {'id': path, 'name': 'Véloce Mercato'}
        return {'id': path, 'from': {'id': '1384363904759072'}, 'permalink_url': 'https://www.facebook.com/1384363904759072/posts/99'}


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root/'a').mkdir()
        (self.root/'multisport').mkdir()
        (self.root/'multisport/actualites.json').write_text('{"sports":{}}')
        self.row = {'id': 'foot-test-1', 'titre': 'Une actualité sportive vérifiée', 'resume': 'Une brève originale.',
                    'publishedAt': NOW.isoformat(), 'sources': [{'nom': 'Source', 'url': 'https://example.com/article'}]}
        (self.root/'articles.json').write_text(json.dumps([self.row]))
        (self.root/'a/foot-test-1.html').write_text('article')
        self.state = State()
    def tearDown(self):
        self.tmp.cleanup()
    def test_confirmation_and_receipts_prevent_second_post(self):
        graph = Graph(self.state)
        result = mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW)
        self.assertEqual(result['status'], 'publie')
        self.assertEqual(len(result['posts']), 1)
        mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW)
        self.assertEqual(len(graph.posts), 1)
        self.assertEqual(self.state.data['meta']['editorial/facebook/foot/foot-test-1']['status'], 'publie_confirme')
    def test_timeout_never_retried(self):
        graph = Graph(self.state, fail=True)
        result = mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW)
        self.assertEqual(result['status'], 'envoi_a_verifier')
        mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW + dt.timedelta(minutes=20))
        self.assertEqual(len(graph.posts), 1)
    def test_no_post_when_instagram_quota_exhausted(self):
        graph = Graph(self.state, quota=100)
        result = mod.publish_target(self.state, graph, 'meta', 'instagram', self.root, NOW)
        self.assertEqual(result['status'], 'quota_atteint')
        self.assertEqual(graph.posts, [])
    def test_wrong_instagram_identity_stops_before_send(self):
        graph = Graph(self.state, username='autre.compte')
        with self.assertRaises(mod.DeliveryError):
            mod.publish_target(self.state, graph, 'meta', 'instagram', self.root, NOW)
        self.assertEqual(graph.posts, [])
    def test_wrong_page_stops_before_send(self):
        self.state.data['tokens']['meta']['page_id'] = '999'
        graph = Graph(self.state)
        with self.assertRaises(mod.DeliveryError):
            mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW)
        self.assertEqual(graph.posts, [])
    def test_legacy_receipt_and_old_article_are_not_reused(self):
        self.state.data['meta'] = {'article/foot/foot-test-1': {'status': 'envoi'}}
        graph = Graph(self.state)
        result = mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW)
        self.assertEqual(result['posts'], [])
        self.state.data['meta'] = {}
        result = mod.publish_target(self.state, graph, 'meta', 'facebook', self.root, NOW + dt.timedelta(days=2))
        self.assertEqual(result['posts'], [])
    def test_slots_use_requested_periods(self):
        for account, network, interval in [('meta','facebook',10),('meta','instagram',15),('meta_univers','facebook',60)]:
            t = NOW.replace(minute=0)
            self.assertEqual(mod.slot_key(t,account,network),mod.slot_key(t+dt.timedelta(minutes=interval-1),account,network))
            self.assertNotEqual(mod.slot_key(t,account,network),mod.slot_key(t+dt.timedelta(minutes=interval),account,network))
    def test_multisport_filters_string_pattern_without_failing(self):
        import sys
        from types import SimpleNamespace
        from unittest.mock import patch
        rows = {'sports': {'nba': [
            {'id':'nba-test-1','titre':'GTA VI et NBA 2K','date':NOW.isoformat(),'source':'Source','url':'https://example.com/gaming'},
            {'id':'nba-test-2','titre':'NBA : Wembanyama avec les Spurs','date':NOW.isoformat(),'source':'Source','url':'https://example.com/nba'}]}}
        (self.root/'multisport/actualites.json').write_text(json.dumps(rows))
        done = {'article/foot/foot-test-1': True}
        with patch.dict(sys.modules, {'tools.multisport_flux':SimpleNamespace(GAMING_CONTENT=r'\b(?:gta|gaming)\b')}):
            choice = mod.select_news(self.root,NOW,done,'meta','facebook',[])
        self.assertEqual(choice[1]['id'],'nba-test-2')


if __name__ == '__main__':
    unittest.main()
