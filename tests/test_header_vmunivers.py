"""L'en-tête visible de l'accueil affiche Véloce Mercato et VMUNIVERS.FR sur une même ligne."""
import functools
import http.server
from pathlib import Path
import threading
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = (320, 360, 390, 430, 768, 1024, 1366)


class HeaderVmUniversTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        handler.log_message = lambda *args: None
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()

    def test_static_markup(self):
        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        header = home.split('<header class="vm-cinema-top">', 1)[1].split('</header>', 1)[0]
        self.assertIn('class="vm-cinema-logo"', header)
        self.assertIn('class="vm-cinema-univers" href="https://vmunivers.fr/"', header)
        self.assertLess(header.index('vm-cinema-logo'), header.index('vm-cinema-univers'))
        self.assertLess(header.index('vm-cinema-univers'), header.index('vm-cinema-menu'))

    def test_logo_and_vmunivers_on_one_line_at_every_width(self):
        for width in WIDTHS:
            with self.subTest(width=width):
                mobile = width < 700
                context = self.browser.new_context(viewport={'width': width, 'height': 800},
                                                   is_mobile=mobile, has_touch=mobile)
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/*', lambda route: route.abort()
                           if not route.request.url.startswith(self.base) else route.continue_())
                page.goto(self.base + '/', wait_until='load')
                info = page.evaluate("""() => {
                  const logo = document.querySelector('.vm-cinema-logo');
                  const univ = document.querySelector('.vm-cinema-univers');
                  const menu = document.querySelector('.vm-cinema-menu');
                  const box = e => e.getBoundingClientRect();
                  const hit = e => { const r = box(e);
                    return document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)?.closest('a') === e; };
                  const l = box(logo), u = box(univ), m = box(menu);
                  return {l: [l.left, l.right, l.top + l.height / 2], u: [u.left, u.right, u.top + u.height / 2, u.height],
                          menuTop: m.top, uBottom: u.bottom, hitLogo: hit(logo), hitUniv: hit(univ),
                          href: univ.href, logoHref: logo.getAttribute('href'),
                          scroll: document.documentElement.scrollWidth, vw: innerWidth};
                }""")
                self.assertEqual(info['href'], 'https://vmunivers.fr/')
                self.assertEqual(info['logoHref'], '/')
                self.assertLess(abs(info['l'][2] - info['u'][2]), 6)        # même ligne
                self.assertGreater(info['u'][0], info['l'][1])               # à droite du logo, sans chevauchement
                self.assertLessEqual(info['u'][1], info['vw'])               # pas hors écran
                self.assertGreaterEqual(info['u'][3], 44)                    # cible tactile suffisante
                self.assertTrue(info['hitLogo'] and info['hitUniv'])         # rien ne recouvre les liens
                self.assertEqual(info['scroll'], info['vw'])                 # pas de défilement horizontal
                if width <= 750:
                    self.assertGreaterEqual(info['menuTop'], info['uBottom'] - 2)  # menu juste en dessous
                self.assertFalse(errors, errors)
                context.close()


if __name__ == '__main__':
    unittest.main()
