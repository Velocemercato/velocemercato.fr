"""Tests VM Performance 2.0 (modules sans interface) : python -m unittest -v test_v2"""
import json
import tempfile
import unittest
from pathlib import Path

from atelier_store import Atelier, ValidationError, csv_safe
from electrique import DemoEV, OBDEV, formater, NON_FOURNI
from pdf_simple import lines_to_pdf
from stage1_e85 import Moteur, Etude, EtudeErreur, courbe, CHECKLIST_E85, score_checklist


class TestAtelier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.a = Atelier(Path(self.tmp.name) / "a.sqlite3")
        self.c = self.a.ajouter_client("Garage Test", "03 84 00 00 00", "test@example.fr")
        self.v = self.a.ajouter_vehicule(self.c, "Auto", "Marque", "Modèle", "2018", "Essence", "120000")

    def tearDown(self):
        self.tmp.cleanup()

    def test_validation(self):
        with self.assertRaises(ValidationError):
            self.a.ajouter_client("")
        with self.assertRaises(ValidationError):
            self.a.ajouter_client("X", email="pas-un-mail")
        with self.assertRaises(ValidationError):
            self.a.ajouter_vehicule(self.c, "Auto", "M", annee="1800")
        with self.assertRaises(ValidationError):
            self.a.ajouter_vehicule(self.c, "Avion", "M")
        with self.assertRaises(ValidationError):
            self.a.ajouter_intervention(self.v, "Diagnostic", "x", montant="-5")
        with self.assertRaises(ValidationError):
            self.a.ajouter_intervention(self.v, "Diagnostic", "x", date_="31/02/2026")
        with self.assertRaises(ValidationError):
            self.a.ajouter_recharge(self.v, soc_debut=80, soc_fin=20)

    def test_flux_complet_et_cascade(self):
        i = self.a.ajouter_intervention(self.v, "Diagnostic", "Lecture défauts", "49,90", "Devis", "21/10/2026")
        self.a.changer_statut(i, "Terminé")
        self.a.ajouter_recharge(self.v, None, 20, 80, 30.5, 12)
        rows = self.a.interventions()
        self.assertEqual(rows[0]["statut"], "Terminé")
        self.assertEqual(rows[0]["montant"], 49.9)
        self.assertEqual(rows[0]["date"], "2026-10-21")
        self.a.supprimer_client(self.c)
        self.assertEqual(self.a.interventions(), [])
        self.assertEqual(self.a.vehicules(), [])

    def test_export_csv_neutralise_formules(self):
        self.a.ajouter_intervention(self.v, "Autre", "=HYPERLINK(\"x\")")
        p = self.a.export_csv(Path(self.tmp.name) / "e.csv")
        self.assertIn("'=HYPERLINK", p.read_text(encoding="utf-8-sig"))
        self.assertEqual(csv_safe("+1"), "'+1")

    def test_sauvegarde_restauration(self):
        self.a.ajouter_intervention(self.v, "Diagnostic", "avant sauvegarde")
        sav = self.a.sauvegarder(Path(self.tmp.name) / "sav.sqlite3")
        self.a.supprimer_client(self.c)
        self.assertEqual(self.a.clients(), [])
        self.a.restaurer(sav)
        self.assertEqual(len(self.a.interventions()), 1)
        faux = Path(self.tmp.name) / "faux.sqlite3"
        faux.write_text("pas une base")
        with self.assertRaises(ValidationError):
            self.a.restaurer(faux)

    def test_rapport_pdf(self):
        self.a.ajouter_intervention(self.v, "Diagnostic", "Démo", demo=True)
        titre, lignes = self.a.rapport_lignes(self.v)
        self.assertTrue(any("DÉMONSTRATION" in l for l in lignes))
        pdf = lines_to_pdf(titre, lignes, Path(self.tmp.name) / "r.pdf", "VM Performance 2.0")
        data = pdf.read_bytes()
        self.assertTrue(data.startswith(b"%PDF-1.4") and data.rstrip().endswith(b"%%EOF"))


class TestStage1(unittest.TestCase):
    def test_courbe_coherente(self):
        m = Moteur(150, 250, 2000, 5500, 6500)
        pts = courbe(m)
        self.assertEqual(pts[0][0], 1000)
        self.assertAlmostEqual(max(t for _, t, _ in pts), 250, delta=1)
        pmax = max(p for _, _, p in pts)
        self.assertLessEqual(pmax, 151)
        self.assertGreater(pmax, 140)

    def test_validation_moteur(self):
        with self.assertRaises(EtudeErreur):
            courbe(Moteur(150, 250, 6000, 5500, 6500))
        with self.assertRaises(EtudeErreur):
            courbe(Moteur(5, 250))

    def test_etude_alertes_et_rapport(self):
        e = Etude("Test", Moteur(150, 250), Moteur(230, 400))
        self.assertTrue(any("sans source" in a for a in e.alertes()))
        self.assertTrue(any("très élevé" in a for a in e.alertes()))
        lignes = e.lignes_rapport()
        self.assertIn("ESTIMATION NON CERTIFIÉE", lignes[1])
        e2 = Etude.from_json(e.to_json())
        self.assertEqual(e2.cible.couple_nm, 400)
        self.assertEqual(score_checklist({"homologue": True}, CHECKLIST_E85), (1, len(CHECKLIST_E85)))


class FauxReponse:
    def __init__(self, v):
        self.value = v

    def is_null(self):
        return self.value is None


class FauxConn:
    def __init__(self, supportes):
        self.s = supportes

    def supports(self, cmd):
        return cmd in self.s

    def query(self, cmd):
        return FauxReponse(self.s[cmd])


class FauxOBD:
    class commands:
        HYBRID_BATTERY_REMAINING = "5B"
        CONTROL_MODULE_VOLTAGE = "42"
        AMBIANT_AIR_TEMP = "46"
        SPEED = "0D"
        DISTANCE_SINCE_DTC_CLEAR = "31"


class TestElectrique(unittest.TestCase):
    def test_non_fourni_si_absent(self):
        ev = OBDEV(FauxConn({"42": 13.9}), FauxOBD)
        m = ev.lire()
        self.assertEqual(m["tension_module"], 13.9)
        self.assertIsNone(m["batterie_hybride"])
        txt = formater(m, demo=False)
        self.assertTrue(any(NON_FOURNI in l for l in txt))
        self.assertFalse(any("[DÉMO]" in l for l in txt))

    def test_demo_marquee(self):
        txt = formater(DemoEV().lire(), demo=True)
        self.assertTrue(any("[DÉMO]" in l for l in txt))


if __name__ == "__main__":
    unittest.main()
