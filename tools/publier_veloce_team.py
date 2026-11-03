#!/usr/bin/env python3
"""Campagne UNIQUE « VÉLOCE TEAM — Deux univers, une passion ».

Destinations : Facebook + Instagram (photo et story) des Pages Véloce Mercato et VM Univers,
et un Short YouTube. Visuels originaux VM (assets/social/veloce-team-*), aucun contenu tiers.

Deux étapes :
  --mode essai    : aucune publication Meta. Vérifie les médias publics, les Pages, les comptes Instagram
                    et la chaîne YouTube, puis envoie le Short en PRIVÉ (visible du seul propriétaire).
  --mode publier  : exige un essai réussi. Publie les posts Meta et passe le Short privé en public.

Chaque action est inscrite dans l'état chiffré AVANT l'envoi : relancer ne crée jamais de doublon.
Aucun identifiant n'est créé, modifié ni affiché.
"""
import argparse
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import HTTP, State, YouTube, DeliveryError, access_token, git_save, public_allowed
from tools.publier_meta import Graph, instagram_image, ensure_meta_targets

KEY = 'veloce_team_v1'
BASE = 'https://velocemercato.fr/assets/social/'
POST, STORY, VIDEO = BASE + 'veloce-team-post.jpg', BASE + 'veloce-team-story.jpg', BASE + 'veloce-team-short.mp4'
SHORT_FILE = ROOT / 'assets/social/veloce-team-short.mp4'
EXPECTED = {'meta': '1384363904759072', 'meta_univers': '1349998758205153'}

CAPTION = (
    "🔥 VÉLOCE TEAM — Deux univers, une passion ! ⚽👑\n\n"
    "Deux sites, une seule équipe :\n"
    "⚽ velocemercato.fr : le foot pro, amateur et régional, VM Actu, VM Multisport, VM MANGAS et VM Séries.\n"
    "👑 vmunivers.fr : tous les projets VM, les services près de chez toi, les pros et la communauté.\n\n"
    "👉 https://velocemercato.fr/\n"
    "👉 https://vmunivers.fr/\n\n"
    "Tu es plutôt team foot ou team univers ? Dis-le en commentaire 👇\n"
    "#VeloceTeam #VeloceMercato #VMUnivers #Foot #FootAmateur #FrancheComte")
IG_CAPTION = CAPTION.replace("👉 https://velocemercato.fr/\n👉 https://vmunivers.fr/",
                             "🔗 velocemercato.fr et vmunivers.fr : lien dans la bio")
