"""Préparer les JT avant les heures cibles et rattraper un déclenchement retardé."""
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pastille_schedule as schedule


class ScheduleTests(unittest.TestCase):
    def test_preparation_and_late_start_cover_summer_winter_and_dst(self):
        for date in ['2026-01-15', '2026-07-15', '2026-03-29', '2026-10-25']:
            for hour, moment in [(8, 'matin'), (12, 'midi'), (20, 'soir')]:
                target = dt.datetime.fromisoformat(date).replace(hour=hour, tzinfo=schedule.PARIS)
                for minutes in [-75, -45, 0, 35, 59]:
                    now = (target + dt.timedelta(minutes=minutes)).astimezone(dt.timezone.utc)
                    self.assertEqual(schedule.slot(now, schedule.JT_PREP_CRON), moment)
                for minutes in [-76, 60]:
                    now = (target + dt.timedelta(minutes=minutes)).astimezone(dt.timezone.utc)
                    self.assertEqual(schedule.slot(now, schedule.JT_PREP_CRON), '')
                for minutes in [0, 35, 59]:
                    now = (target + dt.timedelta(minutes=minutes)).astimezone(dt.timezone.utc)
                    self.assertEqual(schedule.slot(now, schedule.JT_CRON), moment)

    def test_cron_expression_includes_early_utc_slot_for_both_seasons(self):
        minute, hours, *_ = schedule.JT_PREP_CRON.split()
        for date in ['2026-01-15', '2026-07-15', '2026-03-29', '2026-10-25']:
            for hour in [8, 12, 20]:
                target = dt.datetime.fromisoformat(date).replace(hour=hour, tzinfo=schedule.PARIS)
                early = (target - dt.timedelta(minutes=75)).astimezone(dt.timezone.utc)
                self.assertEqual(int(minute), early.minute)
                self.assertIn(str(early.hour), hours.split(','))

    def test_complete_batch_is_not_regenerated_and_missing_actus_is_not_ignored(self):
        now = dt.datetime(2026, 10, 23, 7, 45, tzinfo=schedule.PARIS)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); tv = root / 'studio/tv'; tv.mkdir(parents=True)
            for universe in ['foot', 'actus', 'gaming']:
                row = {'univers': universe, 'format': 'edition', 'moment': 'matin',
                       'date': '2026-10-23T07:00:00+02:00', 'publie': True}
                (tv / (universe + '.json')).write_text(json.dumps(row))
            self.assertEqual(schedule.plan(root, now, schedule.JT_PREP_CRON), '')
            (tv / 'actus.json').unlink()
            self.assertEqual(schedule.plan(root, now, schedule.JT_PREP_CRON), 'matin')
            self.assertTrue(schedule.already_published(root, 'foot', 'edition', 'matin', now))
            self.assertFalse(schedule.already_published(root, 'actus', 'edition', 'matin', now))


if __name__ == '__main__': unittest.main(verbosity=2)
