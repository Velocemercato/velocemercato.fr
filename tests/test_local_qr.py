"""QR calculés localement, brouillon du menu et téléchargement d'une vraie image."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json, unittest
from PIL import Image
import test_site as site


class LocalQRTests(unittest.TestCase):
    setUpClass=classmethod(site.SiteTests.setUpClass.__func__)
    tearDownClass=classmethod(site.SiteTests.tearDownClass.__func__)
    context=site.SiteTests.context

    def test_share_qr_needs_no_external_generator(self):
        context=self.context();page=context.new_page();requests=[]
        page.on('request',lambda r:requests.append(r.url))
        page.goto(self.base,wait_until='networkidle');page.locator('#vmFab').click()
        page.wait_for_selector('#vmShQ canvas',state='attached')
        page.wait_for_function("document.querySelector('#vmShQ img')?.naturalWidth>0")
        self.assertFalse(any('qrserver.com' in u or 'qrcodejs' in u for u in requests),requests)
        context.close()

    @unittest.skipIf(site.PORTAL,'Le générateur de menus se trouve sur le domaine média.')
    def test_menu_survives_reload_and_download_is_an_image(self):
        context=self.context();page=context.new_page();requests=[]
        page.on('request',lambda r:requests.append(r.url))
        page.goto(self.base+'/menu/',wait_until='networkidle')
        page.locator('#nom').fill('Café de test')
        page.locator('#txt').fill('# Midi\nPlat du jour | 12 €')
        page.wait_for_function("JSON.parse(localStorage.getItem('vm-menu')).n==='Café de test'")
        page.reload(wait_until='networkidle')
        self.assertEqual(page.locator('#nom').input_value(),'Café de test')
        self.assertIn('Plat du jour',page.locator('#menu').inner_text())
        with page.expect_download() as pending:page.locator('#dl').click()
        with TemporaryDirectory() as folder:
            path=Path(folder)/'qr.png';pending.value.save_as(str(path))
            with Image.open(path) as im:self.assertEqual(im.size,(880,880));self.assertEqual(im.format,'PNG')
        link=page.locator('#cp').get_attribute('data-u')
        page.goto(link,wait_until='networkidle')
        self.assertTrue(page.locator('body').evaluate("b=>b.classList.contains('viewer')"))
        self.assertIn('Café de test',page.locator('#menu').inner_text())
        self.assertFalse(any('qrserver.com' in u for u in requests))
        context.close()

    @unittest.skipIf(site.PORTAL,'Le générateur de menus se trouve sur le domaine média.')
    def test_long_menu_keeps_draft_and_disables_invalid_download(self):
        context=self.context();page=context.new_page();page.goto(self.base+'/menu/',wait_until='networkidle')
        page.locator('#txt').fill('Un très long menu '+('Plat | 12 €\n'*250))
        page.wait_for_function("document.querySelector('#dl').disabled")
        self.assertIn('Carte trop longue',page.locator('#qr').inner_text())
        self.assertEqual(page.locator('#qr canvas,#qr img').count(),0)
        self.assertIn('Un très long menu',page.evaluate("JSON.parse(localStorage.getItem('vm-menu')).t"))
        context.close()

if __name__=='__main__':unittest.main(verbosity=2)
