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
SCHEDULE = {
    ('meta', 'facebook'): (8, 12, 20),
    ('meta', 'instagram'): (12, 20),
    ('meta_pronos', 'facebook'): (12, 20),
    ('meta_univers', 'facebook'): (8, 12, 18),
    ('meta_univers', 'instagram'): (18,),
}
SLOT_CLOSE_MINUTE = 50
ANGLES = ('Découvre', 'À retrouver dans notre univers', 'Un projet VM à explorer',
          'Le saviez-vous ? Notre projet', 'Focus sur', 'La sélection VM :')


def normal(value):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(value or ''))).strip().casefold()


def fingerprint(value):
    return hashlib.sha256(normal(value).encode()).hexdigest()[:24]


def ledger(state, account):
    return state.data.setdefault('meta' if account == 'meta' else account + '_accuses', {})


def recent_facebook_titles(state, now):
    """Titres confirmés ou incertains aujourd'hui sur les deux Pages Facebook éditoriales."""
    local_day = now.astimezone(PARIS).date()
    statuses = {'publie_confirme', 'envoi', 'envoye_a_verifier', 'a_verifier_sans_renvoi'}
    seen = set()
    for account in ('meta', 'meta_pronos'):
        for key, receipt in ledger(state, account).items():
            if not re.fullmatch(r'editorial/facebook/(?!titre/)[^/]+/[^/]+', key):
                continue
            if not isinstance(receipt, dict) or receipt.get('status') not in statuses:
                continue
            try:
                stamp = dt.datetime.fromisoformat(str(receipt.get('at', '')).replace('Z', '+00:00'))
                if stamp.tzinfo is None or stamp.astimezone(PARIS).date() != local_day:
                    continue
            except (TypeError, ValueError):
                continue
            title = normal(receipt.get('title'))
            if title:
                seen.add(title)
    return seen


def slot_key(now, account, network):
    local = now.astimezone(PARIS)
    if local.hour not in SCHEDULE.get((account, network), ()) or local.minute >= SLOT_CLOSE_MINUTE:
        return None
    local = local.replace(minute=0, second=0, microsecond=0)
    return 'editorial/slot/' + network + '/' + local.isoformat()


def known(done, network, universe, row):
    ident = str(row['id'])
    return any(key in done for key in (
        f'editorial/{network}/{universe}/{ident}',
        f'editorial/{network}/titre/{fingerprint(row["titre"])}',
        (f'article/{universe}/{ident}' if network == 'facebook' else f'insta/{universe}/{ident}'),
        ('article/' + ident if network == 'facebook' else 'insta/' + ident),
        ('post/' + universe + '/' + ident if network == 'facebook' else '__never__')))


def select_news(root, now, done, account, network, seen):
    genres = ROTATIONS[account]
    local = now.astimezone(PARIS)
    cycle = local.date().toordinal() + SCHEDULE[(account, network)].index(local.hour)
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


def select_project(root, now, done, network, seen):
    choices = projects(root)
    if not choices:
        return None
    local = now.astimezone(PARIS)
    for step in range(len(choices) * len(ANGLES)):
        index = local.date().toordinal() + step
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


def publish_target(state, graph, account, network, root=ROOT, now=None,
                   card=instagram_card, project_card=instagram_projet_card, seen_extra=None):
    now = now or dt.datetime.now(UTC)
    slot = slot_key(now, account, network)
    if slot is None:
        return {'status': 'hors_creneau', 'posts': []}
    done = ledger(state, account)
    if slot in done:
        return {'status': 'creneau_deja_traite', 'posts': []}
    meta = state.data.get('tokens', {}).get(account) or {}
    who = identity(graph, meta, account, network)
    seen = current_posts(graph, meta, network) + list(seen_extra or ())
    if network == 'instagram' and not instagram_room(graph, meta):
        return {'status': 'quota_atteint', 'posts': [], 'identity': who}
    choice = (select_project(root, now, done, network, seen) if account == 'meta_univers'
              else select_news(root, now, done, account, network, seen))
    if not choice:
        return {'status': 'aucun_contenu_inedit', 'posts': [], 'identity': who}
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
        link = source['url'] if universe == 'multisport' else article_url(universe, row['id'])
        caption = f'{conf["emoji"]} {clean(row["titre"], 200)}\n\n{clean(row["resume"], 550)}\n\nSource : {clean(source["nom"], 70)}\n👉 {link}\n\n{conf["tags"]}'
    # Un rendu qui échoue n'est pas un envoi tenté.
    image = None
    if network == 'instagram':
        image = (project_card(item['name'], item['icon'], item['pitch']) if universe == 'projet'
                 else card(universe, row, source))
    state.data['editorial/active/' + account] = True
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
    except Exception:
        # Une erreur de transport peut survenir après publication effective.
        mark('a_verifier_sans_renvoi')
        return {'status': 'envoi_a_verifier', 'posts': [], 'identity': who}
    print(f'::notice::{TARGETS[account][1]} / {network} : {url}')
    return {'status': 'publie', 'identity': who,
            'posts': [{'title': row['titre'], 'section': universe, 'id': ident, 'url': url}]}


def run(state, graph, root=ROOT, now=None):
    now = now or dt.datetime.now(UTC)
    result = {'updated_at': now.isoformat(), 'mode': 'programme',
              'targets': {}, 'unconnected': ['Troisième compte Instagram : identité et connexion absentes.']}
    targets = [(account, network) for account, network in SCHEDULE if slot_key(now, account, network)]
    if not targets:
        return result
    # Scope validé : exactement trois Pages Facebook et deux comptes Instagram.
    result = {'updated_at': now.isoformat(), 'mode': 'programme',
              'targets': {}, 'unconnected': []}
    targets = [(account, network) for account, network in SCHEDULE if slot_key(now, account, network)]
    if not targets:
        return result
    ensure_meta_targets(state)
    # Une même brève ne doit pas être publiée le même jour sur les deux Pages Facebook.
    # Les envois incertains restent réservés jusqu'à une vérification des accusés.
    fb_seen = recent_facebook_titles(state, now)
    for account, network in targets:
        try:
            extra = fb_seen if network == 'facebook' and account in ('meta', 'meta_pronos') else None
            item = publish_target(state, graph, account, network, root, now, seen_extra=extra)
            result['targets'][account + '/' + network] = item
            if network == 'facebook' and account in ('meta', 'meta_pronos'):
                fb_seen.update(recent_facebook_titles(state, now))
                for post in item.get('posts', []):
                    title = normal(post.get('title'))
                    if title:
                        fb_seen.add(title)
        except Exception as error:
            detail = re.sub(r'EA[A-Za-z0-9]{20,}|access_token=[^&\\s]+', '[masqué]', str(error))[:240]
            result['targets'][account + '/' + network] = {'status': 'bloque', 'reason': type(error).__name__,
                                                          'detail': detail, 'posts': []}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    # Une exécution déjà planifiée peut encore transmettre cet ancien argument.
    parser.add_argument('--burst', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    result = run(state, Graph())
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
