#!/usr/bin/env python3
"""Circuit éditorial central. Accusé avant envoi, confirmation après, jamais de retry ambigu."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import (Graph, UNIVERS, PROJETS, article, article_url, clean,
                                instagram_card, instagram_projet_card, instagram_image,
                                ensure_meta_targets)

PARIS = ZoneInfo('Europe/Paris')
UTC = dt.timezone.utc
TARGETS = {
    'meta': ('1384363904759072', 'Véloce Mercato', 'veloce.mercato'),
    'meta_pronos': ('112294796981981', 'VM Actus et Pronos', None),
    'meta_univers': ('1349998758205153', 'VM Univers', 'vmunivers.fr'),
}
ROTATIONS = {'meta': ('foot', 'multisport'),
             'meta_pronos': ('actus', 'gaming', 'multisport', 'actus', 'foot')}
ANGLES = ('Découvre', 'À retrouver dans notre univers', 'Un projet VM à explorer',
          'Le saviez-vous ? Notre projet', 'Focus sur', 'La sélection VM :')


def normal(value):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(value or ''))).strip().casefold()


def fingerprint(value):
    return hashlib.sha256(normal(value).encode()).hexdigest()[:24]


def ledger(state, account):
    return state.data.setdefault('meta' if account == 'meta' else account + '_accuses', {})


def slot_key(now, account, network):
    local = now.astimezone(PARIS)
    minutes = 60 if account == 'meta_univers' and network == 'facebook' else (10 if network == 'facebook' else 15)
    # Le décalage UTC de l'heure locale distingue les deux heures du changement d'heure.
    local = local.replace(minute=(local.minute // minutes) * minutes, second=0, microsecond=0)
    return 'editorial/slot/' + network + '/' + local.isoformat()


def known(done, network, universe, row):
    ident = str(row['id'])
    return any(key in done for key in (
        f'editorial/{network}/{universe}/{ident}',
        f'editorial/{network}/titre/{fingerprint(row["titre"])}',
        (f'article/{universe}/{ident}' if network == 'facebook' else f'insta/{universe}/{ident}'),
        ('article/' + ident if network == 'facebook' else 'insta/' + ident),
        ('post/' + universe + '/' + ident if network == 'facebook' else '__never__')))


def select_news(root, now, done, account, network, seen, offset=0):
    genres = ROTATIONS[account]
    cycle = int(now.timestamp() // (600 if network == 'facebook' else 900)) + offset
    genres = genres[cycle % len(genres):] + genres[:cycle % len(genres)]
    for universe in dict.fromkeys(genres):
        excluded = dict(done)
        # Respecter le filtrage Multisport commun, même dans un ancien JSON.
        for _ in range(250):
            row, source = article(root, now, excluded, universe, hours=24)
            if not row:
                break
            excluded[f'article/{universe}/{row["id"]}'] = True
            title = normal(row['titre'])
            if known(done, network, universe, row) or any(title in text for text in seen):
                continue
            if universe == 'multisport':
                from tools.multisport_flux import GAMING_CONTENT
                if re.search(GAMING_CONTENT, row['titre'], re.I):
                    continue
            return universe, row, source
    return None


def projects(root):
    out = []
    for name, icon, path, pitch in PROJETS:
        local = Path(root) / path.lstrip('/').split('#')[0]
        if local.is_dir():
            local = local / 'index.html'
        if not local.is_file():
            continue
        out.append({'name': name, 'icon': icon, 'url': 'https://velocemercato.fr' + path, 'pitch': pitch})
    return out


def select_project(root, now, done, network, seen, offset=0):
    choices = projects(root)
    if not choices:
        return None
    local = now.astimezone(PARIS)
    for step in range(len(choices) * len(ANGLES)):
        index = local.hour + offset + step
        item = choices[index % len(choices)]
        angle = ANGLES[(index // len(choices)) % len(ANGLES)]
        title = angle + ' ' + item['name']
        ident = f'projet-{local:%Y%m%d}-{index % (len(choices) * len(ANGLES))}'
        row = {'id': ident, 'titre': title, 'resume': item['pitch'], 'project': item}
        if not known(done, network, 'projet', row) and not any(normal(title) in text for text in seen):
            return 'projet', row, {'nom': 'VM Univers', 'url': item['url']}
    return None


def identity(graph, meta, account, network):
    expected, _, username = TARGETS[account]
    if str(meta.get('page_id')) != expected or not meta.get('page_token'):
        raise DeliveryError('Connexion Meta absente ou mauvaise destination.')
    if network == 'facebook':
        proof = graph.call('GET', expected, {'fields': 'id,name', 'access_token': meta['page_token']})
        if str(proof.get('id')) != expected:
            raise DeliveryError('Identité Facebook non confirmée.')
        return {'id': expected, 'name': proof.get('name', '')}
    if not username or not meta.get('ig_id'):
        raise DeliveryError('Instagram non connecté à cette destination.')
    proof = graph.call('GET', str(meta['ig_id']), {'fields': 'id,username', 'access_token': meta['page_token']})
    if str(proof.get('id')) != str(meta['ig_id']) or normal(proof.get('username')) != normal(username):
        raise DeliveryError('Identité Instagram différente du compte demandé.')
    return {'id': str(meta['ig_id']), 'name': proof['username']}


def current_posts(graph, meta, network):
    ident = meta['page_id'] if network == 'facebook' else meta['ig_id']
    fields = 'message,created_time,permalink_url' if network == 'facebook' else 'caption,timestamp,permalink'
    edge = '/published_posts' if network == 'facebook' else '/media'
    response = graph.call('GET', str(ident) + edge, {'fields': fields, 'limit': 100, 'access_token': meta['page_token']})
    rows = response.get('data')
    if not isinstance(rows, list):
        raise DeliveryError('Historique de publication non vérifiable.')
    return [normal(row.get('message') or row.get('caption')) for row in rows]


def instagram_room(graph, meta):
    data = graph.call('GET', str(meta['ig_id']) + '/content_publishing_limit',
                      {'fields': 'quota_usage,config', 'access_token': meta['page_token']}).get('data')
    if not isinstance(data, list) or not data or not isinstance(data[0].get('quota_usage'), int):
        raise DeliveryError('Quota Instagram non vérifiable.')
    info = data[0]
    total = int((info.get('config') or {}).get('quota_total', 100))
    return max(0, total - info['quota_usage'])


def confirm(graph, meta, network, ident):
    if network == 'facebook':
        if not re.fullmatch(re.escape(str(meta['page_id'])) + r'_[0-9]+', ident):
            raise DeliveryError('Accusé Facebook invalide.')
        proof = graph.call('GET', ident, {'fields': 'id,from{id},permalink_url', 'access_token': meta['page_token']})
        url = proof.get('permalink_url', '')
        if str(proof.get('id')) != ident or str((proof.get('from') or {}).get('id')) != str(meta['page_id']):
            raise DeliveryError('Propriétaire du post non confirmé.')
        if not re.match(r'https://(?:www\.|m\.)?facebook\.com/', url):
            raise DeliveryError('URL Facebook non confirmée.')
    else:
        if not ident.isdigit():
            raise DeliveryError('Accusé Instagram invalide.')
        proof = graph.call('GET', ident, {'fields': 'id,permalink', 'access_token': meta['page_token']})
        url = proof.get('permalink', '')
        if str(proof.get('id')) != ident or not url.startswith('https://www.instagram.com/'):
            raise DeliveryError('URL Instagram non confirmée.')
    return url


def publish_target(state, graph, account, network, root=ROOT, now=None, count=1,
                   burst=False, card=instagram_card, project_card=instagram_projet_card):
    now = now or dt.datetime.now(UTC)
    meta = state.data.get('tokens', {}).get(account) or {}
    who = identity(graph, meta, account, network)
    seen = current_posts(graph, meta, network)
    done = ledger(state, account)
    slot = slot_key(now, account, network)
    if not burst and slot in done:
        return {'status': 'creneau_deja_traite', 'posts': [], 'identity': who}
    room = instagram_room(graph, meta) if network == 'instagram' else count
    state.data['editorial/active/' + account] = True
    state.save()
    sent = []
    for index in range(min(count, room)):
        choice = (select_project(root, now, done, network, seen, index) if account == 'meta_univers'
                  else select_news(root, now, done, account, network, seen, index))
        if not choice:
            break
        universe, row, source = choice
        key = f'editorial/{network}/{universe}/{row["id"]}'
        title_key = f'editorial/{network}/titre/{fingerprint(row["titre"])}'
        def mark(status, **extra):
            receipt = {'status': status, 'at': now.isoformat(), 'title': row['titre'], **extra}
            done[key] = receipt
            done[title_key] = receipt
            done[slot] = receipt
            state.save()
        if universe == 'projet':
            item = row['project']
            caption = f'✨ {row["titre"]}\n\n{item["pitch"]}\n\n👉 {item["url"]}\nTous nos projets : https://vmunivers.fr/\n\n#VMUnivers #Projets #VeloceMercato'
            link = item['url']
        else:
            conf = UNIVERS[universe]
            caption = f'{conf["emoji"]} {clean(row["titre"], 200)}\n\n{clean(row["resume"], 550)}\n\nSource : {clean(source["nom"], 70)}\n👉 https://{conf["site"]}\n\n{conf["tags"]}'
            link = source['url'] if universe == 'multisport' else article_url(universe, row['id'])
        # Image créée avant de réserver l'envoi : un échec de rendu n'est pas un post tenté.
        image = None
        if network == 'instagram':
            image = (project_card(item['name'], item['icon'], item['pitch']) if universe == 'projet'
                     else card(universe, row, source))
        mark('envoi')
        try:
            if network == 'facebook':
                ident = str(graph.call('POST', meta['page_id'] + '/feed',
                                      {'message': caption, 'link': link, 'access_token': meta['page_token']}).get('id') or '')
            else:
                ident = str(instagram_image(graph, meta, image, caption) or '')
            mark('envoye_a_verifier', id=ident)
            url = confirm(graph, meta, network, ident)
            mark('publie_confirme', id=ident, url=url)
            sent.append({'title': row['titre'], 'section': universe, 'id': ident, 'url': url})
            seen.append(normal(caption))
            print(f'::notice::{TARGETS[account][1]} / {network} : {url}')
        except Exception:
            # Même une erreur de transport peut survenir après publication effective : ne pas relancer.
            mark('a_verifier_sans_renvoi')
            return {'status': 'envoi_a_verifier', 'posts': sent, 'identity': who}
    return {'status': 'publie' if sent else ('quota_atteint' if not room else 'aucun_contenu_inedit'),
            'posts': sent, 'identity': who}


def run(state, graph, root=ROOT, now=None, burst=False):
    now = now or dt.datetime.now(UTC)
    ensure_meta_targets(state)
    result = {'updated_at': now.isoformat(), 'mode': 'rattrapage_10' if burst else 'programme',
              'targets': {}, 'unconnected': ['Troisième compte Instagram : identité et connexion absentes.']}
    batch = 'editorial/lot-demarre-2026-11-11'
    # Une correction peut reprendre les seules destinations incomplètes du même lot.
    # Les envois ambigus comptent comme tentés ; aucun contenu déjà tenté n'est renvoyé.
    if burst and not state.data.get(batch):
        state.data[batch] = {'at': now.isoformat()}
        state.save()
    for account in TARGETS:
        for network in ('facebook', 'instagram'):
            if account == 'meta_pronos' and network == 'instagram':
                continue
            count = 1
            if burst:
                started = state.data[batch]['at']
                attempted = sum(1 for key, value in ledger(state, account).items()
                                if key.startswith('editorial/' + network + '/')
                                and not key.startswith('editorial/' + network + '/titre/')
                                and isinstance(value, dict) and value.get('at', '') >= started)
                count = max(0, 10 - attempted)
                if not count:
                    result['targets'][account + '/' + network] = {'status': 'lot_deja_traite', 'posts': []}
                    continue
            try:
                result['targets'][account + '/' + network] = publish_target(
                    state, graph, account, network, root, now, count, burst=burst)
            except Exception as error:
                result['targets'][account + '/' + network] = {'status': 'bloque', 'reason': type(error).__name__, 'posts': []}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--burst', action='store_true')
    args = parser.parse_args()
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    result = run(state, Graph(), burst=args.burst)
    confirmed = []
    for account in TARGETS:
        for key, receipt in ledger(state, account).items():
            match = re.fullmatch(r'editorial/(facebook|instagram)/(?!titre/)([^/]+)/([^/]+)', key)
            if not match or not isinstance(receipt, dict) or receipt.get('status') != 'publie_confirme':
                continue
            url = str(receipt.get('url', ''))
            if not re.match(r'https://(?:www\.|m\.)?(?:facebook|instagram)\.com/', url):
                continue
            confirmed.append({'target': account+'/'+match[1], 'title': receipt.get('title',''),
                              'section':match[2], 'id':receipt.get('id',''), 'url':url, 'date':receipt.get('at','')})
    result['confirmed'] = sorted(confirmed,key=lambda row:row['date'],reverse=True)[:500]
    path = ROOT/'studio/editorial-status.json'
    path.parent.mkdir(exist_ok=True)
    if path.exists():
        previous = json.loads(path.read_text())
        result['history'] = ([{k: v for k, v in previous.items() if k != 'history'}] + previous.get('history', []))[:300]
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    posts = sum(len(item.get('posts', [])) for item in result.get('targets', {}).values())
    print(f'Bilan : {posts} publications confirmées. Les autres statuts sont dans studio/editorial-status.json.')


if __name__ == '__main__':
    main()
