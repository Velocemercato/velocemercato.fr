"""Créneaux séparés, sources nouvelles et autorisation d'un seul original HD."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pastille_schedule as S
import update_emission as E
from tools import diffuser_jt as D

UTC = dt.timezone.utc
HD = {'format': {'duration': '165.2'}, 'streams': [
    {'codec_type': 'video', 'codec_name': 'h264', 'width': 1280, 'height': 720, 'avg_frame_rate': '24/1'}]}


class GridTests(unittest.TestCase):
    def test_each_requested_slot_is_due_once_in_summer_winter_and_dst(self):
        for day in ['2026-01-15', '2026-07-15', '2026-03-29', '2026-10-25']:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); tv = root / 'studio/tv'; tv.mkdir(parents=True)
                for universe, hours in S.EDITION_HOURS.items():
                    for hour in hours:
                        target = dt.datetime.fromisoformat(day).replace(hour=hour, tzinfo=S.PARIS)
                        now = target.astimezone(UTC) + dt.timedelta(minutes=7)
                        edition = S.due_edition(root, now, universe=universe)
                        self.assertEqual(edition['edition_at'], target.isoformat())
                        row = {**edition, 'format': 'edition', 'publie': True}
                        (tv / f'{universe}-{hour}.json').write_text(json.dumps(row))
                        self.assertIsNone(S.due_edition(root, now, universe=universe))
                        self.assertEqual(edition['source_end'], edition['edition_at'])

    def test_midnight_and_next_morning_have_adjacent_windows(self):
        midnight = dt.datetime(2026, 10, 25, 0, tzinfo=S.PARIS)
        a = S.edition_window('gaming', midnight)
        b = S.edition_window('gaming', midnight.replace(hour=10))
        self.assertEqual(a['source_start'], '2026-10-24T18:00:00+02:00')
        self.assertEqual(a['source_end'], b['source_start'])
        # Le changement d'heure ajoute une heure réelle, sans trou ni doublon.
        self.assertEqual(dt.datetime.fromisoformat(b['source_end']) - dt.datetime.fromisoformat(b['source_start']), dt.timedelta(hours=11))
        with tempfile.TemporaryDirectory() as tmp:
            edition = S.due_edition(tmp, midnight.astimezone(UTC) + dt.timedelta(minutes=7), 'gaming')
            self.assertTrue(edition['edition_at'].startswith('2026-10-25T00:00'))
            self.assertIsNone(S.due_edition(tmp, midnight.astimezone(UTC) - dt.timedelta(seconds=1), 'gaming'))

    def test_old_morning_and_evening_batch_does_not_block_new_times(self):
        now = dt.datetime(2026, 10, 23, 23, 35, tzinfo=S.PARIS)
        with tempfile.TemporaryDirectory() as tmp:
            tv = Path(tmp) / 'studio/tv'; tv.mkdir(parents=True)
            (tv / 'old.json').write_text(json.dumps({'univers': 'foot', 'format': 'edition', 'moment': 'soir', 'publie': True, 'date': now.date().isoformat()}))
            edition = S.due_edition(tmp, now, 'foot')
            self.assertIn('T23:00:', edition['edition_at'])
            (tv / 'new.json').write_text(json.dumps({**edition, 'format': 'edition', 'publie': False, 'hebergement': 'en_attente'}))
            self.assertIsNone(S.due_edition(tmp, now, 'foot'))
            self.assertIsNone(S.due_edition(tmp, now + dt.timedelta(hours=2), 'foot'))

    def test_articles_are_selected_in_open_closed_window_without_old_fallback(self):
        start = dt.datetime(2026, 10, 23, 7, tzinfo=S.PARIS)
        end = start.replace(hour=13)
        stamps = [start-dt.timedelta(seconds=1), start, start+dt.timedelta(seconds=1), end, end+dt.timedelta(seconds=1)]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'actus').mkdir()
            rows = [{'id': str(i), 'titre': 'Sujet sourcé', 'resume': 'Résumé', 'publishedAt': t.isoformat()} for i, t in enumerate(stamps)]
            (root / 'actus/news.json').write_text(json.dumps(rows))
            with patch.object(E, 'ROOT', root):
                selected = E.load_news('actus', 14, 8, start=start, end=end)
            self.assertEqual({r['id'] for r in selected}, {'2', '3'})

    def test_no_new_articles_never_calls_writer_or_recycles_old_news(self):
        now = dt.datetime.now(S.PARIS)
        target = now.replace(hour=13, minute=0, second=0, microsecond=0)
        # Figer une date de test, sans utiliser une heure future réelle.
        class Clock(dt.datetime):
            @classmethod
            def now(cls, tz=None): return target.replace(minute=20).astimezone(tz or UTC)
        with patch.object(E.dt, 'datetime', Clock), patch.dict(os.environ, {'VM_EDITION_AT':target.isoformat()}), \
             patch.object(E.D, 'piper_ready', return_value=True), patch.object(E.D.media, 'video_profile'), \
             patch.object(E, 'load_news', return_value=[]) as reader, patch.object(E, 'write_script') as writer:
            self.assertIsNone(E.make('actus', 'edition', 'midi'))
            self.assertEqual(reader.call_count, 1)
            self.assertEqual(set(reader.call_args.kwargs), {'start', 'end'})
            writer.assert_not_called()

    def fixture(self, root, *, universe='gaming', hour=0):
        target = dt.datetime(2026, 10, 25, hour, tzinfo=S.PARIS)
        edition = S.edition_window(universe, target)
        ident = f'{universe}-edition-{target:%Y%m%d-%H%M}'
        created = target.astimezone(UTC) + dt.timedelta(minutes=15)
        sources = [{'id': 'article-1', 'titre': 'Article sourcé', 'publishedAt': (target-dt.timedelta(minutes=1)).isoformat(), 'references': [{'nom':'Source','url':'https://example.org/article'}]}]
        row = {**edition, 'id':ident, 'format':'edition', 'titre':'Une actualité réelle', 'sources':sources, 'editorial_revision':'court-v1'}
        auth = {**edition, 'publish':True, 'created':created.isoformat(), 'date':target.date().isoformat(), 'format':'edition', 'unit':ident, 'run_id':'42'}
        (root / '_autorisation.json').write_text(json.dumps(auth))
        (root / (ident + '.json')).write_text(json.dumps(row))
        (root / (ident + '.mp4')).write_bytes(b'original-HD')
        return created, row, root / (ident + '.json')

    def test_single_hd_source_at_midnight_is_copied_and_category_stays_gaming(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); now, row, _ = self.fixture(root)
            with patch.object(D, 'probe', return_value=HD), patch.object(D, 'assemble') as assemble:
                manifest = D.prepare(root, root / 'out.mp4', now=now, expected_run='42')
            assemble.assert_not_called()
            self.assertEqual((root / 'out.mp4').read_bytes(), b'original-HD')
            self.assertEqual(manifest['universes'], ['gaming'])
            self.assertEqual(manifest['id'], row['id'])
            meta = D.youtube_metadata(manifest)
            self.assertIn('VM Gaming — JT 00 h', meta['snippet']['title'])
            self.assertEqual(meta['snippet']['categoryId'], '20')
            self.assertIn('https://example.org/article', meta['snippet']['description'])
            D.public_index(root / 'public.json', manifest, {'youtube': {'status':'private','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}})
            self.assertFalse((root / 'public.json').exists())
            D.public_index(root / 'public.json', manifest, {'youtube': {'status':'published','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}})
            published = json.loads((root / 'public.json').read_text())[0]
            self.assertEqual(published['edition_at'], manifest['edition_at'])
            self.assertEqual(published['universes'], ['gaming'])

    def test_tampered_or_out_of_window_article_is_rejected_before_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); now, row, file = self.fixture(root)
            row['sources'][0]['publishedAt'] = '2026-10-24T01:00:00+02:00'
            file.write_text(json.dumps(row))
            with self.assertRaisesRegex(D.DeliveryError, 'en dehors'):
                D.prepare(root, root / 'out.mp4', now=now, expected_run='42')
            self.assertFalse((root / 'out.mp4').exists())
            row['source_start'] = '2026-10-24T01:00:00+02:00';file.write_text(json.dumps(row))
            with self.assertRaisesRegex(D.DeliveryError, 'incohérente'):
                D.prepare(root, root / 'out.mp4', now=now, expected_run='42')

    def test_foot_evening_can_finish_after_midnight_without_becoming_next_day_jt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); now, row, _ = self.fixture(root, universe='foot', hour=23)
            with patch.object(D, 'probe', return_value=HD):
                manifest = D.prepare(root, root / 'out.mp4', now=now+dt.timedelta(hours=1), expected_run='42')
            self.assertEqual(manifest['date'], '2026-10-25')
            self.assertIn('Véloce Mercato — JT 23 h', D.youtube_metadata(manifest)['snippet']['title'])
            with self.assertRaisesRegex(D.DeliveryError, 'ancien'):
                D.prepare(root, root / 'out.mp4', now=now+dt.timedelta(hours=4), expected_run='42')

    def test_too_long_single_journal_is_not_cut_and_not_uploaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); now, _, _ = self.fixture(root)
            info = {**HD, 'format':{'duration':'301'}}
            with patch.object(D, 'probe', return_value=info), self.assertRaisesRegex(D.DeliveryError, 'cinq minutes'):
                D.prepare(root, root / 'out.mp4', now=now, expected_run='42')


if __name__ == '__main__': unittest.main(verbosity=2)
