"""VM Studio : 3 offres d'entrée claires, devis préparé vers Gmail, aucun délai ni résultat promis."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / 'web-studio.html').read_text(encoding='utf-8')


class OffresTests(unittest.TestCase):
    def test_three_entry_offers_with_prices_examples_and_quote_buttons(self):
        section = PAGE.split('id="trois-offres"', 1)[1].split('</section>', 1)[0]
        for name, price, offer in (('Visuels', 'dès 90 €', 'visuels'), ('Page web', 'dès 290 €', 'mini'), ('Site vitrine', 'dès 590 €', 'starter')):
            self.assertIn(f'<h4>{name}</h4>', section)
            self.assertIn(price, section)
            self.assertIn(f'data-offer="{offer}"', section)
        for link in re.findall(r'href="(/[^"#]+)"', section):
            self.assertTrue((ROOT / link.lstrip('/')).is_file(), link)
        self.assertIn('TVA non applicable', section)
        self.assertIn('Aucun résultat commercial n’est garanti', section)

    def test_form_offers_every_entry_offer_once_and_tags_the_subject(self):
        options = re.findall(r'<option value="([a-z]+)"', PAGE)
        self.assertEqual(len(options), len(set(options)))
        for value in ('visuels', 'mini', 'starter'):
            self.assertIn(value, options)
        self.assertIn('data-subject="[VM Studio · Demande de devis]"', PAGE)

    def test_no_unconfirmed_delay_or_popularity_claim(self):
        for claim in ('Délais estimés', 'sous 24 h', 'Réponse rapide', 'Le plus demandé', 'garanti 100'):
            self.assertNotIn(claim, PAGE)

    def test_subject_prefix_only_for_tagged_forms(self):
        script = (ROOT / 'assets/pro-contact.js').read_text(encoding='utf-8')
        self.assertIn('form.dataset.subject ?', script)
        self.assertIn('`Projet VM — ${label}`', script)  # les autres formulaires gardent leur objet
        subprocess.run(['node', '--check', str(ROOT / 'assets/pro-contact.js')], check=True)


if __name__ == '__main__':
    unittest.main()
