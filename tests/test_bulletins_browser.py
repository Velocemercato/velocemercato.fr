"""Navigation et routage des JT séparés sur téléphone et ordinateur."""
import json
from pathlib import Path
import unittest

import test_site as site


class BulletinsBrowserTests(unittest.TestCase):
    context = site.SiteTests.context

    @classmethod
    def setUpClass(cls):
        site.SiteTests.setUpClass()
        cls.browser, cls.base = site.SiteTests.browser, site.SiteTests.base

    @classmethod
    def tearDownClass(cls): site.SiteTests.tearDownClass()

    def test_each_site_shows_its_own_confirmed_youtube_journal(self):
        rows = [{'id':name+'-edition-20261023-'+hour, 'date_publication':'2026-10-23T'+clock+':15:00Z',
                 'universes':[name], 'titre':title, 'edition_at':'2026-10-23T'+hour[:2]+':00:00+02:00',
                 'plateformes':{'youtube':{'status':'published','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}}}
                for name,hour,clock,title in [('foot','1200','10','Foot, JT de 12 h'),('actus','1300','11','Actus, JT de 13 h'),('gaming','1800','16','Gaming, JT de 18 h')]]
        for width in (390,1440):
            context=self.context(width)
            context.route('**/studio/diffusions.json', lambda route:route.fulfill(json=rows))
            page=context.new_page()
            for path,title in [('/',rows[0]['titre']),('/actus/',rows[1]['titre']),('/vm-gaming/',rows[2]['titre'])]:
                page.goto(self.base+path, wait_until='networkidle')
                section=page.locator('[data-broadcast-feed]')
                self.assertTrue(section.is_visible())
                self.assertEqual(section.locator('h2').text_content(),title)
                self.assertEqual(section.locator('iframe').count(),0)
                self.assertEqual(section.locator('a').get_attribute('href'),'https://www.youtube.com/watch?v=aB1cdEF2ghi')
                old=page.locator('[data-pastille-universe]') if path!='/' else page.locator('#ptvMain')
                self.assertFalse(old.is_visible())
                section.get_by_role('button',name='▶ Lire ce JT en HD ici').click()
                frame=section.locator('iframe')
                self.assertEqual(frame.get_attribute('src'),'https://www.youtube-nocookie.com/embed/aB1cdEF2ghi?autoplay=1&rel=0')
                self.assertEqual(frame.get_attribute('title'),title)
                self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth'))
            context.close()

    def test_official_broadcasters_page_navigation_no_overflow_and_no_embeds(self):
        providers=json.loads((site.ROOT/'diffuseurs.json').read_text())['providers']
        for width in (390,1440):
            context=self.context(width);page=context.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(self.base,wait_until='networkidle')
            page.locator('#plus-de-foot > summary').click()
            page.get_by_role('link',name='Où regarder les matchs légalement ? →',exact=True).click()
            self.assertTrue(page.url.endswith('/ou-regarder.html'))
            self.assertEqual(page.locator('h1').inner_text(),'Où regarder les matchs ?')
            self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth'))
            self.assertEqual(page.locator('iframe,video').count(),0)
            for provider in providers:
                self.assertEqual(page.locator('.provider a[href="'+provider['url']+'"]').count(),1)
            page.screenshot(path=str(site.ARTIFACTS/f'diffuseurs-{width}.png'),full_page=True)
            page.get_by_role('link',name='Nos JT',exact=True).click()
            self.assertTrue(page.url.endswith('/studio.html#tv'))
            for label in ['Actus 7 h · 13 h · 19 h','Foot 8 h · 12 h · 20 h · 23 h','Gaming 0 h · 10 h · 18 h']:
                self.assertIn(label,' '.join(page.locator('.tv-head').inner_text().split()))
            page.screenshot(path=str(site.ARTIFACTS/f'jt-grid-{width}.png'),full_page=False)
            self.assertEqual(errors,[])
            context.close()


if __name__ == '__main__': unittest.main(verbosity=2)
