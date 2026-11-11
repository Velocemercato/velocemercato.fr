"""JT → TikTok via Metricool : essai sans publication, publication activée seulement sur demande, aucun doublon."""
import datetime as dt
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.tiktok_metricool as tk
from tools.diffuser_jt import DeliveryError

PARIS = ZoneInfo('Europe/Paris')
NOW = dt.datetime(2026, 11, 4, 21, 0, tzinfo=PARIS)
SHA = 'a' * 40


def row(ident='foot-edition-20261104-2000', univers='foot', date='2026-11-04T20:30+01:00'):
    return {'id': ident, 'univers': univers, 'date': date, 'titre': 'La Pastille Foot',
            'texte_vertical': 'Le JT du soir ⚽\nBonsoir.\n\nLe JT complet sur velocemercato.fr 🔗 lien en bio\n#foot',
            'verticale': f'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@{SHA}/{ident}-vertical.mp4'}


class FakeState:
    def __init__(self):
        self.data, self.saves = {}, 0

    def save(self):
        self.saves += 1


class FakeClient:
    def __init__(self, fail=False, scheduled=False):
        self.posts, self.fail, self.scheduled = [], fail, scheduled

    def tiktok_connected(self):
        return 'velocemercato', 'Europe/Paris'

    def already_scheduled(self, media, tz):
        return self.scheduled

    def schedule(self, text, media, when, tz, draft):
        if self.fail:
            raise DeliveryError('Metricool a refusé (HTTP 500)')
        self.posts.append((text, media, draft))
        return str(len(self.posts))


def run(state, client, mode='essai', rows=None, convert=lambda s, o: 58, download=lambda u, p: None):
    return tk.process(state, rows or [row()], mode, {'foot'}, 1, lambda: client, download,
                      convert_fn=convert, host_fn=lambda p: 'https://cdn.jsdelivr.net/gh/x@' + SHA + '/' + p.name,
                      wait_fn=lambda u: None, now=NOW)


