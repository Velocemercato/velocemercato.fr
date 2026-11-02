"""Fraîcheur : chaque matin à 5 h (Paris), ce qui date de la veille s'efface, sans jamais être republié."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import vm_fraicheur as vf  # noqa: E402
import update_foot_amateur as fa  # noqa: E402


class DebutJournee(unittest.TestCase):
    def test_bascule_a_5h_heure_de_paris(self):
        avant = vf.debut_journee(vf.lire_date('2026-11-03T03:59:00Z'))  # 4 h 59 à Paris (hiver)
        apres = vf.debut_journee(vf.lire_date('2026-11-03T04:00:00Z'))  # 5 h 00 à Paris
        self.assertEqual(avant.isoformat(), '2026-11-02T05:00:00+01:00')
        self.assertEqual(apres.isoformat(), '2026-11-03T05:00:00+01:00')

    def test_heure_d_ete(self):
        self.assertEqual(vf.debut_journee(vf.lire_date('2026-07-01T03:30:00Z')).isoformat(), '2026-07-01T05:00:00+02:00')

    def test_du_jour_retire_la_veille_et_les_lignes_sans_date(self):
        now = vf.lire_date('2026-11-03T10:00:00Z')
        rows = [{'publishedAt': '2026-11-03T05:00:00Z'}, {'publishedAt': '2026-11-02T22:00:00Z'}, {'titre': 'sans date'}]
        self.assertEqual(vf.du_jour(rows, now=now), [rows[0]])

    def test_mise_en_ligne_du_jour_sur_une_actu_de_la_veille(self):
        now = vf.lire_date('2026-11-03T10:00:00Z')
        row = {'publishedAt': '2026-11-02T21:00:00Z', 'createdAt': '2026-11-03T06:00:00Z'}
        self.assertEqual(vf.du_jour([row], ('createdAt', 'publishedAt'), now), [row])


class Menage(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / 'belfort').mkdir()
        (self.dir / 'multisport').mkdir()
        self.now = vf.lire_date('2026-11-03T05:00:00Z')
        art = lambda i, d: {'id': f'a{i}', 'publishedAt': d, 'createdAt': d, 'titre': f'Titre {i}',
                            'sources': [{'nom': 'X', 'url': f'https://ex.fr/{i}?utm=1'}]}
        (self.dir / 'articles.json').write_text(json.dumps([art(1, '2026-11-03T04:30:00Z'), art(2, '2026-11-02T20:00:00Z')]))
        (self.dir / 'belfort/actus.json').write_text(json.dumps({'maj': 'x', 'titres': [{'d': '2026-11-02T08:00:00Z'}, {'d': '2026-11-03T04:10:00Z'}]}))
        (self.dir / 'multisport/actualites.json').write_text(json.dumps({'fenetreJours': 7, 'sports': {'nba': [{'date': '2026-11-01T08:00:00+00:00'}]}}))
        (self.dir / 'videos.json').write_text('{pas du json')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_menage_complet_et_idempotent(self):
        total = vf.menage(self.dir, self.now)
        self.assertEqual(total, 3)
        self.assertEqual([a['id'] for a in json.loads((self.dir / 'articles.json').read_text())], ['a1'])
        self.assertEqual(len(json.loads((self.dir / 'belfort/actus.json').read_text())['titres']), 1)
        ms = json.loads((self.dir / 'multisport/actualites.json').read_text())
        self.assertEqual((ms['fenetreJours'], ms['sports']['nba']), (1, []))
        # Un fichier illisible n'est jamais écrasé.
        self.assertEqual((self.dir / 'videos.json').read_text(), '{pas du json')
        memoire = json.loads((self.dir / 'deja-publies.json').read_text())
        self.assertEqual(memoire[0]['urls'], ['https://ex.fr/2'])
        self.assertEqual(vf.menage(self.dir, self.now), 0)


class FootAmateur(unittest.TestCase):
    def test_tri_par_niveau_et_region(self):
        self.assertEqual(fa.niveau('N3 : Belfort s’impose'), 'NATIONAL')
        self.assertEqual(fa.niveau('District : les résultats du D2'), 'DISTRICT')
        self.assertEqual(fa.niveau('Coupe de France : 7e tour'), 'COUPE')
        self.assertEqual(fa.region_de('R1 : Brest et Quimper dos à dos'), 'BRE')
        self.assertEqual(fa.region_de('Un titre sans ville'), 'FR')

    def test_foot_pro_et_autres_sports_ecartes(self):
        ok = lambda t: fa.garder({'t': t, 'u': 'https://ex.fr', 'd': 1, 's': ''})
        self.assertTrue(ok('Régional 1 : le derby tourne court'))
        self.assertFalse(ok('Ligue 1 : le PSG s’impose'))
        self.assertFalse(ok('Rugby amateur : Fédérale 1'))
        self.assertFalse(ok('Football : pronostics du week-end'))

    def test_titre_nettoye_du_nom_du_media(self):
        row = {'t': 'N2 : Bourges accroche Fleury - Le Berry', 'u': 'https://ex.fr', 's': 'Le Berry',
               'd': vf.lire_date('2026-11-03T08:00:00Z')}
        self.assertEqual(fa.ligne(row, 'CVL', 'x')['t'], 'N2 : Bourges accroche Fleury')


if __name__ == '__main__':
    unittest.main()
