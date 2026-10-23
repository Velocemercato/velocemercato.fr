"""Une limite de transport conserve les rendus, sans masquer une panne réelle."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import update_emission as emission
import pastille_media as media


class RecoveryTests(unittest.TestCase):
    def test_refresh_is_explicit_and_identifies_the_new_editorial_version(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.produce(root,100)
            with patch.object(emission,'already_published',return_value=True),patch.dict(os.environ,{'VM_REFRESH_EDITION':'0'}):
                self.assertIsNone(emission.make('actus','edition','midi'))
            with patch.object(emission,'already_published',return_value=True),patch.dict(os.environ,{'VM_REFRESH_EDITION':'1'}),patch.object(emission,'publish',return_value='a'*40):
                entry=emission.make('actus','edition','midi')
            self.assertEqual(entry['editorial_revision'],'court-v1')
            self.assertTrue(entry['publie'])

    def produce(self, root, size):
        (root / 'studio/debats').mkdir(parents=True)
        config = root / 'studio/debats/config.json'
        config.write_text('{"publication_auto": true}')
        self.enterContext(patch.object(emission, 'ROOT', root))
        self.enterContext(patch.object(emission, 'CONFIG', config))
        self.enterContext(patch.object(emission, 'already_published', return_value=False))
        self.enterContext(patch.object(emission.D, 'piper_ready', return_value=True))
        self.enterContext(patch.object(emission, 'load_news', return_value=[{'titre': 'Test'}] * 4))
        self.enterContext(patch.object(emission, 'write_script', return_value={
            'titre': 'Contrôle technique sans publication', 'accroche': 'Test',
            'repliques': [('PRESENTATEUR', 'Une phrase de contrôle sans fait inventé.')] * 35}))
        env = {'VM_PUBLISH': '1', 'GITHUB_ACTIONS': 'true', 'GITHUB_REF': 'refs/heads/main',
               'VM_VIDEO_PROFILE': 'cdn', 'VM_KEEP_HD_MASTER': '1'}
        self.enterContext(patch.dict(os.environ, env))

        def build(script, out):
            # Fichiers de contrôle clairsemés : aucun upload et aucun appel TTS.
            for suffix in ('.mp4', '.m4a', '.jpg'):
                with out.with_suffix(suffix).open('wb') as stream:
                    stream.truncate(size if suffix == '.mp4' else 20)
            if os.getenv('VM_KEEP_HD_MASTER') == '1':
                masters = root / 'studio/tmp/masters'; masters.mkdir(parents=True, exist_ok=True)
                (masters / out.name).write_bytes(b'original-hd-test')
            return 600, ['piper']

        self.enterContext(patch.object(emission.D, 'build_video', side_effect=build))
        return self.enterContext(patch.object(emission, 'rebuild_list'))

    def test_oversized_render_is_recoverable_and_hd_metadata_survives(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); rebuild = self.produce(root, media.CDN_MAX_BYTES)
            listing = root / 'studio/emissions.json'; listing.write_text('[{"id":"ancienne-emission"}]')
            with patch.object(emission, 'git') as git:
                entry = emission.make('actus', 'edition', 'matin')
            git.assert_not_called(); rebuild.assert_not_called()
            self.assertIs(entry['publie'], False)
            self.assertEqual(entry['hebergement'], 'en_attente')
            self.assertEqual(json.loads(listing.read_text()), [{'id': 'ancienne-emission'}])
            pending = root / 'studio/tmp/a-heberger'
            for suffix in ('.mp4', '.m4a', '.jpg', '.json'):
                self.assertTrue((pending / (entry['id'] + suffix)).is_file())
            data = json.loads((pending / (entry['id'] + '.json')).read_text())
            self.assertEqual(len(data['script']['repliques']), 35)
            self.assertNotIn('video', data['emission'])
            master = root / 'studio/tmp/masters' / (entry['id'] + '.json')
            self.assertEqual(json.loads(master.read_text())['id'], entry['id'])
            self.assertTrue(master.with_suffix('.mp4').is_file())
            self.assertFalse((root / 'studio/tv').exists())

    def test_network_publication_failure_stays_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); rebuild = self.produce(root, 100)
            with patch.object(emission, 'publish', side_effect=RuntimeError('Git indisponible')):
                with self.assertRaisesRegex(RuntimeError, 'Git indisponible'):
                    emission.make('actus', 'edition', 'matin')
            rebuild.assert_not_called()
            self.assertEqual(len(list((root / 'studio/tmp').glob('*.mp4'))), 1)
            self.assertEqual(list((root / 'studio/tmp').glob('a-heberger/*.json')), [])

    def test_no_connected_host_keeps_a_download_without_claiming_hd(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); rebuild = self.produce(root, media.CDN_MAX_BYTES)
            with patch.dict(os.environ, {'VM_KEEP_HD_MASTER': '0'}), patch.object(emission, 'git') as git:
                entry = emission.make('actus', 'edition', 'matin')
            git.assert_not_called(); rebuild.assert_not_called()
            self.assertIs(entry['publie'], False)
            self.assertTrue((root / 'studio/tmp/a-heberger' / entry['fichier']).is_file())
            self.assertFalse((root / 'studio/tmp/masters').exists())

    def test_successful_cdn_upload_publishes_only_after_confirmation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); rebuild = self.produce(root, 100)
            with patch.object(emission, 'publish', return_value='a' * 40) as upload:
                entry = emission.make('actus', 'edition', 'matin')
            upload.assert_called_once(); rebuild.assert_called_once()
            self.assertIs(entry['publie'], True)
            stored = json.loads((root / 'studio/tv' / (entry['id'] + '.json')).read_text())
            self.assertEqual(stored['media_sha'], 'a' * 40)
            self.assertIs(stored['publie'], True)
            master = root / 'studio/tmp/masters' / (entry['id'] + '.json')
            self.assertIs(json.loads(master.read_text())['publie'], True)
            self.assertFalse((root / 'studio/tmp' / entry['fichier']).exists())
            self.assertTrue((root / 'studio/episodes/posters' / (entry['id'] + '.jpg')).is_file())

    def test_batch_summary_distinguishes_published_deferred_and_failed(self):
        with tempfile.TemporaryDirectory() as folder:
            summary = Path(folder) / 'summary.md'
            replies = [{'publie': True}, {'publie': False, 'hebergement': 'en_attente'}, None]
            with patch.object(sys, 'argv', ['update_emission.py', 'plan', 'matin']), \
                 patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), \
                 patch.object(emission, 'make', side_effect=replies) as make:
                emission.main()
                self.assertEqual(make.call_count, 3)
            text = summary.read_text()
            self.assertIn('| foot | edition / matin | publiée sur le site |', text)
            self.assertIn('| actus | edition / matin | conservée, hébergement requis |', text)
            self.assertIn('| gaming | edition / matin | aucune nouvelle émission |', text)
            with patch.object(sys, 'argv', ['update_emission.py', 'plan', 'matin']), \
                 patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), \
                 patch.object(emission, 'make', side_effect=[RuntimeError('Panne réelle'), None, None]):
                with self.assertRaises(SystemExit) as stopped: emission.main()
            self.assertEqual(stopped.exception.code, 1)
            self.assertIn('échec : RuntimeError', summary.read_text())


if __name__ == '__main__': unittest.main(verbosity=2)
