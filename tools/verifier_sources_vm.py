#!/usr/bin/env python3
"""Découvre les RSS déclarés par les éditeurs. Aucun contournement des refus robots ou abonnements."""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import update_news as robot


class Discovery(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and 'alternate' in a.get('rel', '').lower() and ('rss' in a.get('type', '') or 'atom' in a.get('type', '')):
            self.urls.append(a.get('href', ''))


def same_publisher(url, home):
    parsed = urlsplit(url)
    host = (parsed.hostname or '').removeprefix('www.')
    parent = (urlsplit(home).hostname or '').removeprefix('www.')
    return parsed.scheme == 'https' and not parsed.username and not parsed.password and (host == parent or host.endswith('.' + parent))


def check(row):
    out = dict(row)
    if row.get('manual'):
        return {**out, 'status': 'validation_editoriale_requise'}
    candidates = list(row.get('feeds', []))
    try:
        if not robot.can_fetch(row['home']):
            return {**out, 'status': 'robots_ou_acces_non_autorise'}
        page = robot.request_bytes(row['home'], limit=1_000_000, timeout=10)
        parser = Discovery()
        parser.feed(page.decode('utf-8', errors='replace'))
        candidates.extend(urljoin(row['home'], value) for value in parser.urls)
        for feed in list(dict.fromkeys(candidates))[:6]:
            if not same_publisher(feed, row['home']) or not robot.can_fetch(feed):
                continue
            try:
                data = robot.request_bytes(feed, limit=2_000_000, timeout=10)
                xml = ET.fromstring(data)
                items = xml.findall('.//item') or xml.findall('{http://www.w3.org/2005/Atom}entry')
                if items:
                    return {**out, 'status': 'valide', 'feed': feed, 'items': len(items)}
            except Exception:
                continue
        return {**out, 'status': 'aucun_flux_public_valide'}
    except Exception as error:
        return {**out, 'status': 'acces_a_verifier', 'reason': type(error).__name__}


def main():
    requested = json.loads((ROOT/'sources/demandees-romain.json').read_text())
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(check, requested['sources']))
    data = {'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'sources': rows}
    (ROOT/'sources/flux-valides.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print('Sources contrôlées :', len(rows), '; flux publics validés :', sum(r['status'] == 'valide' for r in rows))


if __name__ == '__main__':
    main()
