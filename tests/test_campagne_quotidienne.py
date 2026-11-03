"""Campagne quotidienne : calendrier valide, pause/arrêt respectés, publication unique."""
from datetime import datetime, date, timedelta
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.publier_campagne_du_jour as pj
import tools.campagne_quotidienne as cq
from tools.diffuser_jt import DeliveryError

CAL = json.loads((ROOT / 'campagnes/calendrier.json').read_text(encoding='utf-8'))


class FakeState:
    def __init__(self):
        self.data = {'tokens': {
            'meta': {'page_id': '1384363904759072', 'page_token': 'x', 'ig_id': 'ig1'},
            'meta_univers': {'page_id': '1349998758205153', 'page_token': 'y', 'ig_id': 'ig2'}}}

    def save(self):
        pass


class FakeGraph:
    def __init__(self):
        self.calls = []

    def call(self, method, path, params):
        self.calls.append((method, path))
        if method == 'GET':
            field = params.get('fields')
            if field in ('permalink', 'permalink_url'):
                return {field: 'https://example.invalid/' + path}
            return {'status_code': 'FINISHED'}
        if path.endswith('/photos'):
            return {'id': 'p', 'post_id': 'post_' + path.split('/')[0]}
        if path.endswith('/media'):
            return {'id': 'c'}
        return {'id': 'id_' + path.split('/')[0]}


def posts(graph):
    return [c for c in graph.calls if c[0] == 'POST' and c[1].endswith(('/photos', '/videos', '/media_publish'))]


class CalendrierTests(unittest.TestCase):
    def test_calendar_is_complete_and_points_to_our_sites(self):
        days = [d['date'] for d in CAL['jours']]
        self.assertEqual(len(days), len(set(days)))
        self.assertEqual(days, sorted(days))
        for d in CAL['jours']:
            self.assertIn(d['statut'], ('pret', 'pause', 'publie'))
            self.assertRegex(d['lien'], r'^https://(velocemercato\.fr|vmunivers\.fr)/')
            self.assertIn(d['lien'], d['texte'])
            self.assertIn('#VeloceTeam', d['texte'])
            for kind, path in cq.files(d).items():
                if kind == 'video' and not (d.get('reel') or d.get('youtube_short')):
                    continue
                self.assertTrue((ROOT / path).is_file(), path)
        shorts = [d for d in CAL['jours'] if d.get('youtube_short')]
        for d in shorts:  # pas de Short de JT le dimanche : la place est libre
            self.assertEqual(date.fromisoformat(d['date']).isoweekday(), 7, d['date'])

    def test_every_poster_fits(self):
        for d in CAL['jours']:
            for h in (1350, 1920):
                img = cq.poster(d, h)
                self.assertEqual(img.size, (1080, h))

    def test_instagram_text_has_no_dead_links(self):
        for d in CAL['jours']:
            text = pj.ig_text(d['texte'])
            self.assertNotIn('https://', text)
            self.assertIn(d['lien'].replace('https://', '').rstrip('/'), text)


class PublicationTests(unittest.TestCase):
    def entry(self, **extra):
        base = dict(CAL['jours'][0])
        base.update(extra)
        return base

    def test_paused_or_disabled_days_publish_nothing(self):
        when = datetime.fromisoformat(CAL['jours'][0]['date'] + 'T17:41').replace(tzinfo=ZoneInfo('Europe/Paris'))
        with mock.patch.object(pj.json, 'loads', return_value=dict(CAL, actif=False)):
            self.assertIsNone(pj.today_entry(when))
        paused = dict(CAL, jours=[dict(CAL['jours'][0], statut='pause')])
        with mock.patch.object(pj.json, 'loads', return_value=paused):
            self.assertIsNone(pj.today_entry(when))
        self.assertEqual(pj.today_entry(when)['date'], CAL['jours'][0]['date'])
        later = when + timedelta(days=400)
        self.assertIsNone(pj.today_entry(later))

    def test_photo_day_then_no_duplicate(self):
        state, graph = FakeState(), FakeGraph()
        rows = pj.publish(state, self.entry(reel=False, youtube_short=False), graph)
        self.assertEqual(len(posts(graph)), 6)  # 2 Pages × photo FB + photo IG + story
        self.assertTrue(all(r['statut'] == 'publie' for r in rows))
        graph2 = FakeGraph()
        pj.publish(state, self.entry(reel=False, youtube_short=False), graph2)
        self.assertFalse(posts(graph2))

    def test_reel_day_uses_videos_and_short_only_when_flagged(self):
        state, graph, shorts = FakeState(), FakeGraph(), []
        fake_short = lambda s, e, p: (shorts.append(e['date']) or 'abcdefghijk', 'https://www.youtube.com/shorts/abcdefghijk')
        pj.publish(state, self.entry(reel=True, youtube_short=False), graph, short=fake_short)
        self.assertEqual(len([c for c in graph.calls if c[1].endswith('/videos')]), 2)
        self.assertFalse([c for c in graph.calls if c[1].endswith('/photos')])
        self.assertEqual(shorts, [])
        rows = pj.publish(FakeState(), self.entry(reel=True, youtube_short=True), FakeGraph(), short=fake_short)
        self.assertEqual(len(shorts), 1)
        self.assertIn('https://www.youtube.com/shorts/abcdefghijk', [r.get('lien') for r in rows])

    def test_pronos_page_is_never_targeted_and_wrong_page_blocks(self):
        state, graph = FakeState(), FakeGraph()
        state.data['tokens']['meta_pronos'] = {'page_id': '112294796981981', 'page_token': 'z'}
        pj.publish(state, self.entry(reel=False), graph)
        self.assertFalse([c for c in graph.calls if c[1].startswith('112294796981981')])
        bad = FakeState()
        bad.data['tokens']['meta']['page_id'] = '999'
        with self.assertRaises(DeliveryError):
            pj.publish(bad, self.entry(), FakeGraph())

    def test_custom_promo_video_is_used_for_reel_and_facebook_video(self):
        state, graph = FakeState(), FakeGraph()
        sent = []
        orig = graph.call
        def call(method, path, params):
            sent.append(params.get('file_url') or params.get('video_url') or '')
            return orig(method, path, params)
        graph.call = call
        day = self.entry(reel=True, youtube_short=False, video='assets/social/promo/foot-amateur.mp4')
        pj.publish(state, day, graph)
        used = [u for u in sent if u]
        self.assertEqual(len(used), 4)  # vidéo Facebook + Reel Instagram, sur les deux Pages
        self.assertTrue(all(u == 'https://velocemercato.fr/assets/social/promo/foot-amateur.mp4' for u in used))

    def test_video_outside_vm_folders_is_refused(self):
        for bad in ('media/tiers.mp4', 'assets/social/promo/../../x.mp4', 'https://exemple.com/v.mp4', 'assets/social/promo/a.mov'):
            with self.assertRaises(ValueError):
                cq.files(self.entry(video=bad))


if __name__ == '__main__':
    unittest.main()
