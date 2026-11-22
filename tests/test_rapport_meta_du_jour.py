import datetime as dt
import unittest

from tools import rapport_meta_du_jour as report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 11, 22, 12, 55, tzinfo=report.PARIS)

    def test_editorial_slots_only_use_matching_account_day_and_network(self):
        date = self.now.replace(hour=8, minute=0).isoformat()
        wrong_date = (self.now - dt.timedelta(days=1)).replace(hour=12, minute=0).isoformat()
        state = {"meta": {
            f"editorial/slot/facebook/{date}": {"status": "publie_confirme"},
            f"editorial/slot/facebook/{wrong_date}": {"status": "publie_confirme"},
        }}
        self.assertEqual(report.editorial_slots(state, "meta", "facebook", self.now),
                         "8 h confirmé · 12 h sans confirmation · 20 h à venir")
        self.assertNotIn("confirmé", report.editorial_slots(state, "meta", "instagram", self.now))

    def test_editorial_slot_preserves_uncertain_send(self):
        start = self.now.replace(minute=0)
        state = {"meta_pronos_accuses": {
            f"editorial/slot/facebook/{start.isoformat()}": {"status": "a_verifier_sans_renvoi"},
        }}
        self.assertEqual(report.editorial_slots(state, "meta_pronos", "facebook", self.now),
                         "12 h à vérifier · 20 h à venir")
        self.assertIn("12 h ouvert", report.editorial_slots({}, "meta", "facebook", start))

    def test_summary_distinguishes_unavailable_from_confirmed_zero(self):
        last = self.now.replace(hour=12, minute=12)
        early = self.now.replace(hour=8, minute=11)
        url = "https://www.facebook.com/1384363904759072/posts/18"
        observations = {
            ("meta", "facebook"): {"followers": 15, "posts": [(early, "1", url), (last, "2", url)]},
            ("meta", "instagram"): {"followers": 0, "posts": []},
        }
        summary = report.format_summary({}, observations, self.now)
        self.assertEqual(summary.count("| Facebook ·"), 3)
        self.assertEqual(summary.count("| Instagram ·"), 2)
        self.assertIn(f"Facebook · Véloce Mercato | 15 | 2 | [12 h 12]({url})", summary)
        self.assertIn("Instagram · Véloce Mercato | 0 | 0 | —", summary)
        self.assertIn("Instagram · VM Univers | — | indisponible | —", summary)