YT_META = {
    'snippet': {
        'title': 'VÉLOCE TEAM ⚽👑 Deux univers, une passion #Shorts',
        'description': ('Deux sites, une seule équipe !\n'
                        '⚽ Le foot, l’actu, le multisport, les mangas et les séries : https://velocemercato.fr/\n'
                        '👑 Les projets VM, les services locaux et la communauté : https://vmunivers.fr/\n\n'
                        'Rejoins la Véloce Team 👇\n#VeloceTeam #VeloceMercato #VMUnivers\n'
                        'Visuel original VM, personnage fictif Véloce.'),
        'categoryId': '17', 'defaultLanguage': 'fr',
        'tags': ['Véloce Team', 'Véloce Mercato', 'VM Univers', 'foot', 'foot amateur', 'Franche-Comté']},
    'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}


def note(text):
    print('::notice::' + text, flush=True)


def confirm_media():
    for link, kind in ((POST, 'image/'), (STORY, 'image/'), (VIDEO, 'video/')):
        for attempt in range(18):
            try:
                req = urllib.request.Request(link, method='HEAD', headers={'User-Agent': 'VM-Veloce-Team/1'})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    if resp.status == 200 and (resp.headers.get('Content-Type') or '').startswith(kind):
                        note('Média public prêt : ' + link.rsplit('/', 1)[-1])
                        break
            except Exception:
                pass
            if attempt == 17:
                raise DeliveryError('Média public indisponible : ' + link.rsplit('/', 1)[-1])
            time.sleep(10)


def accounts(state):
    ensure_meta_targets(state)
    found = []
    for account, page_id in EXPECTED.items():
        meta = state.data.get('tokens', {}).get(account) or {}
        if not meta.get('page_token'):
            print('::warning::Page non connectée, ignorée : ' + account, flush=True)
            continue
        if str(meta.get('page_id')) != page_id:
            raise DeliveryError('Page Meta non conforme : ' + account)
        found.append((account, meta))
    return found


def action(state, key, callback):
    done = state.data.setdefault(KEY, {})
    previous = done.get(key, {})
    if previous.get('status') in ('envoi', 'publie'):
        # 'envoi' sans confirmation : l'issue est inconnue, on ne renvoie pas pour éviter un doublon.
        note('Déjà traité, aucun nouvel envoi : ' + key + ((' → ' + previous['url']) if previous.get('url') else ''))
        return
    done[key] = {'status': 'envoi'}
    state.save()
    try:
        ident, url = callback()
        if not ident:
            raise DeliveryError('aucun identifiant de publication retourné')
        done[key] = {'status': 'publie', 'id': str(ident), 'url': url or ''}
        state.save()
        note('PUBLIÉ ' + key + ' → ' + (url or 'lien public non communiqué par Meta'))
    except Exception as ex:
        done[key] = {'status': 'echec', 'raison': (str(ex) if isinstance(ex, DeliveryError) else type(ex).__name__)[:170]}
        state.save()
        print('::error::Échec ' + key + ' : ' + done[key]['raison'], flush=True)


def permalink(graph, ident, field, token):
    try:
        return graph.call('GET', ident, {'fields': field, 'access_token': token}).get(field, '')
    except DeliveryError:
        return ''


def ig_story(graph, meta):
    created = graph.call('POST', meta['ig_id'] + '/media', {'media_type': 'STORIES', 'image_url': STORY, 'access_token': meta['page_token']})
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


def youtube_client(state):
    http = HTTP()
    client = YouTube(http, state, access_token('youtube', state, http))
    client.verify_channel()
    return client


def essai(state):
    graph = Graph()
    for account, meta in accounts(state):
        page = graph.call('GET', meta['page_id'], {'fields': 'name', 'access_token': meta['page_token']})
        note(f'Page Facebook {account} joignable : {page.get("name", "?")}')
        if meta.get('ig_id'):
            ig = graph.call('GET', meta['ig_id'], {'fields': 'username', 'access_token': meta['page_token']})
            note(f'Instagram {account} joignable : @{ig.get("username", "?")}')
        else:
            print('::warning::Pas de compte Instagram relié pour ' + account, flush=True)
    if os.getenv('VM_AUTO_YOUTUBE') != 'true':
        raise DeliveryError('YouTube non activé (VM_AUTO_YOUTUBE) : essai incomplet')
    client = youtube_client(state)
    receipt = state.data.setdefault('promos', {}).setdefault('veloce-team-short', {})
    client.upload(SHORT_FILE, YT_META, receipt)
    if receipt.get('status') not in ('private', 'uploaded', 'public'):
        raise DeliveryError('Short non confirmé par YouTube')
    note('Short YouTube envoyé en PRIVÉ (visible du seul propriétaire) : https://studio.youtube.com/video/' + receipt['video_id'] + '/edit')
    state.data.setdefault(KEY, {})['essai'] = {'status': 'ok', 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    state.save()
    note('ESSAI RÉUSSI : aucune publication Facebook ou Instagram effectuée.')


def publier(state):
    if state.data.get(KEY, {}).get('essai', {}).get('status') != 'ok':
        raise DeliveryError('Essai privé non validé : lancer d’abord le mode essai')
    graph = Graph()
    for account, meta in accounts(state):
        token = meta['page_token']

        def fb(m=meta):
            r = graph.call('POST', m['page_id'] + '/photos', {'url': POST, 'caption': CAPTION, 'access_token': m['page_token']})
            post = r.get('post_id') or r.get('id')
            return post, permalink(graph, post, 'permalink_url', m['page_token']) if post else ''
        action(state, account + '/facebook/photo', fb)
        if meta.get('ig_id'):
            def ig(m=meta):
                ident = instagram_image(graph, m, POST, IG_CAPTION)
                return ident, permalink(graph, ident, 'permalink', m['page_token']) if ident else ''
            action(state, account + '/instagram/photo', ig)
            action(state, account + '/instagram/story', lambda m=meta: (ig_story(graph, m), 'story Instagram (24 h)'))
    receipt = state.data.get('promos', {}).get('veloce-team-short', {})
    if not receipt.get('video_id'):
        raise DeliveryError('Short privé introuvable dans les accusés')

    def yt():
        if not public_allowed():
            raise DeliveryError('Passage en public non autorisé (VM_YOUTUBE_PUBLIC)')
        if receipt.get('status') != 'public':
            youtube_client(state).make_public(receipt)
        return receipt['video_id'], 'https://www.youtube.com/shorts/' + receipt['video_id']
    action(state, 'youtube/short', yt)
    bilan = state.data.get(KEY, {})
    for key in sorted(k for k in bilan if '/' in k):
        row = bilan[key]
        note(f"BILAN {key} : {row.get('status')} {row.get('url') or row.get('raison') or ''}".rstrip())
    if any(row.get('status') == 'echec' for k, row in bilan.items() if '/' in k):
        raise DeliveryError('Au moins une publication a échoué (voir le bilan)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True, type=Path)
    parser.add_argument('--mode', required=True, choices=['essai', 'publier'])
    args = parser.parse_args()
    if not SHORT_FILE.is_file():
        raise DeliveryError('Vidéo du Short absente du dépôt')
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    confirm_media()
    (essai if args.mode == 'essai' else publier)(state)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print('::error::Campagne VÉLOCE TEAM : ' + (str(ex) if isinstance(ex, DeliveryError) else type(ex).__name__)[:180], flush=True)
        sys.exit(1)
