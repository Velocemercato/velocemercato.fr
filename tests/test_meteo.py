"""Météo & Découverte sur velocemercato.fr : affichage, données et absence de débordement. Aucun appel externe."""
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
from threading import Thread
import unittest
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class MeteoTests(unittest.TestCase):
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

    def test_meteo_page(self):
        def weather(route):
            query = parse_qs(urlsplit(route.request.url).query)
            count = len(query['latitude'][0].split(','))
            item = {'current': {'time': '2026-10-23T14:00', 'temperature_2m': 14.2, 'apparent_temperature': 12.9, 'weather_code': 3,
                                'wind_speed_10m': 11.0, 'relative_humidity_2m': 70},
                    'daily': {'time': ['2026-10-23'] * 7, 'weather_code': [61] * 7, 'temperature_2m_max': [16.0] * 7,
                              'temperature_2m_min': [8.0] * 7, 'precipitation_probability_max': [40] * 7}}
            route.fulfill(json=[item] * count if count > 1 else item)
        for width in [320, 1440]:
            context = self.browser.new_context(viewport={'width': width, 'height': 900}, service_workers='block')
            context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(self.base + '/') else route.abort())
            context.route('https://api.open-meteo.com/**', weather)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            with self.subTest(width=width):
                page.goto(self.base + '/meteo/', wait_until='networkidle')
                self.assertEqual(page.locator('#villes .ville').count(), 16)
                self.assertGreater(page.locator('#lieux .lieu').count(), 4)
                self.assertEqual(page.locator('.portal-brand').get_attribute('href'), 'https://vmunivers.fr/')
                self.assertEqual(page.locator('link[rel=canonical]').get_attribute('href'), 'https://velocemercato.fr/meteo/')
                self.assertEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                self.assertFalse(errors, errors)
            context.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
