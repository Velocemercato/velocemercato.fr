"""Bibliothèque VF : aucune VF ni disponibilité inventée, preuves exigées, rien de publié sans vérification."""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import verifier_vf as V  # noqa: E402
from tools import bibliotheque_vf_candidats as C  # noqa: E402

NOW = dt.datetime(2026, 11, 5, 5, 0, tzinfo=dt.timezone.utc)
CHAINES = {
    "officielle": {"nom": "CODE LYOKO OFFICIEL", "ids": ["UCQiZ4G8PHqUIji3c74jBiTA"], "noms": ["CODE LYOKO OFFICIEL"],
                   "francophone": True},
    "par_nom": {"nom": "La chaîne Mangas", "noms": ["Mangas"]},
    "inconnue": {"nom": "?", "noms": []},
}


def page(channel="UCQiZ4G8PHqUIji3c74jBiTA", auteur="CODE LYOKO OFFICIEL 🇫🇷", titre="CODE LYOKO - SAISON 1",
         pays=("FR", "BE"), pistes=(), statut="OK"):
    player = {"videoDetails": {"channelId": channel, "author": auteur, "title": titre, "lengthSeconds": "6500",
                               "shortDescription": "Épisodes complets"},
              "playabilityStatus": {"status": statut},
              "microformat": {"playerMicroformatRenderer": {"availableCountries": list(pays), "isFamilySafe": True,
                                                            "uploadDate": "2024-01-01"}},
              "streamingData": {"adaptiveFormats": [{"height": 1080}, {"height": 480}] +
                                [{"audioTrack": {"id": p}} for p in pistes]}}
    return "<script>var ytInitialPlayerResponse = " + json.dumps(player) + ";var x=1;</script>"


def faux_get(oembed_code=200, html=None, titre="CODE LYOKO - SAISON 1", auteur="CODE LYOKO OFFICIEL 🇫🇷"):
    def get(url, timeout=20):
        if "oembed" in url:
            return oembed_code, json.dumps({"title": titre, "author_name": auteur,
                                            "author_url": "https://www.youtube.com/@codelyokoofficiel7410"})
        return (200, html) if html is not None else (200, page())
    return get


def lien(chaine="officielle", statut="candidat"):
    return {"id": "x", "oeuvre": "code-lyoko", "titre": "Code Lyoko", "video": "1ObJPU0BQBg",
            "chaine": chaine, "statut": statut, "page": None}


