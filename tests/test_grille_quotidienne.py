"""Validation hors ligne du programme quotidien : aucun appel API et aucun post."""
import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMES = ("07:00", "08:00", "10:00", "10:40", "11:00", "12:00", "13:00",
         "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "22:30", "23:00")


def assign(path, name):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    for item in tree.body:
        if isinstance(item, ast.Assign) and any(isinstance(x, ast.Name) and x.id == name for x in item.targets):
            return ast.literal_eval(item.value)
    raise AssertionError(name + " introuvable dans " + path)


class GrilleQuotidienneTests(unittest.TestCase):
    def test_grille_is_daily_and_has_exact_slots(self):
        data = json.loads((ROOT / "programmes/grille_vm_quotidienne.json").read_text())
        self.assertEqual(tuple(s["heure"] for s in data["slots"]), TIMES)
        self.assertEqual(data["timezone"], "Europe/Paris")
        self.assertEqual(data["recurrence"], "tous les jours, sans date de fin")
        self.assertFalse(data["instagram_rq_pronos"])

    def test_destination_separation(self):
        data = json.loads((ROOT / "programmes/grille_vm_quotidienne.json").read_text())
        for s in data["slots"]:
            self.assertTrue(set(s["pages_facebook"]) <= {"meta", "meta_univers", "meta_pronos"})
        self.assertEqual(data["instagram"], ["meta", "meta_univers"])

    def test_meta_hours_and_pronos_hours(self):
        meta = assign("tools/publier_meta.py", "SLOTS")
        rq = assign("tools/pronos_programme.py", "SLOTS")
        self.assertEqual(meta, {7: "actus", 8: "foot", 10: "multisport", 11: "foot",
                                12: "multisport", 13: "gaming", 15: "multisport", 16: "gaming",
                                17: "multisport", 18: "foot", 19: "actus", 20: "gaming",
                                21: "multisport", 22: "actus", 23: "multisport"})
        self.assertEqual(assign("tools/publier_meta.py", "HEURES_UNIVERS_DEFAUT"), (10, 15, 21))
        for hour in (7, 8, 10, 11, 12, 13, 15, 18, 19, 20, 21):
            self.assertIn(hour, rq)

    def test_scripts_parse(self):
        for path in ("tools/publier_meta.py", "tools/pronos_programme.py",
                     "tools/rapport_meta_du_jour.py", "tools/programme_vmunivers.py"):
            with self.subTest(path=path):
                ast.parse((ROOT / path).read_text(encoding="utf-8"))

    def test_audit_day_is_dynamic(self):
        code = (ROOT / "tools/rapport_meta_du_jour.py").read_text()
        self.assertIn("DAY = dt.datetime.now(PARIS).date()", code)
        self.assertNotIn("DAY = dt.date(2026, 11, 1)", code)


if __name__ == "__main__":
    unittest.main()
