"""Radio : affiches locales, absence de lecture automatique et reprise après panne."""
import unittest
import test_site as site


class RadioTests(unittest.TestCase):
    setUpClass = classmethod(site.SiteTests.setUpClass.__func__)
    tearDownClass = classmethod(site.SiteTests.tearDownClass.__func__)
    context = site.SiteTests.context

    def test_posters_are_local_and_audio_waits_for_listener(self):
        context = self.context(); page = context.new_page(); requests = []
        page.on('request', lambda r: requests.append(r.url))
        page.goto(self.base + '/radio.html', wait_until='networkidle')
        self.assertGreater(page.locator('#list button[data-i]').count(), 0)
        for image in page.locator('#list img').all():
            self.assertTrue(image.get_attribute('src').startswith('/'))
        self.assertFalse(any(u.endswith(('.mp4', '.m4a')) for u in requests), requests)
        page.locator('#playBtn').click()
        page.wait_for_function("document.querySelector('#nowMeta').textContent.includes('L’audio ne se charge pas')")
        self.assertTrue(page.locator('#nowImg').get_attribute('src').startswith('/'))
        self.assertFalse(any('cdn.jsdelivr.net' in u and u.endswith(('.jpg', '.png', '.webp')) for u in requests), requests)
        context.close()

    def test_failed_list_can_be_retried_without_fake_empty_state(self):
        context = self.context(); page = context.new_page()
        pattern = '**/studio/emissions.json*'
        context.route(pattern, lambda route: route.fulfill(status=503, body='indisponible'))
        page.goto(self.base + '/radio.html', wait_until='networkidle')
        self.assertIn('Impossible de charger', page.locator('#list').inner_text())
        self.assertTrue(page.locator('#playBtn').is_disabled())
        context.unroute(pattern)
        page.get_by_role('button', name='Réessayer', exact=True).click()
        page.wait_for_selector('#list button[data-i]')
        self.assertTrue(page.locator('#playBtn').is_enabled())
        context.close()


if __name__ == '__main__': unittest.main(verbosity=2)
