"""Parcours professionnel : choix d'offre et brouillon local sans envoi implicite."""
import unittest
from urllib.parse import urlsplit, parse_qs
import test_site as site

class ProfessionalTests(unittest.TestCase):
    setUpClass = classmethod(site.SiteTests.setUpClass.__func__)
    tearDownClass = classmethod(site.SiteTests.tearDownClass.__func__)
    context = site.SiteTests.context
    paths = ['/professionnels/'] if site.PORTAL else ['/web-studio.html', '/pub/']

    def test_home_exposes_studio_and_preserves_identity(self):
        context = self.context(); page = context.new_page()
        page.goto(self.base, wait_until='networkidle')
        if site.PORTAL:
            self.assertTrue(page.locator('.portal-links a[href="/professionnels/"]').is_visible())
            page.get_by_role('searchbox').fill('cartes visite')
            self.assertEqual(page.locator('.ap:not([hidden])').count(), 1)
            self.assertEqual(page.locator('.ap:not([hidden])').get_attribute('href'), '/professionnels/')
            self.assertEqual(page.locator('.grp .gapps .gapps').count(), 0)
        else:
            self.assertTrue(page.locator('.vmbar a[href="/web-studio.html"]').is_visible())
            self.assertIn('football', page.title().lower())
            self.assertIn('cartes de visite', page.locator('.promo-entry').inner_text())
        context.close()

    def test_offer_shortcuts_and_prefilled_url(self):
        context = self.context(); page = context.new_page()
        for path in self.paths:
            value = 'local' if path == '/pub/' else 'cartes'
            page.goto(self.base + path + '?offre=' + value + '#devis', wait_until='networkidle')
            self.assertEqual(page.locator('select[name=service]').input_value(), value)
            for link in page.locator('a[data-offer]').all():
                expected = link.get_attribute('data-offer')
                link.click()
                self.assertEqual(page.locator('select[name=service]').input_value(), expected)
        context.close()

    def test_draft_keeps_accents_and_sends_nothing(self):
        context = self.context(); page = context.new_page()
        for path in self.paths:
            page.goto(self.base + path, wait_until='networkidle')
            url = page.url
            page.locator('input[name=nom]').fill('Atelier Test & Fils')
            page.locator('input[name=ville]').fill('Belfort')
            page.locator('textarea[name=besoin]').fill('Carte recto / verso — été & création <test>.')
            requests = []
            page.on('request', lambda r: requests.append({'url': r.url, 'method': r.method}))
            page.get_by_role('button', name='Préparer ma demande').click()
            self.assertTrue(page.locator('[data-pro-result]').is_visible())
            parts = urlsplit(page.locator('[data-pro-mail]').get_attribute('href'))
            self.assertEqual(parts.path, 'vminvest.fr@gmail.com')
            body = parse_qs(parts.query)['body'][0]
            self.assertIn('Atelier Test & Fils', body)
            self.assertIn('Carte recto / verso — été & création <test>.', body)
            self.assertIn('\n\nMon projet :\n', body)
            self.assertEqual(page.url, url)
            # Le défilement peut charger des images ; aucune requête de contact ne part.
            self.assertTrue(all(r['method'] == 'GET' and urlsplit(r['url']).path.endswith(('.webp', '.png', '.jpg')) and r['url'].startswith(self.base + '/') and not urlsplit(r['url']).query for r in requests), requests)
            self.assertEqual(page.evaluate('Object.keys(localStorage)'), [])
            page.locator('textarea[name=besoin]').fill('Un autre besoin')
            self.assertTrue(page.locator('[data-pro-result]').is_hidden())
        context.close()

    def test_copy_fallback_and_offer_change_invalidate_draft(self):
        context = self.context(); page = context.new_page()
        page.goto(self.base + self.paths[0], wait_until='networkidle')
        page.locator('input[name=nom]').fill('Atelier de test')
        page.locator('textarea[name=besoin]').fill('Une carte de visite')
        page.get_by_role('button', name='Préparer ma demande').click()
        page.evaluate("Object.defineProperty(navigator, 'clipboard', {value: {writeText: () => Promise.reject(new Error('indisponible'))}, configurable:true})")
        page.get_by_role('button', name='Copier la demande').click()
        self.assertIn('Sélectionnez Copier', page.locator('[data-pro-status]').inner_text())
        self.assertIn('Atelier de test', page.evaluate('getSelection().toString()'))
        page.locator('a[data-offer]').first.click()
        self.assertTrue(page.locator('[data-pro-result]').is_hidden())
        page.locator('input[name=nom]').fill('   ')
        page.get_by_role('button', name='Préparer ma demande').click()
        self.assertTrue(page.locator('[data-pro-result]').is_hidden())
        self.assertFalse(page.locator('input[name=nom]').evaluate('element => element.checkValidity()'))
        page.locator('input[name=nom]').fill('Nouvel atelier')
        page.get_by_role('button', name='Préparer ma demande').click()
        self.assertTrue(page.locator('[data-pro-result]').is_visible())
        self.assertIn('Nouvel atelier', page.locator('[data-pro-preview]').inner_text())
        context.close()

    def test_email_available_without_javascript(self):
        context = self.browser.new_context(java_script_enabled=False)
        context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(self.base + '/') else r.abort())
        page = context.new_page()
        for path in self.paths:
            page.goto(self.base + path, wait_until='networkidle')
            self.assertTrue(page.locator('a.pro-mail[href="mailto:vminvest.fr@gmail.com"]').is_visible())
            self.assertIn('Écrivez directement', page.locator('noscript').inner_text())
        context.close()

    def test_portfolio_previews_fit_their_cards(self):
        for width in [390, 1440]:
            context = self.context(width); page = context.new_page()
            page.goto(self.base + self.paths[0], wait_until='networkidle')
            self.assertGreater(page.locator('.pro-work > img').count(), 0)
            for image in page.locator('.pro-work > img').all():
                box = image.bounding_box()
                self.assertGreater(box['height'], 0)
                self.assertLessEqual(box['height'], box['width'] + 1)
            context.close()

if __name__ == '__main__': unittest.main(verbosity=2)
