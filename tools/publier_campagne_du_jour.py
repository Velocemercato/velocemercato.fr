#!/usr/bin/env python3
"""Publie le jour prévu dans campagnes/calendrier.json (heure de Paris), une seule fois.

Facebook + Instagram de Véloce Mercato et VM Univers (jamais RQ Pronos) :
  - jour « reel »   : vidéo Facebook + Reel Instagram + story Instagram
  - sinon           : photo Facebook + photo Instagram + story Instagram
  - « youtube_short » : Short envoyé directement en public (le dimanche, sans Short de JT).
Garde-fous : calendrier « actif », jour « pret », Pages exactes, médias publics vérifiés,
accusé chiffré écrit AVANT chaque envoi (jamais de doublon), aucun identifiant modifié.
Les liens publics obtenus sont ajoutés à campagnes/journal.json.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import HTTP, State, YouTube, DeliveryError, access_token, git_save
from tools.publier_meta import Graph, instagram_image, instagram_reel, ensure_meta_targets
from tools.campagne_quotidienne import CAL, files

SITE = 'https://velocemercato.fr/'
JOURNAL = ROOT / 'campagnes/journal.json'
EXPECTED = {'meta': '1384363904759072', 'meta_univers': '1349998758205153'}
KEY = 'campagne_quotidienne'


def note(text):
    print('::notice::' + text, flush=True)


def ig_text(text):
    """Instagram ne rend pas les liens cliquables : domaines en clair et lien dans la bio."""
    out = re.sub(r'👉 https?://(\S+?)/?(\s)', r'🔗 \1 (lien dans la bio)\2', text)
    return re.sub(r'https?://(\S+?)/?(?=[\s:]|$)', r'\1', out)


def today_entry(now=None):
    cal = json.loads(CAL.read_text(encoding='utf-8'))
    if cal.get('actif') is not True:
        note('Campagne quotidienne désactivée (actif: false) : rien à publier.')
        return None
    day = (now or datetime.now(ZoneInfo('Europe/Paris'))).date().isoformat()
    entry = next((d for d in cal.get('jours', []) if d.get('date') == day), None)
    if not entry:
        print('::warning::Aucun contenu prévu pour ' + day + ' : préparer les jours suivants du calendrier.', flush=True)
        return None
    if entry.get('statut') != 'pret':
        note(f'{day} en statut « {entry.get("statut")} » : rien publié.')
        return None
    return entry


def confirm_public(urls):
    for link, kind in urls:
        for attempt in range(18):
            try:
                req = urllib.request.Request(link, method='HEAD', headers={'User-Agent': 'VM-Campagne/1'})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    if resp.status == 200 and (resp.headers.get('Content-Type') or '').startswith(kind):
                        break
            except Exception:
                pass
            if attempt == 17:
                raise DeliveryError('Média public indisponible : ' + link.rsplit('/', 1)[-1])
            time.sleep(10)
    note('Médias publics vérifiés')


def action(state, key, callback, journal):
    done = state.data.setdefault(KEY, {})
    previous = done.get(key, {})
    if previous.get('status') in ('envoi', 'publie'):
        note('Déjà traité, aucun nouvel envoi : ' + key)
        return
    done[key] = {'status': 'envoi'}
    state.save()
    try:
        ident, url = callback()
        if not ident:
            raise DeliveryError('aucun identifiant de publication retourné')
        done[key] = {'status': 'publie', 'id': str(ident), 'url': url or ''}
        state.save()
        journal.append({'cle': key, 'statut': 'publie', 'lien': url or ''})
        note('PUBLIÉ ' + key + ' → ' + (url or 'publié (lien non communiqué)'))
    except Exception as ex:
        reason = (str(ex) if isinstance(ex, DeliveryError) else type(ex).__name__)[:170]
        done[key] = {'status': 'echec', 'raison': reason}
        state.save()
        journal.append({'cle': key, 'statut': 'echec', 'raison': reason})
        print('::error::Échec ' + key + ' : ' + reason, flush=True)


def permalink(graph, ident, field, token):
    try:
        return graph.call('GET', ident, {'fields': field, 'access_token': token}).get(field, '')
    except DeliveryError:
        return ''


def ig_story(graph, meta, image_url):
    created = graph.call('POST', meta['ig_id'] + '/media', {'media_type': 'STORIES', 'image_url': image_url, 'access_token': meta['page_token']})
    container = created.get('id')
    if not container:
        raise DeliveryError('Story : préparation non confirmée')
    for _ in range(24):
        status = graph.call('GET', container, {'fields': 'status_code', 'access_token': meta['page_token']}).get('status_code')
        if status in (None, 'FINISHED'):
            break
        if status in ('ERROR', 'EXPIRED'):
            raise DeliveryError('Story refusée par Instagram')
        time.sleep(5)
    else:
        raise DeliveryError('Story encore en traitement')
    return graph.call('POST', meta['ig_id'] + '/media_publish', {'creation_id': container, 'access_token': meta['page_token']}).get('id')


def youtube_short(state, entry, path):
    if os.getenv('VM_AUTO_YOUTUBE') != 'true':
        raise DeliveryError('YouTube non activé (VM_AUTO_YOUTUBE)')
    receipt = state.data.setdefault('promos', {}).setdefault('campagne-' + entry['date'], {})
    http = HTTP()
    client = YouTube(http, state, access_token('youtube', state, http))
    client.verify_channel()
    meta = {'snippet': {'title': entry.get('youtube_titre', entry['titre'] + ' #Shorts')[:100],
                        'description': entry['texte'][:4900] + '\nVisuel original VM, personnage fictif Véloce.',
                        'categoryId': '17', 'defaultLanguage': 'fr', 'tags': ['Véloce Team', 'Véloce Mercato', 'VM Univers']},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}
    client.upload(path, meta, receipt)
    if not receipt.get('video_id'):
        raise DeliveryError('Short non confirmé par YouTube')
    return receipt['video_id'], 'https://www.youtube.com/shorts/' + receipt['video_id']


def publish(state, entry, graph=None, short=youtube_short):
    graph = graph or Graph()
    f = files(entry)
    urls = {k: SITE + v for k, v in f.items()}
    reel = bool(entry.get('reel'))
    journal = []
    ensure_meta_targets(state)
    for account, page_id in EXPECTED.items():
        meta = state.data.get('tokens', {}).get(account) or {}
        if not meta.get('page_token'):
            print('::warning::Page non connectée, ignorée : ' + account, flush=True)
            continue
        if str(meta.get('page_id')) != page_id:
            raise DeliveryError('Page Meta non conforme : ' + account)
        prefix = f"{entry['date']}/{account}/"
        if reel:
            def fb(m=meta):
                r = graph.call('POST', m['page_id'] + '/videos', {'file_url': urls['video'], 'description': entry['texte'], 'access_token': m['page_token']})
                return r.get('id'), ('https://www.facebook.com/' + m['page_id'] + '/videos/' + r['id']) if r.get('id') else ''
            action(state, prefix + 'facebook/video', fb, journal)
        else:
            def fb(m=meta):
                r = graph.call('POST', m['page_id'] + '/photos', {'url': urls['post'], 'caption': entry['texte'], 'access_token': m['page_token']})
                post = r.get('post_id') or r.get('id')
                return post, permalink(graph, post, 'permalink_url', m['page_token']) if post else ''
            action(state, prefix + 'facebook/photo', fb, journal)
        if meta.get('ig_id'):
            if reel:
                def ig(m=meta):
                    ident = instagram_reel(graph, m, {'verticale': urls['video'], 'texte_vertical': ig_text(entry['texte'])})
                    return ident, permalink(graph, ident, 'permalink', m['page_token']) if ident else ''
                action(state, prefix + 'instagram/reel', ig, journal)
            else:
                def ig(m=meta):
                    ident = instagram_image(graph, m, urls['post'], ig_text(entry['texte']))
                    return ident, permalink(graph, ident, 'permalink', m['page_token']) if ident else ''
                action(state, prefix + 'instagram/photo', ig, journal)
            action(state, prefix + 'instagram/story', lambda m=meta: (ig_story(graph, m, urls['story']), 'story Instagram (24 h)'), journal)
    if entry.get('youtube_short'):
        action(state, entry['date'] + '/youtube/short', lambda: short(state, entry, ROOT / f['video']), journal)
    return journal


def save_journal(entry, rows):
    data = json.loads(JOURNAL.read_text(encoding='utf-8')) if JOURNAL.exists() else []
    known = {(r['date'], r['cle']) for r in data}
    for row in rows:
        if (entry['date'], row['cle']) not in known:
            data.append(dict(row, date=entry['date'], theme=entry['titre']))
    data.sort(key=lambda r: (r['date'], r['cle']), reverse=True)
    JOURNAL.write_text(json.dumps(data[:400], ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True, type=Path)
    args = parser.parse_args()
    entry = today_entry()
    if not entry:
        return
    f = files(entry)
    kinds = [(SITE + f['story'], 'image/')]
    kinds += [(SITE + f['video'], 'video/')] if (entry.get('reel') or entry.get('youtube_short')) else []
    kinds += [] if entry.get('reel') else [(SITE + f['post'], 'image/')]
    confirm_public(kinds)
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    rows = publish(state, entry)
    save_journal(entry, rows)
    for row in rows:
        note(f"BILAN {row['cle']} : {row['statut']} {row.get('lien') or row.get('raison') or ''}".rstrip())
    if any(r['statut'] == 'echec' for r in rows):
        raise DeliveryError('Au moins une publication du jour a échoué (voir le bilan)')


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print('::error::Campagne du jour : ' + (str(ex) if isinstance(ex, DeliveryError) else type(ex).__name__)[:180], flush=True)
        sys.exit(1)
