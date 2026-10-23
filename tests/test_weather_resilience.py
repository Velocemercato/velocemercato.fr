"""Données météo absentes, réseau indisponible et réponses arrivant dans le désordre."""
import unittest
from urllib.parse import parse_qs, urlsplit
import test_site as site


def weather(value=14):
    return {'current': {'time':'2026-10-23T14:00','temperature_2m':value,'apparent_temperature':value,'weather_code':3,'wind_speed_10m':value,'relative_humidity_2m':value},
            'daily': {'time':['2026-10-23']*7,'weather_code':[3]*7,'temperature_2m_max':[value]*7,'temperature_2m_min':[value]*7,'precipitation_probability_max':[value]*7},
            'hourly': {'time':[f'2026-10-23T{h:02d}:00' for h in range(24)],'weather_code':[3]*24,'temperature_2m':[value]*24,'precipitation_probability':[value]*24}}


class WeatherResilienceTests(unittest.TestCase):
    setUpClass=classmethod(site.SiteTests.setUpClass.__func__)
    tearDownClass=classmethod(site.SiteTests.tearDownClass.__func__)
    context=site.SiteTests.context

    def serve(self, route, value=14):
        count=len(parse_qs(urlsplit(route.request.url).query)['latitude'][0].split(','))
        row=weather(value)
        route.fulfill(json=[row]*count if count>1 else row)

    def test_missing_measurements_never_become_zero(self):
        context=self.context();context.route('https://api.open-meteo.com/**',lambda r:self.serve(r,None))
        page=context.new_page();page.goto(self.base+'/meteo/',wait_until='networkidle')
        self.assertEqual(page.locator('#villes .ville strong').first.inner_text(),'—')
        page.locator('#villes .ville').first.click()
        page.wait_for_selector('#detail .days')
        self.assertNotIn('0°',page.locator('#detail').inner_text())
        self.assertNotIn('0%',page.locator('#detail').inner_text())
        self.assertNotIn('NaN',page.locator('#detail').inner_text())
        context.close()

    def test_failed_weather_can_be_retried(self):
        context=self.context();failed=[True]
        context.route('https://api.open-meteo.com/**',lambda r:r.fulfill(status=503,json={}) if failed[0] else self.serve(r))
        page=context.new_page();page.goto(self.base+'/meteo/',wait_until='networkidle')
        self.assertTrue(page.get_by_role('button',name='Réessayer la météo',exact=True).is_visible())
        failed[0]=False;page.get_by_role('button',name='Réessayer la météo',exact=True).click()
        page.wait_for_selector('#villes .ville')
        self.assertEqual(page.locator('#villes .ville').count(),16)
        self.assertIn('14°',page.locator('#villes').inner_text())
        context.close()

    def test_last_city_selection_wins_over_slow_response(self):
        context=self.context();held=[];details=[0]
        def reply(route):
            query=parse_qs(urlsplit(route.request.url).query)
            if query.get('forecast_days')==['7']:
                details[0]+=1
                if details[0]==1:held.append(route);return
            self.serve(route,22)
        context.route('https://api.open-meteo.com/**',reply)
        page=context.new_page();page.goto(self.base+'/meteo/',wait_until='networkidle')
        name=page.locator('#villes .ville b').nth(1).inner_text()
        page.locator('#villes .ville').first.click()
        page.locator('#villes .ville').nth(1).click()
        page.wait_for_selector('#detail .days')
        self.assertTrue(held)
        self.serve(held[0],8)
        page.wait_for_load_state('networkidle')
        self.assertEqual(page.locator('#detail h2').inner_text(),name)
        self.assertIn('22°',page.locator('#detail .big').inner_text())
        context.close()

if __name__=='__main__':unittest.main(verbosity=2)
