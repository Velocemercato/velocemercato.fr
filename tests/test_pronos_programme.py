"""Tests isolés : interdiction d'envoyer un vrai post depuis ces essais."""
import ast
import datetime as dt
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo


class DeliveryError(RuntimeError):
    pass


class FakeState:
    def __init__(self, confirmed=True):
        self.saves = 0
        self.data = {"meta_pronos_accuses": {}}
        if confirmed:
            self.data["meta_pronos_accuses"]["test/unique"] = {
                "status": "publie_confirme",
                "id": "112294796981981_1234",
                "url": "https://www.facebook.com/112294796981981_1234",
            }

    def save(self):
        self.saves += 1


def load_publish_slot(candidates=None, journal=()):
    source = Path(__file__).resolve().parents[1] / "tools" / "pronos_programme.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "publish_slot")
    graph = Mock()
    mock_verification = Mock(return_value="https://www.facebook.com/112294796981981_9876")
    env = {
        "os": os, "dt": dt, "UTC": dt.timezone.utc, "PARIS": ZoneInfo("Europe/Paris"),
        "SLOTS": {18: "actus"},
        "DeliveryError": DeliveryError,
        "page_access": lambda state: {
            "page_id": "112294796981981", "page_token": "TOKEN_TEST"},
        "candidates": lambda now, kind: candidates if candidates is not None else [{
            "key": "actus/id-a",
            "text": "Une actualité avec ses faits vérifiés.",
            "link": "https://velocemercato.fr/actus/"}],
        "safe_url": lambda url: str(url).startswith("https://"),
        "verify": mock_verification,
        "contenu_autorise": lambda item: "cote" not in item["text"],
        "empreinte": lambda item: item.get("empreinte", item["text"]).lower(),
        "deja_sur_la_page": lambda graph, token, page_id, now: [m.lower() for m in journal],
    }
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), "exec"), env)
    return env["publish_slot"], graph, mock_verification


