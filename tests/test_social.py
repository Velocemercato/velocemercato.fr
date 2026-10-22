import datetime as dt
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import social_publications as social
import pastille_media as media


class SocialTests(unittest.TestCase):
    def fixture(self, folder):
        root = Path(folder)
        for universe, route in [('foot', 'articles.json'), ('actus', 'actus/news.json'), ('gaming', 'vm-gaming/news.json')]:
            file = root / route
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps([
                {'id': universe + '-recent', 'titre': 'Essai sourcé @everyone', 'publishedAt': '2026-10-22T09:00:00Z',
                 'sources': [{'nom': 'Média de contrôle', 'url': 'https://example.org/source'}]},
                {'id': universe + '-futur', 'titre': 'Exclure le futur', 'publishedAt': '2026-10-23T09:00:00Z',
                 'sources': [{'nom': 'Source', 'url': 'https://example.org/source'}]},
                {'id': universe + '-ancien', 'titre': 'Exclure ancien', 'publishedAt': '2026-10-19T09:00:00Z',
                 'sources': [{'nom': 'Source', 'url': 'https://example.org/source'}]},
            ]))
        (root / 'a').mkdir()
        (root / 'a/foot-recent.html').write_text('article réel de contrôle')
        (root / 'studio/episodes').mkdir(parents=True)
        (root / 'studio/episodes/foot-jt.html').write_text('émission de contrôle')
        (root / 'studio/emissions.json').write_text(json.dumps([
            {'id': 'foot-jt', 'univers': 'foot', 'titre': 'JT technique', 'publie': True, 'date': '2026-10-22T09:30:00Z'},
            {'id': 'gaming-prive', 'univers': 'gaming', 'titre': 'Brouillon invisible', 'publie': False, 'date': '2026-10-22T09:30:00Z'},
        ]))
        (root / 'quiz.json').write_text(json.dumps({'id': 'quiz-22', 'date': '2026-10-22T08:00:00Z', 'questions': [{'q': 'Question de contrôle'}]}))
        return root

    def test_distinct_brands_fresh_sources_actual_links_no_invented_content(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.fixture(folder)
            rows = social.prepare(root, dt.datetime(2026, 10, 22, 10, tzinfo=dt.timezone.utc), 'midi')
            self.assertEqual([r['brand'] for r in rows], ['velocemercato', 'vmunivers'])
            self.assertIn('https://velocemercato.fr/a/foot-recent.html', rows[0]['content'])
            self.assertIn('https://vmunivers.fr/', rows[1]['content'])
            self.assertIn('https://velocemercato.fr/#quiz', rows[0]['content'])
            self.assertIn('/studio/episodes/foot-jt.html', rows[0]['content'])
            for row in rows:
                self.assertNotIn('futur', row['content'])
                self.assertNotIn('ancien', row['content'])
                self.assertNotIn('@everyone', row['content'])
                self.assertNotIn('Brouillon', row['content'])
                self.assertTrue(row['sources'])
                self.assertLessEqual(len(row['content']), 1950)
            state = {'receipts': {r['id']: dict(brand=r['brand'], items=r['items'], status='sent') for r in rows}}
            self.assertEqual(social.prepare(root, dt.datetime(2026, 10, 22, 18, tzinfo=dt.timezone.utc), 'soir', state), [])

    def test_schedule_handles_both_clock_changes(self):
        for date in ['2026-03-29', '2026-10-25', '2026-07-01', '2026-01-01']:
            for hour, moment in [(7, 'matin'), (12, 'midi'), (20, 'soir')]:
                now = dt.datetime.fromisoformat(date).replace(hour=hour, minute=15, tzinfo=social.PARIS)
                self.assertEqual(social.eligible_slot(now.astimezone(dt.timezone.utc)), moment)
                self.assertEqual(social.eligible_slot(now.replace(hour=hour + 1)), '')

    def test_receipt_is_persisted_before_http_and_retries_do_not_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.fixture(folder)
            rows = social.prepare(root, dt.datetime(2026, 10, 22, 10, tzinfo=dt.timezone.utc), 'midi')[:1]
            state_path = root / 'state.json'
            stages = []
            def persist():
                stages.append(json.loads(state_path.read_text())['receipts'][rows[0]['id']]['status'])
            def request(req, timeout):
                self.assertEqual(stages, ['sending'])
                self.assertEqual(json.loads(req.data)['allowed_mentions'], {'parse': []})
                return io.BytesIO(b'{"id":"12345"}')
            result = social.deliver(rows, state_path, 'https://discord.com/api/webhooks/123/test-access', persist, request)
            self.assertEqual(stages, ['sending', 'sent'])
            self.assertEqual(result[0]['status'], 'sent')
            with patch.object(social.urllib.request, 'urlopen', side_effect=AssertionError('Envoi dupliqué')):
                result = social.deliver(rows, state_path, 'https://discord.com/api/webhooks/123/test-access', persist, request)
            self.assertFalse(result[0]['attempted'])
            self.assertNotIn('test-access', state_path.read_text())

    def test_ambiguous_delivery_or_failed_persistence_never_blindly_retried(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.fixture(folder)
            rows = social.prepare(root, dt.datetime(2026, 10, 22, 10, tzinfo=dt.timezone.utc), 'midi')[:1]
            state_path = root / 'state.json'
            def fail(*args, **kwargs):
                raise TimeoutError()
            result = social.deliver(rows, state_path, 'https://discord.com/api/webhooks/123/test-access', opener=fail)
            self.assertEqual(result[0]['status'], 'uncertain')
            result = social.deliver(rows, state_path, 'https://discord.com/api/webhooks/123/test-access', opener=fail)
            self.assertFalse(result[0]['attempted'])
            state_path.unlink()
            with self.assertRaises(TimeoutError), patch.object(social.urllib.request, 'build_opener') as http:
                social.deliver(rows, state_path, 'https://discord.com/api/webhooks/123/test-access', persist=fail)
                http.return_value.open.assert_not_called()

    def test_invalid_destination_is_never_contacted(self):
        with patch.object(social.urllib.request, 'build_opener') as http:
            with self.assertRaises(ValueError):
                social.deliver([], Path('/tmp/unused.json'), 'https://example.org/webhook')
            http.assert_not_called()

    def test_production_profile_and_cdn_retention_preserve_current_files(self):
        with patch.dict('os.environ', {'VM_PUBLISH': '1', 'GITHUB_ACTIONS': 'true', 'GITHUB_REF': 'refs/heads/main', 'VM_VIDEO_PROFILE': 'auto'}):
            self.assertEqual(media.video_profile(), 'cdn')
            with patch.dict('os.environ', {'VM_VIDEO_PROFILE': 'hd'}):
                with self.assertRaises(RuntimeError):
                    media.video_profile()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'foot-20261022-0700.mp4').write_bytes(b'a' * 70)
            (root / 'foot-20261022-1200.mp4').write_bytes(b'b' * 70)
            (root / 'foot-20261022-2000.mp4').write_bytes(b'c' * 70)
            with patch.object(media, 'CDN_PACKAGE_BYTES', 150):
                media.prune_cdn_package(root, 'foot-20261022-2000.mp4')
            self.assertFalse((root / 'foot-20261022-0700.mp4').exists())
            self.assertTrue((root / 'foot-20261022-2000.mp4').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
