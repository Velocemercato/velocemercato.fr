"""Inventorie les liens des pages et les anomalies de classement pour la reprise Claude."""
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
import sys
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.multisport_flux import relevant

HOSTS = {'velocemercato.fr', 'www.velocemercato.fr'}
SKIP_DIRS = {'.git', '.github', '.devcontainer', 'tests', 'docs', 'tools'}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('name'):
            self.ids.add(attrs['name'])
        if tag in {'a', 'img', 'script', 'link', 'iframe', 'video', 'source'}:
            url = attrs.get('href') if tag in {'a', 'link'} else attrs.get('src')
            if url:
                self.links.append((url, self.getpos()[0], tag))


def resolve(path):
    local = ROOT / unquote(path).lstrip('/')
    if ROOT not in local.resolve().parents and local.resolve() != ROOT:
        return None
    for candidate in (local, Path(str(local) + '.html'), local/'index.html'):
        if candidate.is_file():
            return candidate
    return None


def public_url(url):
    parts = urlsplit(url)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
        return False
    if re.search(r'(?:token|secret|password|signature|access_key)=', parts.query, re.I):
        return False
    try:
        addresses = socket.getaddrinfo(parts.hostname, parts.port or 443, type=socket.SOCK_STREAM)
        return bool(addresses) and all(ipaddress.ip_address(addr[4][0]).is_global for addr in addresses)
    except (OSError, ValueError):
        return False


def check_url(url):
    if not public_url(url):
        return {'url': url, 'status': 'non_teste', 'reason': 'Adresse non publique, protégée ou non résolue'}
    try:
        request = Request(url, headers={'User-Agent': 'VeloceMercato-LinkAudit/1.0', 'Range': 'bytes=0-1023'})
        with urlopen(request, timeout=7) as response:
            response.read(1024)
            return {'url': url, 'status': response.status, 'final_url': response.geturl()}
    except HTTPError as error:
        return {'url': url, 'status': error.code}
    except (OSError, ValueError) as error:
        return {'url': url, 'status': 'non_teste', 'reason': type(error).__name__}


def load_json(path, issues):
    try:
        return json.loads((ROOT/path).read_text())
    except (OSError, ValueError) as error:
        issues.append({'file': path, 'reason': type(error).__name__})
        return None


