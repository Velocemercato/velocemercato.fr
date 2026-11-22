import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from tools import editorial_vm as mod

NOW = dt.datetime(2026, 11, 11, 11, 5, tzinfo=dt.timezone.utc)


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
    def test_daily_slots_are_bounded_in_both_time_zones(self):
        expected = {
            ('meta', 'facebook'): (8, 12, 20),
            ('meta', 'instagram'): (12, 20),
            ('meta_pronos', 'facebook'): (12, 20),
            ('meta_univers', 'facebook'): (8, 12, 18),
            ('meta_univers', 'instagram'): (18,),
        }
        for month in (7, 11):
            midnight = dt.datetime(2026, month, 11, tzinfo=mod.PARIS)
            for account, network in expected:
                keys = {mod.slot_key(midnight + dt.timedelta(minutes=minute), account, network)
                        for minute in range(1440)} - {None}
                self.assertEqual(len(keys), len(expected[account, network]))
                for hour in expected[account, network]:
                    start = midnight.replace(hour=hour)
                    self.assertIn(mod.slot_key(start, account, network), keys)
                    self.assertEqual(mod.slot_key(start, account, network),
                                     mod.slot_key(start.replace(minute=49), account, network))
                    self.assertIsNone(mod.slot_key(start.replace(minute=50), account, network))

    def test_outside_slot_no_state_or_graph_access(self):
        midnight = NOW.replace(hour=1)
        result = mod.run(self.state, None, self.root, midnight)
        self.assertEqual(result['targets'], {})
        self.assertEqual(result['unconnected'], [])
        self.assertEqual(mod.publish_target(self.state, None, 'meta', 'facebook', self.root, midnight)['status'],
                         'hors_creneau')
        self.assertEqual(self.state.saves, 0)
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


    def test_all_five_targets_have_distinct_expected_identity_and_schedule(self):
        expected = {
            'meta': ('1384363904759072', 'veloce.mercato'),
            'meta_pronos': ('112294796981981', None),
            'meta_univers': ('1349998758205153', 'vmunivers.fr'),
        }
        self.assertEqual({k: (v[0], v[2]) for k, v in mod.TARGETS.items()}, expected)
        self.assertEqual(mod.SCHEDULE, {
            ('meta', 'facebook'): (8, 12, 20),
            ('meta', 'instagram'): (12, 20),
            ('meta_pronos', 'facebook'): (12, 20),
            ('meta_univers', 'facebook'): (8, 12, 18),
            ('meta_univers', 'instagram'): (18,),
        })

    def test_pronos_never_has_instagram_target(self):
        self.assertNotIn(('meta_pronos', 'instagram'), mod.SCHEDULE)
        self.assertIsNone(mod.TARGETS['meta_pronos'][2])

    def test_each_expected_destination_requires_its_own_page_token(self):
        class IdentityGraph:
            def call(self, method, path, params):
                pages = {value[0] for value in mod.TARGETS.values()}
                if path in pages:
                    account = next(k for k, value in mod.TARGETS.items() if value[0] == path)
                    return {'id': path, 'name': mod.TARGETS[account][1]}
                instagram = {
                    'ig-meta': 'veloce.mercato',
                    'ig-meta_univers': 'vmunivers.fr',
                }
                if path in instagram:
                    return {'id': path, 'username': instagram[path]}
                raise AssertionError('Destination inconnue : ' + str(path))

        graph = IdentityGraph()
        state = State()
        state.data['tokens'] = {
            'meta': {'page_id': '1384363904759072', 'page_token': 'fb-main',
                     'ig_id': 'ig-meta'},
            'meta_univers': {'page_id': '1349998758205153', 'page_token': 'fb-univers',
                             'ig_id': 'ig-meta_univers'},
            'meta_pronos': {'page_id': '112294796981981', 'page_token': 'fb-pronos'},
        }
        mod.ensure_meta_targets(state)
        destinations = (
            ('meta', 'facebook'), ('meta', 'instagram'),
            ('meta_univers', 'facebook'), ('meta_univers', 'instagram'),
            ('meta_pronos', 'facebook'),
        )
        for account, network in destinations:
            proof = mod.identity(graph, state.data['tokens'][account], account, network)
            self.assertTrue(proof['id'])
        self.assertNotIn('ig_id', state.data['tokens']['meta_pronos'])

    def test_editorial_refuses_duplicate_page_or_instagram_on_pronos(self):
        state = State()
        state.data['tokens'] = {
            'meta': {'page_id': '1384363904759072', 'page_token': 'one'},
            'meta_pronos': {'page_id': '1384363904759072', 'page_token': 'two'},
        }
        with self.assertRaises(mod.DeliveryError):
            mod.ensure_meta_targets(state)
        state.data['tokens'] = {
            'meta_pronos': {'page_id': '112294796981981', 'page_token': 'two', 'ig_id': 'forbidden'},
        }
        with self.assertRaises(mod.DeliveryError):
            mod.ensure_meta_targets(state)


if __name__ == '__main__':
    unittest.main()
