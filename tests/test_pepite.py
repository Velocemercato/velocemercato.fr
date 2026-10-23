"""Pépite FC : formulaires par e-mail, liens vidéo filtrés et dossiers validés. Aucun appel externe."""
import json
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class PepiteTests(unittest.TestCase):
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

    def context(self, dossiers=None, width=390):
        context = self.browser.new_context(viewport={'width': width, 'height': 844}, service_workers='block')
        context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(self.base + '/') else route.abort())
        if dossiers is not None:
            context.route(self.base + '/pepite/dossiers.json', lambda route: route.fulfill(json=dossiers))
        context.add_init_script('window.sent = null; window.vmMail = (s, b) => { window.sent = {s, b}; };')
        return context

    def test_01_empty_list_and_forms(self):
        context = self.context([])
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(self.base + '/pepite/', wait_until='networkidle')
        self.assertIn('Les premiers dossiers validés', page.locator('#dossiers').inner_text())
        page.locator('#formJoueur [name=prenom]').fill('Léo')
        page.locator('#formJoueur [name=nom]').fill('Martin')
        page.locator('#formJoueur [name=categorie]').select_option('U15')
        page.locator('#formJoueur [name=poste]').select_option('Milieu')
        page.locator('#formJoueur [name=ville]').fill('Belfort')
        page.locator('#formJoueur [name=videos]').fill('https://youtu.be/abc123')
        page.locator('#formJoueur [name=mineur]').check()
        page.locator('#formJoueur [name=accord]').check()
        page.locator('#formJoueur [type=submit]').click()
        sent = page.evaluate('window.sent')
        self.assertIn('Léo Martin', sent['s'])
        self.assertIn('Catégorie : U15', sent['b'])
        page.locator('#formPro [name=nom]').fill('Claire Dupont')
        page.locator('#formPro [name=statut]').select_option('Conseiller sportif')
        page.locator('#formPro [name=email]').fill('claire@example.com')
        page.locator('#formPro [name=texte]').fill('Recherche attaquants U17 en Bourgogne.')
        page.locator('#formPro [required]').last.check()
        page.locator('#formPro [type=submit]').click()
        self.assertIn('Claire Dupont', page.evaluate('window.sent.s'))
        self.assertEqual(errors, [])
        self.assertEqual(page.evaluate('document.documentElement.scrollWidth'), 390)
        context.close()

    def test_minor_category_requires_parental_agreement(self):
        context=self.context([]);page=context.new_page();page.goto(self.base+'/pepite/',wait_until='networkidle')
        page.locator('#formJoueur [name=prenom]').fill('Joueur')
        page.locator('#formJoueur [name=nom]').fill('Test')
        page.locator('#formJoueur [name=categorie]').select_option('U15')
        page.locator('#formJoueur [name=poste]').select_option('Milieu')
        page.locator('#formJoueur [name=ville]').fill('Belfort')
        page.locator('#formJoueur [name=videos]').fill('https://youtu.be/abc123')
        page.locator('#formJoueur [name=accord]').check()
        page.locator('#formJoueur [type=submit]').click()
        self.assertIsNone(page.evaluate('window.sent'))
        page.locator('#formJoueur [name=mineur]').check()
        page.locator('#formJoueur [type=submit]').click()
        self.assertIn('Mineur : Oui',page.evaluate('window.sent.b'))
        context.close()

    def test_failed_profiles_are_not_presented_as_empty(self):
        context=self.context();failed=[True]
        context.route(self.base+'/pepite/dossiers.json',lambda r:r.fulfill(status=503,json={}) if failed[0] else r.fulfill(json=[]))
        page=context.new_page();page.goto(self.base+'/pepite/',wait_until='networkidle')
        self.assertIn('Impossible de charger',page.locator('#dossiers').inner_text())
        self.assertNotIn('Les premiers dossiers',page.locator('#dossiers').inner_text())
        failed[0]=False;page.get_by_role('button',name='Réessayer',exact=True).click()
        page.wait_for_function("document.querySelector('#dossiers').textContent.includes('Les premiers dossiers')")
        context.close()

    def test_02_validated_players_and_safe_links(self):
        context = self.context([
            {'prenom': 'Léo', 'nom': 'Martin', 'categorie': 'U15', 'poste': 'Milieu', 'ville': 'Belfort', 'club': '', 'scolaire': '3e',
             'videos': 'https://youtu.be/abc123 http://evil.example/x https://evil.example/y https://vimeo.com/42'},
            {'prenom': '<img src=x onerror=alert(1)>', 'categorie': 'U13', 'poste': 'Gardien', 'ville': 'Lyon', 'videos': 'javascript:alert(1)'},
            {'categorie': 'U13', 'poste': 'Gardien'},
        ])
        page = context.new_page()
        page.goto(self.base + '/pepite/', wait_until='networkidle')
        cards = page.locator('#dossiers .joueur')
        self.assertEqual(cards.count(), 2)
        self.assertEqual(page.locator('#dossiers img').count(), 0)
        hrefs = page.locator('#dossiers .joueur a').evaluate_all('links => links.map(l => l.href)')
        self.assertEqual(hrefs, ['https://youtu.be/abc123', 'https://vimeo.com/42'])
        self.assertNotIn('Martin', page.locator('#dossiers').inner_text())
        context.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