class VerificationTests(unittest.TestCase):
    def test_chaine_officielle_francophone_france_et_lecture_ok(self):
        r = V.verifier(lien(), CHAINES, faux_get(), NOW)
        self.assertEqual(r["statut"], "verifie")
        self.assertEqual(r["audio"], "VF_CONFIRME")
        self.assertEqual(r["preuve_chaine"], "id")
        self.assertEqual(r["qualite"], "1080p")
        self.assertTrue(r["embed_autorise"])
        self.assertEqual(r["lien_type"], "LECTEUR_OFFICIEL")
        self.assertEqual(r["date_verification"], "2026-11-05T05:00:00+00:00")

    def test_titre_francais_ne_suffit_pas_sans_chaine_prouvee(self):
        get = faux_get(html=page(channel="UCautre", auteur="Fan 2000", titre="Épisode complet en français"),
                       titre="Épisode complet en français", auteur="Fan 2000")
        r = V.verifier(lien("inconnue"), CHAINES, get, NOW)
        self.assertEqual(r["statut"], "candidat")
        self.assertEqual(r["motif"], "chaîne officielle non prouvée")
        self.assertNotEqual(r["audio"], "VF_CONFIRME")

    def test_vostfr_jamais_presente_comme_vf(self):
        get = faux_get(html=page(titre="Épisode 1 VOSTFR"), titre="Épisode 1 VOSTFR")
        r = V.verifier(lien(), CHAINES, get, NOW)
        self.assertEqual(r["audio"], "PAS_DE_VF")
        self.assertEqual(r["statut"], "candidat")

    def test_piste_audio_francaise_declaree(self):
        chaines = {"officielle": dict(CHAINES["officielle"], francophone=False)}
        get = faux_get(html=page(pistes=("fr.4", "ja.3"), titre="Episode 1"), titre="Episode 1")
        r = V.verifier(lien(), chaines, get, NOW)
        self.assertEqual(r["audio"], "VF_CONFIRME")
        self.assertIn("fr.4", r["preuve_audio"])

    def test_sans_preuve_audio_reste_a_verifier(self):
        chaines = {"officielle": dict(CHAINES["officielle"], francophone=False)}
        r = V.verifier(lien(), chaines, faux_get(), NOW)
        self.assertEqual(r["audio"], "VF_A_VERIFIER")
        self.assertEqual(r["statut"], "candidat")

    def test_france_non_autorisee(self):
        r = V.verifier(lien(), CHAINES, faux_get(html=page(pays=("US",))), NOW)
        self.assertFalse(r["accessible_france"])
        self.assertEqual(r["statut"], "candidat")

    def test_integration_interdite_donne_un_lien_direct(self):
        r = V.verifier(lien(), CHAINES, faux_get(oembed_code=401), NOW)
        self.assertFalse(r["embed_autorise"])
        self.assertEqual(r["lien_type"], "LIEN_DIFFUSEUR")

    def test_video_supprimee_page_publiee_signalee(self):
        get = faux_get(oembed_code=404, html="<html>indisponible</html>")
        r = V.verifier(lien(statut="publie"), CHAINES, get, NOW)
        self.assertEqual(r["statut"], "retire")
        self.assertIn("À RETIRER", r["alerte"])

    def test_preuve_par_nom_seul_reste_candidat(self):
        get = faux_get(html=page(channel="UCinconnu", auteur="La chaîne Mangas"), auteur="La chaîne Mangas")
        r = V.verifier(lien("par_nom"), CHAINES, get, NOW)
        self.assertEqual(r["preuve_chaine"], "nom")
        self.assertEqual(r["statut"], "candidat")

    def test_reseau_bloque_aucune_affirmation(self):
        r = V.verifier(lien(), CHAINES, lambda url, timeout=20: (0, ""), NOW)
        self.assertEqual(r["statut"], "non_controle")
        self.assertIsNone(r["accessible_france"])
        r = V.verifier(lien(statut="publie"), CHAINES, lambda url, timeout=20: (0, ""), NOW)
        self.assertIsNone(r["alerte"])

    def test_identifiant_invalide(self):
        r = V.verifier(dict(lien(), video="../../x"), CHAINES, faux_get(), NOW)
        self.assertEqual(r["statut"], "retire")


class CatalogueTests(unittest.TestCase):
    def test_candidats_jamais_marques_vf_ni_verifies(self):
        data = json.loads((ROOT / "bibliotheque-vf" / "candidats.json").read_text(encoding="utf-8"))
        self.assertGreater(data["total"], 400)
        self.assertEqual(data["total"], len(data["oeuvres"]))
        ids = [o["id"] for o in data["oeuvres"]]
        self.assertEqual(len(ids), len(set(ids)))
        for o in data["oeuvres"]:
            self.assertEqual(o["statut"], "candidat")
            self.assertEqual(o["audio"], "VF_A_VERIFIER")
            self.assertIsNone(o["url_officielle"])
        adultes = {o["titre_fr"] for o in data["oeuvres"] if o["public"] == "adulte"}
        self.assertEqual(adultes, {"South Park", "Les Griffin", "American Dad!", "Rick et Morty"})

    def test_candidats_regeneres_identiques(self):
        dossier = (ROOT / "docs" / "DOSSIER_BIBLIOTHEQUE_VF.md").read_text(encoding="utf-8")
        data = json.loads((ROOT / "bibliotheque-vf" / "candidats.json").read_text(encoding="utf-8"))
        self.assertEqual(C.construire(dossier), data["oeuvres"])

    def test_liens_coherents(self):
        data = json.loads((ROOT / "bibliotheque-vf" / "liens.json").read_text(encoding="utf-8"))
        oeuvres = {o["id"] for o in json.loads(
            (ROOT / "bibliotheque-vf" / "candidats.json").read_text(encoding="utf-8"))["oeuvres"]}
        vus = set()
        for l in data["liens"]:
            self.assertRegex(l["video"], r"^[A-Za-z0-9_-]{11}$")
            self.assertIn(l["chaine"], data["chaines"])
            self.assertIn(l["oeuvre"], oeuvres)
            self.assertNotIn(l["video"], vus)
            vus.add(l["video"])
            if l["statut"] == "publie":
                self.assertTrue((ROOT / l["page"].lstrip("/")).is_file(), l["page"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
