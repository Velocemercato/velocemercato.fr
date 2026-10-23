"""Pages de services : recettes, produits locaux, sport, immobilier et RDV. Aucun appel externe."""
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['recettes', 'produits-locaux', 'sport', 'immo', 'rdv']


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class ServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
        Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.playwright = sync_playwright().start()
        executable = os.environ.get('VM_CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        cls.browser = cls.playwright.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def context(self, width=390):
        context = self.browser.new_context(viewport={'width': width, 'height': 900}, service_workers='block')
        context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(self.base + '/') else route.abort())
        context.add_init_script('window.sent = null; window.vmMail = (s, b) => { window.sent = {s, b}; };')
        return context

    def test_pages_load_without_errors(self):
        for width in [320, 1440]:
            context = self.context(width)
            for slug in PAGES:
                with self.subTest(page=slug, width=width):
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.goto(f'{self.base}/{slug}/', wait_until='networkidle')
                    self.assertTrue(page.locator('h1').count() == 1)
                    self.assertEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    self.assertFalse(errors, errors)
                    page.close()
            context.close()

    def test_recettes_day_and_filters(self):
        context = self.context()
        page = context.new_page()
        page.goto(self.base + '/recettes/', wait_until='networkidle')
        self.assertEqual(page.locator('#jour .rec').count(), 3)
        page.locator('#fRegime').select_option('vegan')
        page.locator('#fObj').select_option('minceur')
        self.assertTrue(all('vegan' in t for t in page.locator('#liste .tags').all_text_contents()))
        self.assertGreater(page.locator('#liste .rec').count(), 0)
        page.locator('#fOcc').select_option('grande soirée')
        self.assertIn('Aucune recette', page.locator('#liste').inner_text())
        context.close()

    def test_produits_and_sport_forms(self):
        context = self.context()
        page = context.new_page()
        page.goto(self.base + '/produits-locaux/', wait_until='networkidle')
        self.assertIn('Pas encore de producteur', page.locator('#producteurs').inner_text())
        page.locator('#formProd [name=nom]').fill('Fromagerie Test')
        page.locator('#formProd [name=ville]').fill('Belfort')
        page.locator('#formProd [name=region]').select_option('Bourgogne-Franche-Comté')
        page.locator('#formProd [name=cat]').select_option('Fromage')
        page.locator('#formProd [name=desc]').fill('Tomme de montagne au lait cru.')
        page.locator('#formProd [type=checkbox]').check()
        page.locator('#formProd [type=submit]').click()
        self.assertIn('Fromagerie Test', page.evaluate('window.sent.s'))
        page.goto(self.base + '/sport/', wait_until='networkidle')
        page.locator('[data-niv=avance]').click()
        self.assertIn('Avancé', page.locator('#muscu').inner_text())
        page.locator('#formChemin [name=nom]').fill('Tour du lac test')
        page.locator('#formChemin [name=region]').select_option('Grand Est')
        page.locator('#formChemin [name=desc]').fill('Boucle plate de 8 km autour du lac.')
        page.locator('#formChemin [type=checkbox]').check()
        page.locator('#formChemin [type=submit]').click()
        self.assertIn('Tour du lac test', page.evaluate('window.sent.s'))
        context.close()

    def test_immo_links_and_rdv(self):
        context = self.context()
        page = context.new_page()
        page.goto(self.base + '/immo/', wait_until='networkidle')
        self.assertIn('du ', page.locator('#weekend').inner_text())
        href = page.locator('a.airbnb').first.get_attribute('href')
        self.assertIn('airbnb.fr/s/', href)
        self.assertIn('checkin=', href)
        page.goto(self.base + '/rdv/', wait_until='networkidle')
        self.assertEqual(page.locator('#cats .rdvc').count(), 6)
        page.locator('#ville').fill('Belfort')
        self.assertIn('Belfort', page.locator('#cats a').first.get_attribute('href') + page.locator('#cats a').nth(1).get_attribute('href'))
        self.assertIn('15', page.locator('.urg').inner_text())
        context.close()

    def test_data_failure_is_distinct_from_empty_list_and_retry_works(self):
        for path,url,target in [('produits-locaux','producteurs.json','producteurs'),('sport','chemins.json','chemins')]:
            with self.subTest(path=path):
                context=self.context();failed=[True]
                context.route(self.base+'/'+path+'/'+url,lambda r:r.fulfill(status=503,json={}) if failed[0] else r.fulfill(json=[]))
                page=context.new_page();page.goto(self.base+'/'+path+'/',wait_until='networkidle')
                self.assertIn('Impossible de charger',page.locator('#'+target).inner_text())
                self.assertNotIn('Pas encore',page.locator('#'+target).inner_text())
                failed[0]=False;page.get_by_role('button',name='Réessayer',exact=True).click()
                page.wait_for_function('(id)=>document.getElementById(id).textContent.includes("Pas encore")',arg=target)
                context.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
