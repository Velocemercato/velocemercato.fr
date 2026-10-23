"""Un visiteur trouve les actus et le JT, puis les fonctions secondaires à la demande."""
import unittest
from urllib.parse import urlsplit
import test_site as site

class HomeClarityTests(unittest.TestCase):
    setUpClass=classmethod(site.SiteTests.setUpClass.__func__)
    tearDownClass=classmethod(site.SiteTests.tearDownClass.__func__)
    context=site.SiteTests.context

    def test_news_is_immediately_reachable_and_more_articles_stay_available(self):
        for width,total in [(390,4),(1440,6)]:
            context=self.context(width);page=context.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(self.base,wait_until='networkidle')
            self.assertEqual(page.locator('main').count(),1)
            self.assertEqual(page.locator('#feed .card').count(),total)
            headline=page.locator('#feed .card h3').first.bounding_box()
            self.assertLess(headline['y'],page.viewport_size['height'])
            self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth'))
            self.assertFalse(page.locator('#plus-de-foot').get_attribute('open'))
            self.assertTrue(page.locator('#reseaux').is_visible())
            self.assertEqual(page.locator('.home-portal').get_attribute('href'),'https://vmunivers.fr/')
            page.locator('#feedMore').click();self.assertEqual(page.locator('#feed .card').count(),2*total)
            page.locator('#cats button[data-cat=MERCATO]').click()
            self.assertEqual(page.locator('#cats button[data-cat=MERCATO]').get_attribute('aria-pressed'),'true')
            page.locator('.home-filter-more > summary').click()
            page.locator('#cats button[data-cat=LIGUE_2]').click()
            self.assertEqual(page.locator('#cats button[data-cat=LIGUE_2]').get_attribute('aria-pressed'),'true')
            self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth'))
            self.assertEqual(errors,[])
            context.close()

    def test_secondary_video_requests_wait_until_open_and_old_links_still_work(self):
        context=self.context();page=context.new_page();requests=[];errors=[]
        page.on('request',lambda r:requests.append(urlsplit(r.url).path))
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(self.base,wait_until='networkidle')
        for path in ['/videos.json','/agenda.json','/fil.json']:self.assertNotIn(path,requests)
        page.goto(self.base+'/#videos',wait_until='networkidle')
        self.assertEqual(page.locator('#plus-de-foot').get_attribute('open'),'')
        self.assertTrue(page.locator('#videos').is_visible())
        for path in ['/videos.json','/agenda.json','/fil.json']:self.assertIn(path,requests)
        self.assertEqual(page.locator('.home-more .vm-banner').count(),1)
        self.assertEqual(page.locator('.home-more .promo-entry').count(),1)
        self.assertEqual(errors,[])
        context.close()

    def test_home_displays_only_one_foot_journal_when_youtube_is_confirmed(self):
        context=self.context();page=context.new_page()
        rows=[{'id':'actus-edition-20261023-1900','titre':'Actus seule','universes':['actus'],'edition_at':'2026-10-23T19:00:00+02:00','date_publication':'2026-10-23T19:30:00Z','plateformes':{'youtube':{'url':'https://www.youtube.com/watch?v=aB1cdEF2ghi','status':'published'}}},
              {'id':'foot-edition-20261023-2000','titre':'Le JT Foot de 20 h','universes':['foot'],'edition_at':'2026-10-23T20:00:00+02:00','date_publication':'2026-10-23T18:05:00Z','plateformes':{'youtube':{'url':'https://www.youtube.com/watch?v=aB1cdEF2ghi','status':'published'}}}]
        context.route('**/studio/diffusions.json',lambda route:route.fulfill(json=rows))
        page.goto(self.base,wait_until='networkidle')
        section=page.locator('[data-broadcast-feed]')
        self.assertEqual(section.locator('h2').inner_text(),'Le JT Foot de 20 h')
        self.assertFalse(page.locator('#ptvMain').is_visible())
        self.assertFalse(page.locator('#ptvMore').is_visible())
        self.assertEqual(section.locator('iframe').count(),0)
        section.get_by_role('button',name='▶ Lire ce JT en HD ici').click()
        self.assertIn('youtube-nocookie.com/embed/aB1cdEF2ghi',section.locator('iframe').get_attribute('src'))
        context.close()

if __name__=='__main__':unittest.main(verbosity=2)
