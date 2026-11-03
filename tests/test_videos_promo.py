"""Vidéos promo VM : format 9:16, 15 s, son muet (aucune musique tierce), sources VM, calendrier contrôlé."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.vm_videos_promo as vp

ALLOWED = ('img/', 'vm-gaming/img/', 'mangas/assets/')


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate:format=duration',
                          '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class VideosPromoTests(unittest.TestCase):
    def test_videos_are_vertical_15s_and_silent(self):
        for c in vp.CONCEPTS:
            path = ROOT / 'assets/social/promo' / (c['id'] + '.mp4')
            self.assertTrue(path.is_file(), path)
            info = probe(path)
            video = next(s for s in info['streams'] if s['codec_type'] == 'video')
            self.assertEqual((video['codec_name'], video['width'], video['height'], video['r_frame_rate']), ('h264', 1080, 1920, '30/1'))
            self.assertAlmostEqual(float(info['format']['duration']), 15.0, delta=0.2)
            self.assertLess(path.stat().st_size, 8 * 1024 * 1024)
            vol = subprocess.run(['ffmpeg', '-i', str(path), '-af', 'volumedetect', '-vn', '-f', 'null', '-'],
                                 capture_output=True, text=True).stderr
            self.assertIn('max_volume: -91.0 dB', vol, c['id'])  # piste muette : aucune musique tierce

    def test_only_vm_sources(self):
        for c in vp.CONCEPTS:
            if c['illustration']:
                self.assertTrue(c['illustration'].startswith(ALLOWED), c['illustration'])
                self.assertTrue((ROOT / c['illustration']).is_file())

    def test_layout_stays_in_safe_zones_at_every_step(self):
        for c in vp.CONCEPTS:
            concept = vp.Concept(c)
            for t in (0.5, 2.0, 4.0, 7.0, 9.5, 12.0, 14.9):
                self.assertEqual(concept.frame(t).size, (1080, 1920))  # l'assertion interne vérifie la zone sûre

    def test_scheduled_only_through_video_field_of_video_days(self):
        cal = json.loads((ROOT / 'campagnes/calendrier.json').read_text(encoding='utf-8'))
        ids = {c['id'] for c in vp.CONCEPTS}
        for day in cal['jours']:
            for key, value in day.items():
                if key != 'video':
                    self.assertNotIn('assets/social/promo/', str(value), day['date'])
            if day.get('video'):
                self.assertTrue(day.get('reel') or day.get('youtube_short'), day['date'])
                self.assertIn(Path(day['video']).stem, ids)
                self.assertTrue((ROOT / day['video']).is_file())


if __name__ == '__main__':
    unittest.main()
