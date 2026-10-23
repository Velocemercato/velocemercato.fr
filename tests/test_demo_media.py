"""Vérifie les démos illustrées, leur accessibilité et les achats simulés."""
import re
import unittest

import test_site as site


class DemoMediaTests(unittest.TestCase):
    setUpClass = classmethod(site.SiteTests.setUpClass.__func__)
    tearDownClass = classmethod(site.SiteTests.tearDownClass.__func__)
    context = site.SiteTests.context
    demos = ['coiffeur', 'beaute', 'restaurant', 'snack', 'artisan', 'drive', 'cbd']

    def dismiss_age(self, page):
        gate = page.locator('.vd-age')
        if gate.count():
            gate.get_by_role('button', name='Oui, j’ai 18 ans ou plus').click()

    def test_all_demo_images_exist_and_layouts_fit(self):
        for name in self.demos + ['investir']:
            path = '/investisseurs.html' if name == 'investir' else f'/demos/{name}.html'
            source = (site.ROOT / path.lstrip('/')).read_text()
            for image in set(re.findall(r'/demos/img/[\w/-]+\.webp', source)):
                self.assertTrue((site.ROOT / image.lstrip('/')).is_file(), image)
            for width in [320, 390, 1440]:
                with self.subTest(demo=name, width=width):
                    context = self.context(width)
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.goto(self.base + path, wait_until='networkidle')
                    self.dismiss_age(page)
                    self.assertEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    self.assertFalse(errors, errors)
                    hero = page.locator('.vd-hero-art img')
                    self.assertTrue(hero.evaluate('image => image.complete && image.naturalWidth > 1000'))
                    self.assertEqual(page.locator('.vd-hero-art .vd-ph').count(), 0)
                    self.assertEqual(page.locator('.vd-play').count(), 0)
                    self.assertTrue(page.locator('a[href="https://vmunivers.fr/"]').count())
                    context.close()

    def test_gallery_keyboard_and_missing_video_do_not_break_the_page(self):
        context = self.context()
        page = context.new_page()
        missing = []
        page.on('response', lambda response: missing.append(response.url) if response.status >= 400 else None)
        page.goto(self.base + '/demos/coiffeur.html', wait_until='networkidle')
        photo = page.locator('.vd-gal .vd-media').first
        photo.scroll_into_view_if_needed()
        page.wait_for_function('document.querySelector(".vd-gal img").naturalWidth > 0')
        photo.focus()
        page.keyboard.press('Enter')
        viewer = page.get_by_role('dialog', name='Photo agrandie')
        self.assertTrue(viewer.is_visible())
        self.assertEqual(viewer.locator('img').get_attribute('alt'), 'Dégradé américain')
        page.keyboard.press('Tab')
        self.assertTrue(viewer.get_by_role('button', name='Fermer').evaluate('node => node === document.activeElement'))
        page.keyboard.press('Escape')
        self.assertFalse(viewer.is_visible())
        self.assertTrue(photo.evaluate('node => node === document.activeElement'))
        page.locator('.vd-extra-video > summary').click()
        page.get_by_text('Vidéo à venir', exact=True).first.wait_for()
        self.assertIn('Vidéo à venir', page.locator('.vd-extra-video').inner_text())
        self.assertEqual(page.locator('.vd-extra-video video,.vd-extra-video .vd-play').count(), 0)
        page.wait_for_timeout(100)
        self.assertFalse(missing, missing)
        context.close()

    def test_product_photo_and_cart_survive_catalogue_filters(self):
        context = self.context()
        page = context.new_page()
        methods = []
        page.on('request', lambda request: methods.append(request.method))
        page.goto(self.base + '/demos/drive.html', wait_until='networkidle')
        page.locator('[data-search]').fill('pommes')
        card = page.locator('[data-items] .vd-card')
        self.assertEqual(card.count(), 1)
        card.scroll_into_view_if_needed()
        page.wait_for_function('document.querySelector("[data-items] img").naturalWidth > 0')
        card.get_by_role('button', name='Ajouter', exact=True).click()
        self.assertIn('1 article', page.locator('.vd-cartbar').inner_text())
        page.locator('[data-search]').fill('carottes')
        self.assertEqual(page.locator('[data-items] .vd-card').count(), 1)
        page.get_by_role('button', name='Voir le panier →').click()
        self.assertIn('Pommes Golden locales', page.locator('.vd-sheet:not([hidden])').inner_text())
        self.assertTrue(all(method == 'GET' for method in methods), methods)
        context.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