class PublicationTests(unittest.TestCase):
    NOW = dt.datetime(2026, 10, 31, 17, 25, tzinfo=dt.timezone.utc)  # 18h25 Paris

    def test_off_does_not_post(self):
        fn, graph, _ = load_publish_slot()
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "false"}):
            self.assertFalse(fn(FakeState(), graph, self.NOW))
        graph.call.assert_not_called()

    def test_unconfirmed_test_does_not_post(self):
        fn, graph, _ = load_publish_slot()
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(confirmed=False), graph, self.NOW))
        graph.call.assert_not_called()

    def test_one_post_only_and_no_repeat_on_same_slot(self):
        fn, graph, verify = load_publish_slot()
        state = FakeState()
        graph.call.return_value = {"id": "112294796981981_9876"}
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertTrue(fn(state, graph, self.NOW))
            self.assertFalse(fn(state, graph, self.NOW))
        self.assertEqual(graph.call.call_count, 1)
        self.assertEqual(graph.call.call_args.args[1], "112294796981981/feed")
        self.assertEqual(verify.call_count, 1)
        self.assertEqual(state.data["meta_pronos_accuses"]["post/actus/id-a"]["status"], "publie_confirme")

    def test_failed_post_is_never_resent_blindly(self):
        fn, graph, _ = load_publish_slot()
        state = FakeState()
        graph.call.side_effect = DeliveryError("erreur fictive")
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            with self.assertRaises(DeliveryError):
                fn(state, graph, self.NOW)
            self.assertFalse(fn(state, graph, self.NOW))
        self.assertEqual(graph.call.call_count, 1)
        self.assertEqual(state.data["meta_pronos_accuses"]["post/actus/id-a"]["status"], "envoi")

    def test_special_10h40_is_separate_from_belfort_10h25(self):
        fn, graph, _ = load_publish_slot()
        state = FakeState()
        graph.call.return_value = {"id": "112294796981981_9876"}
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertTrue(fn(state, graph, dt.datetime(2026, 11, 2, 9, 40, tzinfo=dt.timezone.utc)))
        self.assertIn("creneau/2026-11-02/10-prono", state.data["meta_pronos_accuses"])

    def test_special_22h40_summary_slot(self):
        fn, graph, _ = load_publish_slot()
        state = FakeState()
        graph.call.return_value = {"id": "112294796981981_9876"}
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertTrue(fn(state, graph, dt.datetime(2026, 11, 2, 21, 40, tzinfo=dt.timezone.utc)))
        self.assertIn("creneau/2026-11-02/22h30-bilan", state.data["meta_pronos_accuses"])

    def test_random_40th_minute_is_not_an_extra_post(self):
        fn, graph, _ = load_publish_slot()
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(), graph, dt.datetime(2026, 11, 2, 17, 40, tzinfo=dt.timezone.utc)))
        graph.call.assert_not_called()

    def test_delayed_regular_cron_at_minute_46_still_posts_only_one(self):
        fn, graph, _ = load_publish_slot()
        graph.call.return_value = {"id": "112294796981981_9876"}
        state = FakeState()
        when = dt.datetime(2026, 11, 1, 17, 46, tzinfo=dt.timezone.utc)
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true",
                                     "VM_TRIGGER_CRON": "25 5-21 * * *"}):
            self.assertTrue(fn(state, graph, when))
            self.assertFalse(fn(state, graph, when))
        self.assertEqual(graph.call.call_count, 1)

    def test_special_cron_never_sends_regular_story_in_same_hour(self):
        fn, graph, _ = load_publish_slot()
        when = dt.datetime(2026, 11, 1, 17, 40, tzinfo=dt.timezone.utc)
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true",
                                     "VM_TRIGGER_CRON": "40 8-21 * * *"}):
            self.assertFalse(fn(FakeState(), graph, when))
        graph.call.assert_not_called()

    def test_no_new_content_does_not_post(self):
        fn, graph, _ = load_publish_slot(candidates=[])
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(), graph, self.NOW))
        graph.call.assert_not_called()

    def test_sujet_deja_present_sur_la_page_n_est_pas_republie(self):
        fn, graph, _ = load_publish_slot(journal=["📰 Une actualité avec ses faits vérifiés. Lire la suite"])
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(), graph, self.NOW))
        graph.call.assert_not_called()

    def test_contenu_de_pari_jamais_envoye(self):
        fn, graph, _ = load_publish_slot(candidates=[{
            "key": "actus/x", "text": "Combiné du jour, cote 1.95", "link": "https://velocemercato.fr/"}])
        with patch.dict(os.environ, {"VM_AUTO_PRONOS": "true"}):
            self.assertFalse(fn(FakeState(), graph, self.NOW))
        graph.call.assert_not_called()


class PromoEtGrilleTests(unittest.TestCase):
    def test_promo_calendrier_sans_prix_ni_pari_ni_vip(self):
        import datetime as dt
        from tools import pronos_programme as P
        themes = set()
        for day in range(28):
            now = dt.datetime(2026, 11, 2, 15, 0, tzinfo=dt.timezone.utc) + dt.timedelta(days=day)
            item = P.candidates(now, "promo")[0]
            self.assertTrue(P.safe_url(item["link"]))
            low = item["text"].lower()
            self.assertNotIn("€", item["text"])
            self.assertNotRegex(low, r"\bcote|combin|bookmaker|\bmise\b|vip|prono")
            self.assertIn(item["link"], item["text"])
            themes.add(item["key"].split("/")[-1])
        self.assertEqual(themes, set(P.PROMO_TEXTES))
        lundi = P.candidates(dt.datetime(2026, 11, 2, 15, tzinfo=dt.timezone.utc), "promo")[0]
        self.assertTrue(lundi["key"].endswith("/univers"))
        jeudi = P.candidates(dt.datetime(2026, 11, 5, 15, tzinfo=dt.timezone.utc), "promo")[0]
        self.assertTrue(jeudi["key"].endswith("/jt"))

    def test_annonces_pronos_informatives(self):
        from tools import pronos_programme as P
        for texte in P.ANNONCES_PRONOS:
            self.assertIn("18+ · Aucun résultat garanti · Joueurs Info Service : 09 74 75 13 13", texte)
            self.assertNotRegex(texte.lower(), r"\bcote\b(?! publiée)|vip|combin")
            self.assertIn("https://velocemercato.fr/pronos/", texte)

    def test_grille_foot_jt_et_promo(self):
        from tools import pronos_programme as P
        self.assertEqual(P.SLOTS[16], "promo")
        self.assertEqual(P.SLOTS[21], "jt")
        self.assertGreaterEqual(list(P.SLOTS.values()).count("foot"), 5)


