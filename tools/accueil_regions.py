"""Publie les titres des flux publics régionaux de France Télévisions."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree

REGIONS = (
    'auvergne-rhone-alpes', 'bourgogne-franche-comte', 'bretagne', 'centre-val-de-loire',
    'corse', 'grand-est', 'hauts-de-france', 'paris-ile-de-france', 'normandie',
    'nouvelle-aquitaine', 'occitanie', 'pays-de-la-loire', 'provence-alpes-cote-d-azur',
    'outre-mer',
)
HOSTS = {'france3-regions.franceinfo.fr', 'la1ere.franceinfo.fr', 'www.franceinfo.fr'}
OUT = Path(__file__).resolve().parents[1] / 'actus' / 'regions-accueil.json'


def headlines(region):
    source = 'France 3'
    url = f'https://france3-regions.franceinfo.fr/{region}/rss'
    if region == 'outre-mer':
        source = 'franceinfo'
        url = 'https://www.franceinfo.fr/france/outre-mer.rss'
    request = Request(url, headers={'User-Agent': 'Veloce Mercato RSS reader'})
    try:
        with urlopen(request, timeout=12) as response:
            if urlsplit(response.geturl()).hostname not in HOSTS:
                raise ValueError('Redirection hors source')
            root = ElementTree.fromstring(response.read(1_000_000))
        articles = []
        for item in root.findall('./channel/item'):
            title = ' '.join((item.findtext('title') or '').split())
            href = (item.findtext('link') or '').strip()
            target = urlsplit(href)
            if title and target.scheme == 'https' and target.hostname in HOSTS:
                articles.append({'title': title, 'url': href, 'source': source,
                                 'date': item.findtext('pubDate')})
            if len(articles) >= 30:
                break
        return region, articles
    except (OSError, ValueError, ElementTree.ParseError) as error:
        print(f'{region} : flux indisponible ({error})')
        return region, []


def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    with ThreadPoolExecutor(max_workers=8) as workers:
        for region, rows in workers.map(headlines, REGIONS):
            if rows:
                old[region] = rows
    if old:
        OUT.write_text(json.dumps(old, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
    print(f'{len(old)}/{len(REGIONS)} flux régionaux disponibles')


if __name__ == '__main__':
    main()