def main():
    pages = {}
    for path in ROOT.rglob('*.html'):
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        parser = Links()
        parser.feed(path.read_text(encoding='utf-8', errors='replace'))
        pages[path] = parser
    missing = []
    anchors = []
    refs = defaultdict(list)
    for path, parser in pages.items():
        base = 'https://velocemercato.fr/' + path.relative_to(ROOT).as_posix()
        for href, line, tag in parser.links:
            if href.startswith(('data:', 'mailto:', 'tel:', 'sms:', 'javascript:', 'blob:')):
                continue
            target = urlsplit(urljoin(base, href))
            if target.scheme not in {'https', 'http'}:
                continue
            url = urlunsplit((target.scheme, target.netloc, target.path, target.query, ''))
            reference = {'file': str(path.relative_to(ROOT)), 'line': line, 'href': href, 'tag': tag}
            if target.hostname in HOSTS:
                local = resolve(target.path)
                if local is None:
                    missing.append(reference)
                    refs[url].append(reference)
                elif target.fragment and local in pages and unquote(target.fragment) not in pages[local].ids:
                    anchors.append(reference)
                continue
            if tag == 'a':
                refs[url].append(reference)
    issues = []
    feeds = {}
    for file in ('articles.json', 'actus/news.json', 'vm-gaming/news.json', 'multisport/actualites.json', 'studio/diffusions.json'):
        feeds[file] = load_json(file, issues)
    classes = []
    multi = feeds.get('multisport/actualites.json') or {}
    for sport, rows in multi.get('sports', {}).items():
        for row in rows:
            if not relevant(sport, row.get('titre', '')):
                classes.append({'file': 'multisport/actualites.json', 'section': sport, 'title': row.get('titre'), 'url': row.get('url'), 'reason': 'Titre hors discipline ou jeu vidéo'})
    hints = {
        'articles.json': r'foot|ligue|mercato|club|joueur|match|PSG|Mbappé|Lille|Marseille|Lens|UEFA|FIFA|premier league|football|coupe|entra[iî]neur',
        'vm-gaming/news.json': r'jeu|gaming|game|console|playstation|xbox|nintendo|gta|steam|ubisoft|call of duty|ea.?fc|gpu|nvidia|carte graphique|esport|rockstar|IA générative|Kirby|Smash|Roblox|Battlefield',
    }
    checked = {}
    for file, rule in hints.items():
        rows = feeds.get(file)
        rows = rows if isinstance(rows, list) else []
        checked[file] = len(rows)
        for row in rows:
            text = ' '.join(str(row.get(field) or '') for field in ('titre', 'resume', 'texte'))
            if not re.search(rule, text, re.I):
                classes.append({'file': file, 'id': row.get('id'), 'title': row.get('titre'), 'reason': 'À relire, aucun indice net de la rubrique dans la brève'})
    for file in ('articles.json', 'actus/news.json', 'vm-gaming/news.json'):
        for row in feeds.get(file) or []:
            for source in row.get('sources') or []:
                url = source.get('url')
                if url and urlsplit(url).scheme == 'https':
                    refs[url].append({'file': file, 'id': row.get('id'), 'title': row.get('titre')})
    with ThreadPoolExecutor(max_workers=8) as workers:
        checked_links = list(workers.map(check_url, sorted(refs)))
    for item in checked_links:
        item['references'] = refs[item['url']]
    broken = [item for item in checked_links if item['status'] in {404, 410}]
    protected = [item for item in checked_links if item['status'] in {401, 403, 429, 'non_teste'}]
    failures = [item for item in checked_links if isinstance(item['status'], int) and item['status'] >= 500]
    videos = feeds.get('studio/diffusions.json') or []
    replay = Counter(genre for row in videos if any(p.get('status') == 'published' for p in (row.get('plateformes') or {}).values()) for genre in row.get('universes', []))
    report = {'generated_at': datetime.now(ZoneInfo('Europe/Paris')).isoformat(),
              'commit': __import__('os').environ.get('GITHUB_SHA', ''), 'html_pages': len(pages),
              'live_urls_checked': len(checked_links), 'local_targets_absent': missing,
              'anchors_to_review': anchors, 'broken_urls_404_410': broken,
              'protected_or_unverified_urls': protected, 'server_failures': failures,
              'classification_to_review': classes, 'feed_counts': checked, 'replay_by_genre': dict(replay),
              'json_errors': issues, 'all_live_results': checked_links}
    docs = ROOT/'docs'
    docs.mkdir(exist_ok=True)
    (docs/'AUDIT_CLAUDE_2026-11-11.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    lines = ['# Audit du site pour Claude', '', 'État mesuré le '+report['generated_at']+'.', '',
             '## Périmètre et limites', '',
             f'{len(pages)} pages HTML inventoriées. Toutes leurs cibles internes sont contrôlées dans le dépôt. {len(checked_links)} URL uniques issues des liens externes, des cibles internes absentes et des sources des articles sont interrogées en HTTP.', '',
             'Un statut 404 ou 410 indique une URL introuvable. Les refus 401/403, les limites 429, les erreurs serveur et les délais dépassés demandent une vérification complémentaire. Le test ne valide pas le visionnage géographique des vidéos ni la véracité des articles. Les classements signalés par mots-clés doivent être relus avant déplacement.', '',
             '## Reprise de la demande de Romain', '',
             'Retirer les accès transversaux aux anciennes applications et leurs invitations à installer. L’accueil doit commencer directement par le bureau. Garder un retour simple à l’accueil. Corriger tout texte sombre sur fond sombre. Réserver Multisport aux disciplines hors football et aux contenus sportifs réels. Réserver ses Pastilles au genre Multisport. Maintenir les conseils pronos fournis par Romain.', '',
             '## Résultats', '',
             f'- Liens confirmés introuvables en HTTP, {len(broken)}.',
             f'- Cibles internes absentes du dépôt, {len(missing)}. Certaines peuvent être servies par Cloudflare, lire leur résultat HTTP avant correction.',
             f'- Ancres à vérifier, {len(anchors)}. Certaines sont gérées par JavaScript.',
             f'- Articles à relire pour leur classement, {len(classes)}.',
             '- Replays réellement publiés par genre, '+json.dumps(dict(replay),ensure_ascii=False)+'.', '',
             'Le fichier JSON associé contient toutes les références, pages et lignes. Les chemins correspondent au commit indiqué dans ce rapport.', '',
             '## Liens introuvables', '']
    for item in broken:
        lines += ['- '+item['url']+' — HTTP '+str(item['status'])+' — '+', '.join(str(ref.get('file'))+(' ligne '+str(ref['line']) if 'line' in ref else '') for ref in item['references'][:6])]
    lines += ['', '## Articles à relire', '']
    for item in classes:
        lines += ['- '+str(item.get('file'))+' — '+str(item.get('section') or item.get('id') or '')+' — '+str(item.get('title'))+' — '+item['reason']]
    lines += ['', '## Corrections déjà apportées dans cette reprise', '',
              '- Le rendu Multisport ne charge plus fil.json ni une Pastille Foot. Les titres de jeux vidéo sont filtrés dans la collecte et dans les volets.',
              '- Le style commun de lecture impose des couleurs lisibles et masque les anciennes invitations à installer.',
              '- La préparation de publication applique la navigation simplifiée aux pages historiques et aux nouveaux articles.',
              '- Le filtre Multisport existe dans le catalogue des Pastilles. Compléter les vidéos uniquement avec des publications confirmées.', '',
              '## Travail restant pour Claude', '',
              'Corriger les liens confirmés introuvables en s’appuyant sur leur fichier et leur ligne. Relire les anomalies de rubrique avec leurs sources. Contrôler les liens protégés depuis un accès autorisé. Vérifier ensuite l’accueil et les lecteurs sur téléphone. Refaire cet audit après les corrections et publier la version contrôlée.', '',
              'L’en-tête ajouté par une éventuelle transformation Cloudflare doit aussi rester masqué sur le domaine. Les consignes et le contexte sont dans docs/PASSATION_VM_2026-11-10.md.']
    (docs/'AUDIT_CLAUDE_2026-11-11.md').write_text('\n'.join(lines)+'\n')
    print(f'Audit terminé. {len(pages)} pages, {len(checked_links)} URL HTTP, {len(broken)} introuvables, {len(classes)} classements à relire.')


if __name__ == '__main__':
    main()
