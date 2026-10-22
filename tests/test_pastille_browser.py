"""Lecture réelle H.264 sur un média de test local, sans publication ni partage externe."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import test_site as site


class PlayerTests(unittest.TestCase):
    context = site.SiteTests.context

    @classmethod
    def setUpClass(cls):
        site.SiteTests.setUpClass()
        cls.browser,cls.base=site.SiteTests.browser,site.SiteTests.base
        cls.folder=tempfile.TemporaryDirectory()
        file=Path(cls.folder.name)/'fixture.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:s=320x180:r=24',
                        '-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','4','-c:v','libx264',
                        '-threads','2','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(file)],check=True)
        cls.media=file.read_bytes()
        cls.rows=json.loads((site.ROOT/'studio/emissions.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()
        site.SiteTests.tearDownClass()

    def playback_context(self,width=390):
        context=self.context(width)
        def serve(route):
            if route.request.url.endswith(('.mp4','.m4a')):
                data=self.media;headers={'content-type':'video/mp4','accept-ranges':'bytes'}
                request=route.request.headers.get('range','')
                if request:
                    bounds=request.split('=',1)[1].split('-',1)
                    start=int(bounds[0]);end=min(int(bounds[1]) if bounds[1] else len(data)-1,len(data)-1)
                    headers['content-range']=f'bytes {start}-{end}/{len(data)}'
                    route.fulfill(status=206,headers=headers,body=data[start:end+1])
                else:route.fulfill(status=200,headers=headers,body=data)
            else:
                path=site.ROOT/'studio/episodes/posters'/route.request.url.rsplit('/',1)[1]
                route.fulfill(path=str(path),content_type='image/jpeg') if path.is_file() else route.abort()
        context.route('https://cdn.jsdelivr.net/gh/**',serve)
        return context

    def test_selected_episode_speed_share_and_no_reset(self):
        context=self.playback_context();page=context.new_page();episode=self.rows[1]
        page.add_init_script("Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{window.sharedEpisode=data}})")
        page.goto(self.base+'/studio.html?episode='+episode['id']+'#tv',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#tvVideo').readyState>=2")
        self.assertEqual(page.locator('#tvVideo').get_attribute('data-episode'),episode['id'])
        self.assertAlmostEqual(page.locator('#tvVideo').evaluate('video=>video.playbackRate'),1.15)
        page.get_by_role('button',name='Partager cette émission').click()
        self.assertEqual(page.evaluate('sharedEpisode.url'),episode['page'])
        page.locator('#tvVideo').evaluate('video=>{video.currentTime=1;return video.play()}')
        page.locator(f'.tv-list button[data-id="{episode["id"]}"]').click()
        self.assertGreater(page.locator('#tvVideo').evaluate('video=>video.currentTime'),0.8)
        self.assertEqual(page.locator('.pastille-tools').count(),1)
        page.locator('#tvVideo').evaluate('video=>video.pause()')
        page.get_by_role('combobox',name='Vitesse de lecture').select_option('1.25')
        self.assertEqual(page.locator('#tvVideo').evaluate('video=>video.playbackRate'),1.25)
        self.assertEqual(page.locator('#tvViews').count(),0)
        context.close()

    def test_gaming_article_link_opens_the_selected_actual_article(self):
        context=self.context();page=context.new_page()
        news=json.loads((site.ROOT/'vm-gaming/news.json').read_text())
        article=next(row for row in news if row.get('titre') and row.get('publishedAt'))
        page.goto(self.base+'/vm-gaming/#a='+article['id'],wait_until='networkidle')
        detail=page.locator('[id="a-'+article['id']+'"]')
        self.assertTrue(detail.evaluate('element=>element.open'))
        self.assertIn(article['titre'],detail.inner_text())
        page.locator('#vmFab').click()
        self.assertIn('#a='+article['id'],page.locator('#vmS-fb').get_attribute('href').replace('%23','#').replace('%3D','='))
        context.close()

    def test_long_programme_card_shows_only_confirmed_public_links(self):
        context=self.context();page=context.new_page()
        rows=[{'id':'foot-speciale-20261022-2100','date_publication':'2026-10-22T21:00:00Z','universes':['foot'],'titre':'Spéciale Foot seule','plateformes':{'youtube':{'status':'published','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}}},
              {'id':'jt-2026-10-23-soir','titre':'Vidéo privée invisible','plateformes':{'youtube':{'status':'private','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}}},
              {'id':'jt-2026-10-22-soir','titre':'Le grand JT <script>test</script>','plateformes':{'youtube':{'status':'published','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}}}]
        context.route('**/studio/diffusions.json',lambda route:route.fulfill(json=rows))
        page.goto(self.base+'/actus/',wait_until='networkidle')
        section=page.locator('[data-broadcast-feed]')
        self.assertTrue(section.is_visible())
        self.assertEqual(section.locator('h2').text_content(),'Le grand JT <script>test</script>')
        self.assertEqual(section.locator('a').get_attribute('href'),'https://www.youtube.com/watch?v=aB1cdEF2ghi')
        self.assertEqual(section.locator('script,iframe').count(),0)
        page.goto(self.base,wait_until='networkidle')
        self.assertEqual(page.locator('[data-broadcast-feed] h2').text_content(),'Spéciale Foot seule')
        context.close()

    def test_static_share_page_without_javascript(self):
        context=self.browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(self.base+'/') else route.abort())
        page=context.new_page();episode=self.rows[1]
        page.goto(self.base+'/studio/episodes/'+episode['id']+'.html',wait_until='domcontentloaded')
        self.assertEqual(page.locator('h1').inner_text(),episode['titre'])
        self.assertEqual(page.locator('meta[property="og:url"]').get_attribute('content'),episode['page'])
        image=page.locator('meta[property="og:image"]').get_attribute('content')
        self.assertTrue(image.startswith('https://velocemercato.fr/studio/episodes/posters/'))
        self.assertEqual(page.locator('video source').get_attribute('src'),episode['video'])
        context.close()

    def test_loading_errors_are_visible(self):
        context=self.context();page=context.new_page()
        page.goto(self.base+'/studio.html',wait_until='networkidle')
        page.wait_for_function("document.querySelector('.pastille-status')?.textContent.includes('ne se charge pas')")
        self.assertTrue(page.get_by_role('link',name='Ouvrir le MP4').is_visible())
        context.close()

    def test_legacy_hash_and_lazy_home_video(self):
        context=self.playback_context();page=context.new_page();episode=self.rows[2]
        page.goto(self.base+'/studio.html#tv='+episode['id'],wait_until='networkidle')
        self.assertEqual(page.locator('#tvVideo').get_attribute('data-episode'),episode['id'])
        page.goto(self.base,wait_until='networkidle')
        self.assertIsNone(page.locator('#homePastilleVideo').get_attribute('src'))
        page.locator('#homePastilleVideo').scroll_into_view_if_needed()
        page.wait_for_function("!!document.querySelector('#homePastilleVideo').src")
        context.close()

    def test_news_sites_show_their_actual_published_journal(self):
        for width in [390,1440]:
            for path,universe in [('actus','actus'),('vm-gaming','gaming'),('belfort','actus')]:
                with self.subTest(width=width,path=path):
                    context=self.playback_context(width);page=context.new_page();errors=[]
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    page.goto(self.base+'/'+path+'/',wait_until='networkidle')
                    section=page.locator('[data-pastille-universe]')
                    actual=next(row for row in self.rows if row['univers']==universe and row['publie'])
                    self.assertEqual(section.locator('h2').inner_text(),actual['titre'])
                    self.assertEqual(section.locator('a').first.get_attribute('href'),actual['page'])
                    box=section.bounding_box();self.assertLessEqual(box['x']+box['width'],width)
                    self.assertFalse(errors,errors)
                    context.close()


if __name__=='__main__':unittest.main(verbosity=2)
