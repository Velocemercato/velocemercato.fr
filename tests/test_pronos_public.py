"""Tests hors ligne : page publique d'actualités RQ Pronos, aucun envoi Meta."""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from tools.pronos_public import build, recent_articles, render, section_agenda, section_affiches_publiques, safe_url, PARIS


class PronosPublicTests(unittest.TestCase):
    NOW = dt.datetime(2026, 11, 1, 10, 0, tzinfo=dt.timezone.utc)

    def fixture(self, root, published="2026-11-01T09:00:00Z", title="Info sourcée"):
        (root / "actus").mkdir(exist_ok=True)
        (root / "actus/news.json").write_text(json.dumps([{
            "id": "news-test-001", "publishedAt": published,
            "titre": title, "resume": "Brève vérifiable",
            "sources": [{"nom": "Source test", "url": "https://example.org/report"}],
        }]), encoding="utf-8")

    def test_news_visible_in_static_html(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.fixture(root)
            text = render(root, self.NOW)
            self.assertIn("Info sourcée", text)
            self.assertIn("Brève vérifiable", text)
            self.assertIn("Source test", text)
            self.assertIn('href="https://www.facebook.com/share/1E6nH6RZzX/"', text)
            self.assertIn("18+", text)

    def test_html_escaped_and_false_stories_excluded(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.fixture(root, title="<script>danger</script>")
            text = render(root, self.NOW)
            self.assertIn("&lt;script&gt;", text)
            self.assertNotIn("<script>", text)
            self.fixture(root, published="2026-10-20T00:00:00Z")
            self.assertNotIn("news-test-001", render(root, self.NOW))
            self.fixture(root, published="2026-11-02T10:00:00Z")
            self.assertEqual(recent_articles(root, "actus/news.json", self.NOW), [])

    def test_unverified_match_not_in_agenda(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "programmes").mkdir()
            f = root / "programmes/avant_match_2026-11-01.json"
            f.write_text(json.dumps({"date_matchs": "2026-11-01", "matches": [{
                "affiche": "Faux match", "heure_paris": "15:00",
                "official_verified": False,
                "sources": [{"url": "https://ligue1.com/fr/articles/example"}],
            }]}))
            self.assertNotIn("Faux match", section_agenda(root, self.NOW))


    def selection(self, root, **over):
        data = {"valide": True, "valide_par": "Rédaction VM", "debut": "2026-11-01T06:00:00Z",
                "expire": "2026-11-02T06:00:00Z", "verifie_le": "2026-11-01T08:00:00Z",
                "combines": [{"titre": "Combiné test", "probabilite": "46 %", "cote": "1,96",
                              "selections": [{"match": "Équipe A – Équipe B", "heure_paris": "21 h",
                                              "marche": "Équipe A gagne", "cote": "1,40", "probabilite": "68 %",
                                              "type_estimation": "modèle",
                                              "source": {"nom": "Src", "url": "https://example.org/m"}}]}]}
        data.update(over)
        (root / "pronos").mkdir(exist_ok=True)
        (root / "pronos/selection.json").write_text(json.dumps(data), encoding="utf-8")

    def test_selection_only_when_validated_and_current(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.selection(root)
            text = render(root, self.NOW)
            self.assertIn("Combiné test", text)
            self.assertIn("interdits aux mineurs", text)
            self.selection(root, cote_max_public=1.30)
            self.assertNotIn("Combiné test", render(root, self.NOW))
            self.selection(root, cote_max_public=2)
            self.assertIn("Combiné test", render(root, self.NOW))
            self.selection(root, valide=False)
            self.assertNotIn("Combiné test", render(root, self.NOW))
            self.selection(root, valide_par="")
            self.assertNotIn("Combiné test", render(root, self.NOW))
            self.selection(root, expire="2026-11-01T09:00:00Z")
            self.assertNotIn("Combiné test", render(root, self.NOW))

    def test_claude_analysis_labelled_unvalidated(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.selection(root)
            data = json.loads((root / "pronos/selection.json").read_text(encoding="utf-8"))
            data.pop("valide"); data.pop("valide_par")
            data["publie_sans_validation"] = True
            data["combines"][0]["titre"] = "Combiné Claude"
            (root / "pronos/analyse-claude.json").write_text(json.dumps(data), encoding="utf-8")
            text = render(root, self.NOW)
            self.assertIn("Combiné Claude", text)
            self.assertIn("sans validation du propriétaire", text)
            data["publie_sans_validation"] = False
            (root / "pronos/analyse-claude.json").write_text(json.dumps(data), encoding="utf-8")
            self.assertNotIn("Combiné Claude", render(root, self.NOW))

    def test_acces_vip_mailto_only(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "pronos").mkdir()
            (root / "pronos/acces.json").write_text(json.dumps({"actif": True, "email": "vm@example.org",
                                                               "titre": "VIP", "texte": "Accès"}), encoding="utf-8")
            text = render(root, self.NOW)
            self.assertIn('id="acces-vip"', text)
            self.assertIn("mailto:vm@example.org", text)
            (root / "pronos/acces.json").write_text(json.dumps({"actif": False, "email": "vm@example.org"}), encoding="utf-8")
            self.assertNotIn('id="acces-vip"', render(root, self.NOW))

    def test_affiches_only_when_images_exist_and_window_active(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "pronos" / "affiches").mkdir(parents=True)
            payload = {
                "actif": True, "debut": "2026-11-01T00:00:00Z",
                "expire": "2026-11-02T00:00:00Z",
                "affiches": [{"titre": "Image publique", "fichier": "affiche-test.jpg"},
                             {"titre": "VIP interdit", "fichier": "../vip.png"}],
            }
            (root / "pronos/affiches-public.json").write_text(json.dumps(payload), encoding="utf-8")
            self.assertNotIn("Image publique", render(root, self.NOW))
            (root / "pronos/affiches/affiche-test.jpg").write_bytes(b"test")
            rendered = render(root, self.NOW)
            self.assertNotIn("Image publique", rendered)
            self.assertIn("Image publique", section_affiches_publiques(root, self.NOW))
            self.assertIn("/pronos/affiches/affiche-test.jpg", section_affiches_publiques(root, self.NOW))
            self.assertNotIn("VIP interdit", section_affiches_publiques(root, self.NOW))
            self.assertNotIn("Image publique", render(root, self.NOW + dt.timedelta(days=2)))

    def test_archive_extraction_for_public_gallery(self):
        import zipfile
        from tools.prepare_public_site import _prepare_affiches
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "pronos/affiches").mkdir(parents=True)
            (root / "pronos/index.html").write_text("<html><main>News</main></html>")
            (root / "conseils").mkdir(parents=True)
            (root / "conseils/index.html").write_text("<html><main><!-- VM_AFFICHES_DU_JOUR --></main></html>")
            config = {"actif": True, "debut": "2026-11-01T00:00:00Z",
                      "expire": "2026-11-02T00:00:00Z",
                      "affiches": [{"fichier": "jour-test.jpg", "titre": "Test"}]}
            (root / "pronos/affiches-public.json").write_text(json.dumps(config))
            with zipfile.ZipFile(root / "pronos/affiches/affiches-veloce-14-novembre-2026.zip", "w") as z:
                z.writestr("jour-test.png", b"\xff\xd8\xff" + b"data")
            _prepare_affiches(root)
            self.assertTrue((root / "pronos/affiches/jour-test.jpg").exists())
            self.assertNotIn("affiches-du-jour", (root / "pronos/index.html").read_text())
            self.assertNotIn("VM_AFFICHES_DU_JOUR", (root / "conseils/index.html").read_text())

    def test_build_idempotent(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            self.fixture(root)
            self.assertTrue(build(root, self.NOW))
            self.assertTrue((root / "pronos/index.html").is_file())
            self.assertFalse(build(root, self.NOW))

    def test_urls_and_timezones(self):
        self.assertTrue(safe_url("https://example.com/story"))
        self.assertFalse(safe_url("https://user:pass@example.com/story"))
        self.assertFalse(safe_url("javascript:alert(1)"))
        self.assertEqual(self.NOW.astimezone(PARIS).hour, 11)


if __name__ == "__main__":
    unittest.main()
