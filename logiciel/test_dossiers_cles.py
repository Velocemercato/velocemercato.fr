import tempfile
import unittest
from pathlib import Path
from dossiers_cles import Case, CaseStore, export_csv, to_html, STAGES, ISSUES, csv_safe

class CaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = CaseStore(Path(self.tmp.name) / 'dossiers.sqlite3')

    def tearDown(self):
        self.tmp.cleanup()

    def case(self, **updates):
        c = Case(marque='Renault', modele='Clio', annee='2018', motif=ISSUES[0])
        for k,v in updates.items():
            setattr(c,k,v)
        return c

    def test_create_update_persistence(self):
        c = self.store.save(self.case())
        self.assertTrue(c.id.startswith('VM-'))
        self.assertEqual(self.store.get(c.id).modele, 'Clio')
        created = c.cree
        c.notes = 'Intervention à planifier'
        self.store.save(c)
        self.assertEqual(self.store.get(c.id).notes, 'Intervention à planifier')
        self.assertEqual(created, self.store.get(c.id).cree)
        self.assertEqual(len(self.store.list()), 1)

    def test_must_verify_before_advanced_stage(self):
        c = self.case(etape=STAGES[2])
        with self.assertRaisesRegex(ValueError, 'justificatifs'):
            self.store.save(c)
        self.assertEqual(self.store.list(), [])
        c.identite_propriete_verifiees = True
        with self.assertRaisesRegex(ValueError, 'justificatifs'):
            self.store.save(c)
        c.mandat_signe = True
        self.assertEqual(self.store.save(c).etape, STAGES[2])

    def test_invalid_year(self):
        with self.assertRaisesRegex(ValueError, 'Année'):
            self.store.save(self.case(annee='text'))
        with self.assertRaisesRegex(ValueError, 'Année'):
            self.store.save(self.case(annee='1830'))

    def test_delete(self):
        c = self.store.save(self.case())
        self.store.delete(c.id)
        self.assertIsNone(self.store.get(c.id))

    def test_report_escapes_html(self):
        c = self.store.save(self.case(modele='<script>alert(1)</script>', notes='<img src=x onerror=evil()>'))
        doc = to_html(c)
        self.assertIn('&lt;script&gt;', doc)
        self.assertNotIn('<script>', doc)
        self.assertNotIn('<img src=x', doc)
        self.assertIn('ne déverrouille pas', doc)

    def test_csv_formula_injection_blocked(self):
        self.assertEqual(csv_safe('=2+2'), "'=2+2")
        self.assertEqual(csv_safe('  +SUM(1,2)'), "'  +SUM(1,2)")
        self.assertEqual(csv_safe('@HYPERLINK'), "'@HYPERLINK")
        self.assertEqual(csv_safe('Renault'), 'Renault')
        c = self.store.save(self.case(marque='=1+1'))
        target = Path(self.tmp.name) / 'safe.csv'
        export_csv([c], target)
        self.assertIn("'=1+1", target.read_text(encoding='utf-8-sig'))

    def test_validate_notes_length(self):
        with self.assertRaisesRegex(ValueError, 'Notes trop longues'):
            self.store.save(self.case(notes='A'*1201))

    def test_completed_requires_verifications(self):
        with self.assertRaisesRegex(ValueError, 'justificatifs'):
            self.store.save(self.case(etape=STAGES[-2]))

    def test_csv(self):
        c = self.store.save(self.case())
        target = Path(self.tmp.name)/'export.csv'
        export_csv([c], target)
        contents = target.read_text(encoding='utf-8-sig')
        self.assertIn('Renault', contents)
        self.assertIn('Réf.', contents)
        self.assertNotIn('VIN', contents)

if __name__ == '__main__':
    unittest.main()
