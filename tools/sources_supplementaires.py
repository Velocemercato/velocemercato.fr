"""Sources demandées par Romain, utilisables seulement après validation du flux public."""
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def feeds(section):
    try:
        data = json.loads((ROOT/'sources/flux-valides.json').read_text())
    except (OSError, ValueError):
        return [], set()
    rows, hosts = [], set()
    for row in data.get('sources', []):
        if row.get('status') != 'valide' or section not in row.get('sections', []):
            continue
        url = str(row.get('feed', ''))
        host = urlsplit(url).hostname or ''
        publisher = urlsplit(str(row.get('home', ''))).hostname or ''
        if not host or not publisher or not url.startswith('https://'):
            continue
        host = host.removeprefix('www.')
        publisher = publisher.removeprefix('www.')
        if host != publisher and not host.endswith('.' + publisher):
            continue
        zone, category = ('INTERNATIONAL','INTERNATIONAL') if section == 'foot' else ('GAMING','GAMING') if section == 'gaming' else ('MONDE','INTERNATIONAL')
        rows.append((zone, category, row['name'], url))
        hosts.add(host)
        hosts.add(publisher)
    return rows, hosts