class PagePrioritaireTests(unittest.TestCase):
    """Issue #162 : VM actus et pronos, Page prioritaire, sans aucun contenu de pari."""

    def test_filtre_pari(self):
        from tools import pronos_programme as P
        for texte in ("Notre combiné du jour", "Cote à 1,95", "Le prono VM", "Accès VIP", "Bankroll simulée",
                      "Ticket gagnant", "Les paris sportifs du soir", "https://velocemercato.fr/pronos/"):
            self.assertFalse(P.contenu_autorise({"key": "actus/x", "text": texte}), texte)
        self.assertTrue(P.contenu_autorise({"key": "actus/x", "text": "Mbappé marque, Côte d'Ivoire qualifiée"}))
        self.assertTrue(P.contenu_autorise({"key": "pronos-du-jour/2026-11-05", "text": P.ANNONCES_PRONOS[0]}))
        self.assertFalse(P.contenu_autorise({"key": "pronos-du-jour/2026-11-05", "text": "Cote 1,95 en VIP"}))

    def test_creneau_10h40_sans_pari_et_annonce_suspendue(self):
        import datetime as dt
        from tools import pronos_programme as P
        now = dt.datetime(2026, 11, 5, 9, 40, tzinfo=dt.timezone.utc)
        for item in P.candidates(now, "prono"):
            self.assertFalse(item["key"].startswith(("pronos-du-jour/", "agenda/", "prono/")), item["key"])
            self.assertTrue(P.contenu_autorise(item))
        self.assertFalse(hasattr(P, "preview_sourcee"))

    def test_multisport_source_et_lien_site(self):
        import datetime as dt
        from unittest.mock import patch as p
        from tools import pronos_programme as P
        data = {"sports": {"nba": [{"id": "nba-1-test", "titre": "Wembanyama brille - L'Équipe", "source": "L'Équipe",
                                    "url": "https://news.google.com/rss/articles/abc", "date": "2026-11-05T08:00:00+00:00"}],
                           "f1": [{"id": "f1-vieux", "titre": "Vieille info", "source": "X",
                                   "url": "https://x.fr/", "date": "2026-10-01T08:00:00+00:00"}]}}
        with p.object(P, "load_json", return_value=data):
            rows = P.multisport_candidates(dt.datetime(2026, 11, 5, 9, 40, tzinfo=dt.timezone.utc))
        self.assertEqual([r["key"] for r in rows], ["multisport/nba-1-test"])
        self.assertEqual(rows[0]["link"], "https://velocemercato.fr/multisport/")
        self.assertIn("Wembanyama brille\n", rows[0]["text"])
        self.assertIn("L'Équipe", rows[0]["text"])

    def test_journal_illisible_bloque_l_envoi(self):
        import datetime as dt
        from unittest.mock import Mock
        from tools import pronos_programme as P
        graph = Mock()
        graph.call.side_effect = RuntimeError("réseau")
        with self.assertRaises(P.DeliveryError):
            P.deja_sur_la_page(graph, "T", "112294796981981", dt.datetime(2026, 11, 5, tzinfo=dt.timezone.utc))
        graph.call.side_effect = None
        graph.call.return_value = {"data": [{"message": "Bonjour  Le Monde"}]}
        self.assertEqual(P.deja_sur_la_page(graph, "T", "112294796981981",
                                            dt.datetime(2026, 11, 5, tzinfo=dt.timezone.utc)), ["bonjour le monde"])
        self.assertEqual(graph.call.call_args.args[:2], ("GET", "112294796981981/published_posts"))

    def test_aucun_contenu_reel_du_jour_ne_parle_de_pari(self):
        import datetime as dt
        from tools import pronos_programme as P
        base = dt.datetime(2026, 11, 4, 6, 0, tzinfo=dt.timezone.utc)
        for hour, kind in P.SLOTS.items():
            for item in P.candidates(base.replace(hour=hour - 1), kind):
                if P.contenu_autorise(item):
                    self.assertNotIn("/pronos/", item["text"])
                    self.assertNotIn("RQPronos", item["text"])
