"""Validation hors ligne du programme quotidien : aucun appel API et aucun post."""
import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMES = tuple(sorted([f"{hour:02d}:00" for hour in range(7, 24)] + ["10:40", "22:40"]))


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
        self.assertEqual(tuple(meta), tuple(range(7, 24)))
        self.assertEqual(tuple(rq), tuple(range(7, 24)))
        self.assertEqual(tuple(h for h, topic in meta.items() if topic == "multisport"),
                         (10, 12, 15, 17, 21, 23))
        univers = assign("tools/publier_meta.py", "HEURES_UNIVERS_DEFAUT")
        self.assertEqual(univers, (9, 10, 12, 15, 17, 19, 21, 23))
        data = json.loads((ROOT / "programmes/grille_vm_quotidienne.json").read_text())
        for account, expected in (("meta", tuple(meta)), ("meta_pronos", tuple(rq)), ("meta_univers", univers)):
            self.assertEqual(tuple(int(slot["heure"][:2]) for slot in data["slots"]
                                   if slot["heure"].endswith(":00") and account in slot["pages_facebook"]), expected)

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