class TikTokTests(unittest.TestCase):
    def test_planned_block_uses_paris_and_no_night_post(self):
        morning = NOW.replace(hour=8, minute=0)
        self.assertEqual(tk.planned_block(morning).hour, 9)
        self.assertIsNone(tk.planned_block(NOW.replace(hour=2, minute=0)))

    def test_three_distinct_genres_once_per_block(self):
        state, client = FakeState(), FakeClient()
        now = NOW.replace(hour=19, minute=0)
        rows = [row('foot-edition-20261104-1800','foot','2026-11-04T18:30+01:00'),
                row('actus-edition-20261104-1800','actus','2026-11-04T18:30+01:00'),
                row('gaming-edition-20261104-1800','gaming','2026-11-04T18:30+01:00')]
        def invoke():
            return tk.process(state, rows, 'publier', {'foot','actus','gaming'}, 3, lambda: client,
                              lambda u,p: None, convert_fn=lambda a,b:58,
                              host_fn=lambda p:'https://cdn.jsdelivr.net/'+p.name,
                              wait_fn=lambda u:None, now=now, planned_at=now.replace(hour=20))
        self.assertEqual(len(invoke()), 3)
        self.assertEqual(invoke(), [])
        self.assertEqual(len(client.posts),3)

    def test_caption_single_line_with_site_and_ai_label(self):
        c = tk.caption(row())
        self.assertNotIn('\n', c)
        self.assertLessEqual(len(c), 2000)
        self.assertIn('velocemercato.fr', c)
        self.assertIn('généré par IA', c)

    def test_only_recent_allowed_universes_with_robot_files(self):
        rows = [row(), row('actus-edition-20261104-1900', 'actus'), row('foot-edition-20261101-2000', date='2026-11-01T20:00+01:00'),
                dict(row('foot-edition-20261104-1200'), verticale='https://exemple.com/x.mp4')]
        self.assertEqual([r['id'] for r in tk.candidates(rows, {'foot'}, NOW)], ['foot-edition-20261104-2000'])

    def test_essai_creates_private_draft_and_never_twice(self):
        state, client = FakeState(), FakeClient()
        rows = run(state, client)
        self.assertEqual(client.posts[0][2], True)  # brouillon
        self.assertEqual(rows[0]['statut'], 'brouillon')
        run(state, client)
        self.assertEqual(len(client.posts), 1)

    def test_publier_schedules_public_post(self):
        client = FakeClient()
        rows = run(FakeState(), client, mode='publier')
        self.assertEqual(client.posts[0][2], False)
        self.assertEqual(rows[0]['statut'], 'programme')

    def test_failure_before_sending_is_retried_at_most_three_times(self):
        state, client = FakeState(), FakeClient()
        def broken(s, o):
            raise DeliveryError('Vidéo refusée : son muet')
        for _ in range(5):
            run(state, client, convert=broken)
        self.assertEqual(state.data[tk.KEY]['foot-edition-20261104-2000']['essais'], 3)
        self.assertEqual(client.posts, [])

    def test_failure_after_sending_is_never_resent(self):
        state = FakeState()
        run(state, FakeClient(fail=True))
        self.assertEqual(state.data[tk.KEY]['foot-edition-20261104-2000']['status'], 'echec')
        client = FakeClient()
        self.assertEqual(run(state, client), [])
        self.assertEqual(client.posts, [])

    def test_already_scheduled_in_metricool_is_not_sent_again(self):
        state, client = FakeState(), FakeClient(scheduled=True)
        rows = run(state, client)
        self.assertEqual(client.posts, [])
        self.assertEqual(rows[0]['statut'], 'echec')

    def test_metricool_request_format(self):
        seen = []
        def opener(req, timeout):
            seen.append(req)
            return io.BytesIO(json.dumps({'data': {'id': 42}}).encode())
        c = tk.Metricool('jeton', '123', '456', opener=opener)
        ident = c.schedule('texte', 'https://cdn.jsdelivr.net/v.mp4', NOW, 'Europe/Paris', draft=True)
        req = seen[0]
        self.assertEqual(ident, '42')
        self.assertTrue(req.full_url.startswith('https://app.metricool.com/api/v2/scheduler/posts?'))
        self.assertIn('blogId=456', req.full_url)
        self.assertEqual(req.get_header('X-mc-auth'), 'jeton')
        body = json.loads(req.data)
        self.assertEqual(body['providers'], [{'network': 'tiktok'}])
        self.assertEqual((body['draft'], body['autoPublish'], body['tiktokData']['privacyOption']), (True, False, 'SELF_ONLY'))
        self.assertFalse(body['tiktokData']['autoAddMusic'])

    def test_missing_secrets_stop_everything(self):
        with self.assertRaises(DeliveryError):
            tk.Metricool('', '', '')

    def test_publication_requires_explicit_activation(self):
        with mock.patch.dict(os.environ, {'VM_AUTO_TIKTOK': ''}), mock.patch.object(sys, 'argv', ['x', '--state', '/tmp/none', '--mode', 'publier']):
            with self.assertRaises(DeliveryError):
                tk.main()

    def test_video_checks_on_real_encode(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out, mute = Path(tmp) / 's.mp4', Path(tmp) / 'o.mp4', Path(tmp) / 'm.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=size=720x1280:rate=30', '-f', 'lavfi',
                            '-i', 'sine=frequency=440', '-t', '4', '-c:v', 'libx264', '-c:a', 'aac', str(src)], check=True)
            self.assertEqual(tk.convert(src, out), 4)
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=size=1080x1920:rate=30', '-f', 'lavfi',
                            '-i', 'anullsrc', '-t', '4', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(mute)], check=True)
            with self.assertRaises(DeliveryError):
                tk.check_video(mute)


if __name__ == '__main__':
    unittest.main()
