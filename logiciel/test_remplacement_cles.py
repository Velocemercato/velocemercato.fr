# -*- coding: utf-8 -*-
import sqlite3
import tempfile
import unittest
from pathlib import Path
from dossiers_cles import Case, CaseStore
from remplacement_cles import Replacement, ReplacementStore, PHASES, report_html, NOTICE


class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.cs=CaseStore(Path(self.tmp.name)/'atelier.sqlite3')
        self.store=ReplacementStore(self.cs)
        self.case=self.cs.save(Case(marque='Renault',modele='Clio',annee='2018'))

    def tearDown(self):
        self.tmp.cleanup()

    def full_case(self):
        self.case.identite_propriete_verifiees=True
        self.case.mandat_signe=True
        self.cs.save(self.case)

    def flow(self,**kw):
        r=Replacement(dossier_id=self.case.id)
        for k,v in kw.items():setattr(r,k,v)
        return r

    def test_create_and_reopen(self):
        a=self.store.save(self.flow())
        b=ReplacementStore(self.cs).get(self.case.id)
        self.assertEqual(b.phase,PHASES[0])
        self.assertEqual(a.cree,b.cree)
        self.assertEqual(len(self.store.log(a.dossier_id)),1)

    def test_blocks_progress_without_verified_case(self):
        with self.assertRaisesRegex(ValueError,'justificatifs'):
            self.store.save(self.flow(phase=PHASES[1]))
        self.assertIsNone(self.store.get(self.case.id))

    def test_allows_admin_steps_after_checks(self):
        self.full_case()
        x=self.store.save(self.flow(phase=PHASES[2]))
        self.assertEqual(x.phase,PHASES[2])

    def test_blocks_key_programming_claim_without_approval(self):
        self.full_case()
        with self.assertRaisesRegex(ValueError,'habilitations'):
            self.store.save(self.flow(phase=PHASES[4]))
        with self.assertRaisesRegex(ValueError,'habilitations'):
            self.store.save(self.flow(phase=PHASES[4],controle_acces_professionnel=True))

    def test_approved_progress_is_declarative_only(self):
        self.full_case()
        r=self.flow(phase=PHASES[4],controle_acces_professionnel=True,
                    outil_constructeur_agree=True,provenance_cle_conforme=True)
        self.store.save(r)
        self.assertEqual(self.store.get(r.dossier_id).phase,PHASES[4])
        self.assertIn('aucune clé n’est programmée',NOTICE)

    def test_final_tests_required(self):
        self.full_case()
        r=self.flow(phase=PHASES[6],controle_acces_professionnel=True,
                    outil_constructeur_agree=True,provenance_cle_conforme=True)
        with self.assertRaisesRegex(ValueError,'essais finaux'):
            self.store.save(r)
        r.essais_declares=True
        self.store.save(r)
        self.assertEqual(self.store.get(self.case.id).phase,PHASES[6])

    def test_history_tracks_status_only(self):
        self.full_case()
        r=self.flow()
        self.store.save(r)
        r.phase=PHASES[1]
        r.note='Aucun détail client'
        self.store.save(r)
        self.store.save(r)
        h=self.store.log(self.case.id)
        self.assertEqual(len(h),2)
        self.assertEqual(h[-1][1:],(PHASES[0],PHASES[1]))
        self.assertNotIn('détail client',str(h))

    def test_no_orphan_when_parent_deleted(self):
        self.store.save(self.flow())
        self.cs.delete(self.case.id)
        self.assertIsNone(self.store.get(self.case.id))
        self.assertEqual(self.store.log(self.case.id),[])

    def test_invalid_options_and_truncated_text(self):
        with self.assertRaisesRegex(ValueError,'inconnue'):
            self.store.save(self.flow(type_cle='???'))
        with self.assertRaisesRegex(ValueError,'trop long'):
            self.store.save(self.flow(note='x'*501))

    def test_report_escapes_untrusted_text(self):
        r=self.store.save(self.flow(prestataire='<script>xx</script>',note='<img src=x onerror=evil()>'))
        rendered=report_html(r,self.store.log(self.case.id),'Renault','Clio')
        self.assertNotIn('<script>xx</script>',rendered)
        self.assertNotIn('<img src=x',rendered)
        self.assertIn('&lt;script&gt;',rendered)
        self.assertIn('SUIVI ADMINISTRATIF',rendered)

    def test_no_real_key_commands_are_offered(self):
        src=Path(__file__).with_name('remplacement_cles.py').read_text(encoding='utf-8')
        self.assertNotIn('import obd',src)
        self.assertNotIn('serial.Serial',src)
        self.assertNotIn('conn.query',src)


if __name__ == '__main__':
    unittest.main()
