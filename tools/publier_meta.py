#!/usr/bin/env python3
"""Facebook et Instagram automatiques pour Véloce Mercato (Page + Instagram pro reliés).

connecter : échange le jeton court (secret META_USER_TOKEN, 1 h) contre l'accès permanent de la Page,
            rangé dans l'état chiffré (branche broadcast-state). Rien n'est publié.
publier   : seulement si VM_AUTO_META=true (réglé par le propriétaire) :
            - les pastilles verticales récentes (studio/reseaux.json) en Reels Facebook + Instagram ;
            - un article foot sourcé par créneau (8 h, 12 h, 20 h) en publication Facebook avec lien.
Jamais deux fois le même contenu : un accusé est écrit AVANT chaque envoi.
Aucun jeton n'est affiché ; les erreurs Meta sont résumées.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save  # noqa: E402

GRAPH = 'https://graph.facebook.com/'
HOSTS = {'graph.facebook.com'}
PARIS = ZoneInfo('Europe/Paris')
UTC = dt.timezone.utc
# Heure de Paris -> univers de l'article publié sur Facebook (demande de Romain, 26/10/2026).
SLOTS = {7: 'foot', 8: 'actus', 9: 'gaming', 12: 'foot', 13: 'actus', 14: 'gaming',
         16: 'foot', 17: 'actus', 18: 'gaming', 20: 'foot'}
UNIVERS = {
    'foot': {'file': 'articles.json', 'emoji': '⚽', 'site': 'velocemercato.fr',
             'tags': '#foot #mercato #football #velocemercato'},
    'actus': {'file': 'actus/news.json', 'emoji': '📰', 'site': 'velocemercato.fr/actus',
              'tags': '#actualite #info #france #vmactus'},
    'gaming': {'file': 'vm-gaming/news.json', 'emoji': '🎮', 'site': 'velocemercato.fr/vm-gaming',
               'tags': '#gaming #jeuxvideo #gamer #vmgaming'},
}

# Page VM Univers : campagne pub, 3 publications par jour (choix de Romain, 27/10/2026).
# 9 h : VM Studio (sites pour artisans et pros, son activité principale)
# 13 h : un outil gratuit VM · 19 h : la vitrine (chaîne YouTube, vmunivers.fr, velocemercato.fr)
# Environ 1 pub pour 4 publications normales : au-delà, Facebook et Instagram montrent moins la page.
DEBUT_UNIVERS = dt.date(2026, 10, 26)
HEURES_UNIVERS = {DEBUT_UNIVERS: (16, 19, 21, 23)}   # lancement ; ensuite tous les jours :
HEURES_UNIVERS_DEFAUT = (9, 13, 19)
YOUTUBE_CHAINE = 'https://www.youtube.com/@VeloceMercato'
STUDIO_URL = 'https://velocemercato.fr/web-studio.html'
STUDIO_PITCH = ('Un site clair sur téléphone, prêt à recevoir vos clients.\n'
                '✅ Page unique 290 € · Site vitrine 590 € · Réservation ou commande 990 €\n'
                '✅ Devis gratuit, prix confirmé par écrit')
STUDIO_TAGS = '#VMStudio #siteinternet #artisan #commerce #restaurant #VM'
GRATUIT_TAGS = '#gratuit #VMUnivers #VM'
# Une liste par créneau (9 h, 13 h, 19 h) ; chaque jour on avance d'un cran dans chaque liste.
ROTATIONS = [
    [
        {'type': 'video', 'name': 'VM Studio', 'video_id': 'vm-studio', 'url': STUDIO_URL,
         'titre': '💼 Artisans, commerçants : votre site pro dès 290 €', 'pitch': STUDIO_PITCH, 'tags': STUDIO_TAGS},
        {'type': 'carte', 'name': 'VM Studio', 'icon': 'studio', 'url': STUDIO_URL,
         'carte': 'Votre site pro dès 290 €. Devis gratuit.',
         'titre': '🛠️ Votre site internet, sans vous ruiner', 'pitch': STUDIO_PITCH, 'tags': STUDIO_TAGS},
        {'type': 'image', 'name': 'VM Studio', 'image': 'https://velocemercato.fr/img/pub/vm-studio-talent.jpg', 'url': STUDIO_URL,
         'titre': '✨ Votre commerce a du talent. Montrez-le en ligne.',
         'pitch': 'Site internet · Photos · Visuels · QR code\nVM Studio prépare une proposition à votre image, puis vous l’ajustez ensemble.\n✅ Dès 290 € · Devis gratuit', 'tags': STUDIO_TAGS},
        {'type': 'video', 'name': 'VM Studio', 'video_id': 'vm-bureaux', 'url': STUDIO_URL,
         'titre': '📲 Coiffeur, snack, artisan : vos clients vous cherchent sur leur téléphone',
         'pitch': 'On crée votre site clé en main, avec réservation ou commande en ligne si besoin.\n'
                  '✅ Dès 290 € · Devis gratuit, prix confirmé par écrit', 'tags': STUDIO_TAGS},
    ],
    [
        {'type': 'carte', 'name': 'VM Emploi', 'icon': 'emploi', 'url': 'https://velocemercato.fr/emploi/',
         'titre': '🎁 Gratuit : VM Emploi', 'pitch': 'Cherche un emploi sur tous les grands sites en un seul clic.', 'tags': GRATUIT_TAGS + ' #emploi'},
        {'type': 'carte', 'name': 'VM CV', 'icon': 'cv', 'url': 'https://velocemercato.fr/cv/',
         'titre': '🎁 Gratuit : VM CV', 'pitch': 'Fais ton CV pro en quelques minutes, sans inscription.', 'tags': GRATUIT_TAGS + ' #cv'},
        {'type': 'carte', 'name': 'VM Recettes', 'icon': 'recettes', 'url': 'https://velocemercato.fr/recettes/',
         'titre': '🎁 Gratuit : VM Recettes', 'pitch': 'Une idée de recette simple chaque jour.', 'tags': GRATUIT_TAGS + ' #recette'},
        {'type': 'carte', 'name': 'VM Météo', 'icon': 'meteo', 'url': 'https://velocemercato.fr/meteo/',
         'titre': '🎁 Gratuit : VM Météo & Découverte', 'pitch': 'La météo et des idées de sorties près de chez toi.', 'tags': GRATUIT_TAGS + ' #meteo'},
        {'type': 'carte', 'name': 'VM Sport', 'icon': 'sport', 'url': 'https://velocemercato.fr/sport/',
         'titre': '🎁 Gratuit : VM Sport & randonnée', 'pitch': 'Des idées de sport et de balades à faire près de chez toi.', 'tags': GRATUIT_TAGS + ' #sport'},
    ],
    [
        {'type': 'carte', 'name': 'YouTube Véloce Mercato', 'icon': 'tv', 'url': YOUTUBE_CHAINE,
         'carte': 'Les JT foot chaque jour. Abonne-toi !',
         'titre': '▶️ Abonne-toi à la chaîne Véloce Mercato',
         'pitch': 'Les JT foot, actus et gaming chaque jour, et le mag du dimanche à 11 h.', 'tags': '#VeloceMercato #foot #YouTube #VM'},
        {'type': 'video', 'name': 'VM Univers', 'video_id': 'vm-univers', 'url': 'https://vmunivers.fr/',
         'titre': '👑 VM Univers : tous nos projets au même endroit',
         'pitch': 'Sites pour les pros, outils gratuits, foot et gaming : un seul lien.', 'tags': '#VMUnivers #VM'},
        {'type': 'video', 'name': 'Véloce Mercato', 'video_id': 'veloce-foot', 'url': 'https://velocemercato.fr/',
         'titre': '⚽ Véloce Mercato : l’essentiel du foot',
         'pitch': 'Actus sourcées, scores, JT en vidéo et tournois EA FC.', 'tags': '#VeloceMercato #foot #mercato #VM'},
    ],
]


def heures_univers(day):
    return HEURES_UNIVERS.get(day, HEURES_UNIVERS_DEFAUT)


def contenu_univers(local):
    """Même calcul que la page studio/programme-vmunivers.html : créneau du jour -> sa liste, un cran par jour."""
    heures = heures_univers(local.date())
    rang = heures.index(local.hour) if local.hour in heures else 0
    jour = (local.date() - DEBUT_UNIVERS).days
    liste = ROTATIONS[rang % len(ROTATIONS)]
    item = dict(liste[jour % len(liste)])
    if item['type'] == 'video':
        item['video'] = f'https://velocemercato.fr/media/promos/{item["video_id"]}-vertical.mp4'
    return item


def texte_univers(item):
    fin = '\nVidéo réalisée avec l’aide de l’IA.' if item['type'] == 'video' else ''
    return (f'{item["titre"]}\n\n{item["pitch"]}\n\n👉 {item["url"]}\n'
            f'Tous nos projets : vmunivers.fr{fin}\n\n{item["tags"]}')


PROJETS = [
    ('VM Emploi', 'emploi', '/emploi/', 'Les offres d’emploi près de chez toi, simples à lire.'),
    ('AlloLivre', 'allolivre', '/allolivre/', 'Livraison et entraide entre voisins.'),
    ('VM Studio', 'studio', '/web-studio.html', 'Sites internet et visuels pour les pros, avec des prix clairs.'),
    ('VM Actus', 'actus', '/actus/', 'L’actu générale en brèves sourcées, toute la journée.'),
    ('VM Gaming', 'gaming', '/vm-gaming/', 'Jeux vidéo, actu gaming et communauté de joueurs.'),
    ('La Pastille TV', 'tv', '/studio.html#tv', 'Les JT foot, actu et gaming en vidéo, générés par IA.'),
    ('VM CV', 'cv', '/cv/', 'Fais ton CV pro gratuitement, en quelques minutes.'),
    ('VM Shop', 'annonces', '/shop/', 'Les petites annonces de la communauté VM.'),
    ('VM Recettes', 'recettes', '/recettes/', 'Une idée de recette chaque jour.'),
    ('VM Météo & Découverte', 'meteo', '/meteo/', 'La météo et des idées de sorties.'),
    ('VM Sport & randonnée', 'sport', '/sport/', 'Sport, balades et randonnées à faire.'),
    ('VM Pro Local', 'pro', '/pro/', 'Les pros et artisans de chez nous.'),
    ('VM Produits locaux', 'produits', '/produits-locaux/', 'Acheter local, près de chez toi.'),
    ('VM Belfort', 'belfort', '/belfort/', 'L’info et les bons plans du coin.'),
    ('Pépite FC', 'pepite', '/pepite/', 'Repère et fais connaître les jeunes talents du foot.'),
    ('VM Radio', 'radio', '/radio.html', 'La radio de l’univers VM.'),
]


def projet_du_jour(now):
    item = contenu_univers(now.astimezone(PARIS))
    return item['name'], item.get('icon', ''), item['url'], item['pitch']


def article_url(univers, ident):
    if univers == 'foot':
        return 'https://velocemercato.fr/a/' + ident + '.html'
    return 'https://velocemercato.fr/' + ('actus/' if univers == 'actus' else 'vm-gaming/') + '#a=' + ident
IDENT = re.compile(r'[a-z0-9][a-z0-9-]{1,99}')
VIDEO = re.compile(r'https://cdn\.jsdelivr\.net/gh/Velocemercato/velocemercato\.fr@[0-9a-f]{40}/[A-Za-z0-9._-]+\.mp4')


class Graph:
    def call(self, method, path, params):
        url = GRAPH + path.lstrip('/')
        if urllib.parse.urlsplit(url).hostname not in HOSTS:
            raise DeliveryError('Destination Meta non autorisée.')
        data = urllib.parse.urlencode(params).encode()
        if method == 'GET':
            request = urllib.request.Request(url + '?' + data.decode(), method='GET')
        else:
            request = urllib.request.Request(url, data=data, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read() or b'{}')
        except urllib.error.HTTPError as error:
            try:
                info = json.loads(error.read()).get('error', {})
            except ValueError:
                info = {}
            message = re.sub(r'[A-Za-z0-9]{40,}', '…', str(info.get('message', '')))[:180]
            raise DeliveryError(f'Meta a refusé ({error.code}, code {info.get("code", "?")}) : {message}') from None


def connect(state, graph, app_id, app_secret, user_token):
    try:
        long = graph.call('GET', 'oauth/access_token', {'grant_type': 'fb_exchange_token', 'client_id': app_id,
                                                        'client_secret': app_secret, 'fb_exchange_token': user_token})
    except DeliveryError as error:
        # Jeton déjà prolongé via l'outil Meta « Extend Access Token » : utilisable tel quel, sans clé secrète.
        print(f'::notice::Échange avec la clé secrète impossible ({str(error)[:90]}) : jeton utilisé tel quel.', flush=True)
        long = {'access_token': user_token}
    token = long.get('access_token')
    if not token:
        raise DeliveryError('Meta : échange du jeton non confirmé (jeton expiré ? le refaire dans l’explorateur).')
    try:
        pages = graph.call('GET', 'me/accounts', {'fields': 'id,name,link,username,access_token,instagram_business_account{id,username}',
                                                  'access_token': token}).get('data', [])
    except DeliveryError as error:
        if 'accounts' not in str(error):
            raise
        # Le jeton collé est déjà celui de la Page (choix « Page » dans l'explorateur).
        print('::notice::Le jeton collé est un jeton de Page (pas un jeton utilisateur).', flush=True)
        page = graph.call('GET', 'me', {'fields': 'id,name,link,username,instagram_business_account{id,username}', 'access_token': token})
        pages = [{**page, 'access_token': token}]
    pages = [p for p in pages if p.get('access_token')]
    if not pages:
        raise DeliveryError('Meta : aucune Page autorisée. Cocher la Page Véloce Mercato lors de « Generate Access Token ».')
    def norm(name):
        return str(name).lower().replace('é', 'e').replace(' ', '')
    targets = {'meta': next((p for p in pages if 'veloce' in norm(p.get('name'))), None),
               'meta_univers': next((p for p in pages if any(k in norm(p.get('name')) for k in ('vminvest', 'univers'))), None)}
    if not any(targets.values()):
        targets['meta'] = pages[0]
    page = targets['meta'] or targets['meta_univers']
    for account, item in targets.items():
        if not item:
            continue
        insta = item.get('instagram_business_account') or {}
        try:
            info = graph.call('GET', 'debug_token', {'input_token': item['access_token'], 'access_token': token}).get('data', {})
            expires = int(info.get('expires_at') or 0)
            print(f'::notice::Accès de la Page « {item.get("name", "?")} » : ' + ('PERMANENT ✅' if expires == 0 else
                  'temporaire, expire le ' + dt.datetime.fromtimestamp(expires, UTC).astimezone(PARIS).strftime('%d/%m %H:%M')
                  + ' (prolonger le jeton dans l’outil Meta puis relancer)'), flush=True)
        except DeliveryError:
            pass
        state.data.setdefault('tokens', {})[account] = {'page_id': str(item['id']), 'page_name': item.get('name', ''),
                                                        'page_token': item['access_token'], 'ig_id': str(insta.get('id', '')),
                                                        'ig_username': insta.get('username', '')}
        state.save()
        print(f'::notice::Meta connecté : Page « {item.get("name", "?")} »'
              + (f' + Instagram @{insta["username"]}' if insta.get('username') else ' (aucun Instagram pro relié à cette Page)')
              + '. Rien n’est publié tant que VM_AUTO_META n’est pas à true.', flush=True)
        print(f'::notice::Adresse publique : {item.get("link") or "https://www.facebook.com/" + str(item.get("username") or item["id"])}', flush=True)
    return page


def read(path, default):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else default


def when(value):
    try:
        moment = dt.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return moment if moment.tzinfo else None
    except ValueError:
        return None


def clean(value, limit=600):
    return re.sub(r'[ \t]+', ' ', str(value)).strip()[:limit]


def reels(root, now, hours=30):
    out = []
    for row in read(Path(root) / 'studio/reseaux.json', []):
        date = when(row.get('date'))
        if (IDENT.fullmatch(str(row.get('id', ''))) and VIDEO.fullmatch(str(row.get('verticale', '')))
                and date and dt.timedelta(0) <= now - date <= dt.timedelta(hours=hours)):
            out.append(row)
    return sorted(out, key=lambda r: r['date'])


def article(root, now, done, univers='foot', hours=12):
    rows = sorted(read(Path(root) / UNIVERS[univers]['file'], []), key=lambda a: a.get('publishedAt', ''), reverse=True)
    for row in rows:
        ident = str(row.get('id', ''))
        source = next((s for s in row.get('sources', []) if s.get('nom') and str(s.get('url', '')).startswith('https://')), None)
        date = when(row.get('publishedAt'))
        if (IDENT.fullmatch(ident) and source and row.get('titre') and row.get('resume')
                and f'article/{univers}/{ident}' not in done and 'article/' + ident not in done
                and date and dt.timedelta(0) <= now - date <= dt.timedelta(hours=hours)
                and (univers != 'foot' or (Path(root) / 'a' / (ident + '.html')).is_file())):
            return row, source
    return None, None


YOUTUBE = re.compile(r'https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}')


def youtube_jt(root, now, hours=6):
    """Les JT déjà publics sur YouTube (studio/diffusions.json), les plus récents d'abord."""
    out = []
    for row in read(Path(root) / 'studio/diffusions.json', []):
        video = (row.get('plateformes') or {}).get('youtube') or {}
        date = when(row.get('date_publication'))
        if (video.get('status') == 'published' and YOUTUBE.fullmatch(str(video.get('url', ''))) and IDENT.fullmatch(str(row.get('id', '')))
                and date and dt.timedelta(0) <= now - date <= dt.timedelta(hours=hours)):
            out.append({**row, 'youtube': video['url']})
    return sorted(out, key=lambda r: r['date_publication'], reverse=True)


def instagram_card(univers, row, source):
    from tools.cartes_insta import make_card, push_card
    with tempfile.TemporaryDirectory(prefix='carte-') as folder:
        path = make_card(univers, clean(row['titre'], 200), clean(source['nom'], 70), Path(folder) / f'{univers}-{row["id"]}.jpg')
        return push_card(path)


def instagram_projet_card(name, icon, pitch):
    from tools.cartes_insta import make_projet_card, push_card
    with tempfile.TemporaryDirectory(prefix='carte-') as folder:
        path = make_projet_card(name, icon, pitch, Path(folder) / f'projet-{icon}-{dt.date.today():%Y%m%d}.jpg')
        return push_card(path)


def instagram_image(graph, meta, image_url, caption, sleep=time.sleep):
    created = graph.call('POST', meta['ig_id'] + '/media', {'image_url': image_url, 'caption': caption[:2100],
                                                           'access_token': meta['page_token']})
    container = created.get('id')
    if not container:
        raise DeliveryError('Instagram : préparation de l’image non confirmée.')
    for _ in range(20):
        status = graph.call('GET', container, {'fields': 'status_code', 'access_token': meta['page_token']}).get('status_code')
        if status in (None, 'FINISHED'):
            break
        if status in ('ERROR', 'EXPIRED'):
            raise DeliveryError('Instagram : image refusée au traitement.')
        sleep(5)
    return graph.call('POST', meta['ig_id'] + '/media_publish', {'creation_id': container,
                                                                 'access_token': meta['page_token']}).get('id')


def instagram_reel(graph, meta, row, wait=480, sleep=time.sleep):
    created = graph.call('POST', meta['ig_id'] + '/media', {'media_type': 'REELS', 'video_url': row['verticale'],
                                                           'caption': clean(row.get('texte_vertical') or row.get('titre'), 2100),
                                                           'share_to_feed': 'true', 'access_token': meta['page_token']})
    container = created.get('id')
    if not container:
        raise DeliveryError('Instagram : préparation du Reel non confirmée.')
    for _ in range(max(1, wait // 15)):
        status = graph.call('GET', container, {'fields': 'status_code', 'access_token': meta['page_token']}).get('status_code')
        if status == 'FINISHED':
            return graph.call('POST', meta['ig_id'] + '/media_publish', {'creation_id': container,
                                                                         'access_token': meta['page_token']}).get('id')
        if status in ('ERROR', 'EXPIRED'):
            raise DeliveryError('Instagram : la vidéo a été refusée au traitement.')
        sleep(15)
    raise DeliveryError('Instagram : traitement trop long, Reel non publié (sera ignoré pour éviter un doublon).')


def publish(state, graph, root=ROOT, now=None, limit=2, sleep=time.sleep, force=None, card=None, account='meta'):
    now = now or dt.datetime.now(UTC)
    meta = state.data.get('tokens', {}).get(account)
    if not meta or not meta.get('page_token'):
        raise DeliveryError('Meta non connecté : lancer « Connecter Facebook et Instagram ».')
    local_now = now.astimezone(PARIS)
    slots = {h: 'projet' for h in heures_univers(local_now.date())} if account == 'meta_univers' else SLOTS
    done = state.data.setdefault('meta' if account == 'meta' else account + '_accuses', {})
    errors, sent = [], 0

    def mark(key, status, **extra):
        done[key] = {'status': status, 'at': now.isoformat(timespec='seconds'), **extra}
        state.save()

    projets_seulement = account == 'meta_univers'  # VM Univers : pas de JT ni d'articles, seulement les projets
    for row in ([] if projets_seulement else youtube_jt(root, now)[:2]):
        key = 'jt/facebook/' + row['id']
        if key in done:
            continue
        mark(key, 'envoi')
        univers = row['id'].split('-', 1)[0]
        conf = UNIVERS.get(univers, UNIVERS['foot'])
        message = (f'🎬 {clean(row.get("titre", "Le JT de La Pastille"), 150)}\n\n'
                   f'Le JT en vidéo : l’essentiel de l’actu en quelques minutes. Émission générée par IA, infos sourcées.\n'
                   f'👉 Toutes les brèves sur {conf["site"]}\n\n{conf["tags"]} #lapastille')
        try:
            result = graph.call('POST', meta['page_id'] + '/feed', {'message': message, 'link': row['youtube'],
                                                                    'access_token': meta['page_token']}).get('id')
            mark(key, 'publie', post=str(result or ''))
            print(f'::notice::facebook : JT YouTube partagé ({row["id"]})')
        except DeliveryError as error:
            mark(key, 'echec')
            errors.append(f'facebook / JT {row["id"]} : {error}')

    for row in ([] if projets_seulement else reels(root, now)):
        if sent >= limit:
            break
        attempted = False
        for network in ('facebook', 'instagram'):
            key = f'reel/{network}/{row["id"]}'
            if key in done or (network == 'instagram' and not meta.get('ig_id')):
                continue
            attempted = True
            mark(key, 'envoi')  # accusé AVANT l'envoi : jamais de doublon, même après une coupure
            try:
                if network == 'facebook':
                    result = graph.call('POST', meta['page_id'] + '/videos', {
                        'file_url': row['verticale'], 'description': clean(row.get('texte_vertical') or row.get('titre'), 2000),
                        'access_token': meta['page_token']}).get('id')
                else:
                    result = instagram_reel(graph, meta, row, sleep=sleep)
                mark(key, 'publie', post=str(result or ''))
                print(f'::notice::{network} : pastille {row["id"]} publiée')
            except DeliveryError as error:
                mark(key, 'echec')
                errors.append(f'{network} / {row["id"]} : {error}')
        sent += attempted

    local = now.astimezone(PARIS)
    # GitHub saute parfois un passage : on rattrape le créneau le plus récent manqué (moins de 3 h).
    def cle(h):
        return (f'projet/{local:%Y-%m-%d}/{h:02d}' if slots.get(h) == 'projet' else f'creneau/{local:%Y-%m-%d}/{h:02d}')
    manques = [h for h in sorted(slots, reverse=True) if 0 <= local.hour - h < 3 and cle(h) not in done]
    heure = manques[0] if manques else local.hour
    cible = local.replace(hour=heure, minute=10)
    if not force and slots.get(heure) == 'projet':
        key = cle(heure)
        if key not in done:
            item = contenu_univers(cible)
            name, text = item['name'], texte_univers(item)
            mark(key, 'envoi', projet=name, type=item['type'])
            try:
                if item['type'] == 'video':
                    graph.call('POST', meta['page_id'] + '/videos', {'file_url': item['video'], 'description': text,
                                                                     'access_token': meta['page_token']})
                elif item['type'] == 'image':
                    graph.call('POST', meta['page_id'] + '/photos', {'url': item['image'], 'caption': text,
                                                                     'access_token': meta['page_token']})
                else:
                    graph.call('POST', meta['page_id'] + '/feed', {'message': text, 'link': item['url'], 'access_token': meta['page_token']})
                print(f'::notice::facebook : {item["type"]} {name}')
                if meta.get('ig_id'):
                    insta_text = text.replace('👉 ' + item['url'], '👉 Lien en bio')
                    if item['type'] == 'video':
                        instagram_reel(graph, meta, {'verticale': item['video'], 'texte_vertical': insta_text}, sleep=sleep)
                    elif item['type'] == 'image':
                        instagram_image(graph, meta, item['image'], insta_text, sleep=sleep)
                    else:
                        instagram_image(graph, meta, (card or instagram_projet_card)(name, item['icon'], item.get('carte', item['pitch'])),
                                        insta_text, sleep=sleep)
                    print(f'::notice::instagram : {item["type"]} {name}')
                mark(key, 'publie', projet=name, type=item['type'])
            except (DeliveryError, OSError, subprocess.CalledProcessError) as error:
                mark(key, 'echec', projet=name)
                errors.append(f'VM Univers {name} : {str(error)[:150]}')
    univers = force or slots.get(heure)
    if univers == 'projet':
        univers = None
    slot_key = cle(heure) if not force else f'manuel/{local:%Y-%m-%d-%H%M}/{force}'
    if univers and slot_key not in done:
        row, source = article(root, now, done, univers)
        if row:
            key = f'article/{univers}/{row["id"]}'
            conf = UNIVERS[univers]
            mark(slot_key, 'envoi', article=row['id'])
            mark(key, 'envoi')
            message = (f'{conf["emoji"]} {clean(row["titre"], 200)}\n\n{clean(row["resume"], 500)}\n\n'
                       f'Selon {clean(source["nom"], 70)}\n👉 Toute l’info sur {conf["site"]}\n\n{conf["tags"]}')
            try:
                result = graph.call('POST', meta['page_id'] + '/feed', {'message': message, 'link': article_url(univers, row['id']),
                                                                        'access_token': meta['page_token']}).get('id')
                mark(key, 'publie', post=str(result or ''))
                mark(slot_key, 'publie', article=row['id'])
                print(f'::notice::facebook : article {univers} publié ({row["titre"][:60]})')
            except DeliveryError as error:
                mark(key, 'echec')
                errors.append(f'facebook / article {univers} {row["id"]} : {error}')
            insta = f'insta/{univers}/{row["id"]}'
            if meta.get('ig_id') and insta not in done:
                mark(insta, 'envoi')
                try:
                    image = (card or instagram_card)(univers, row, source)
                    caption = (f'{conf["emoji"]} {clean(row["titre"], 200)}\n\n{clean(row["resume"], 600)}\n\n'
                               f'Selon {clean(source["nom"], 70)}\n👉 L’article complet sur {conf["site"]} (lien en bio)\n\n{conf["tags"]}')
                    result = instagram_image(graph, meta, image, caption, sleep=sleep)
                    mark(insta, 'publie', post=str(result or ''))
                    print(f'::notice::instagram : article {univers} publié')
                except (DeliveryError, OSError, subprocess.CalledProcessError) as error:
                    mark(insta, 'echec')
                    errors.append(f'instagram / article {univers} {row["id"]} : {str(error)[:150]}')
        else:
            print(f'::notice::Pas d’article {univers} récent et sourcé à publier pour ce créneau.')
    for line in errors:
        print('::error::' + line.replace('\n', ' '))
    return errors


LANCEMENT = [
    {'type': 'video', 'name': 'VM Univers', 'url': 'https://vmunivers.fr/', 'pitch': 'Tous les projets du groupe VM, réunis au même endroit.',
     'video': 'https://velocemercato.fr/media/promos/vm-univers-vertical.mp4'},
    {'type': 'carte', 'name': 'VM Studio', 'icon': 'studio', 'url': 'https://velocemercato.fr/web-studio.html',
     'pitch': 'Sites internet et visuels pour les pros, avec des prix clairs.'},
    {'type': 'carte', 'name': 'VM CV', 'icon': 'cv', 'url': 'https://velocemercato.fr/cv/', 'pitch': 'Fais ton CV pro gratuitement, en quelques minutes.'},
]


def lancement(state, graph, sleep=time.sleep):
    """Premières publications Instagram/Facebook de VM Univers (une seule fois chacune)."""
    meta = state.data.get('tokens', {}).get('meta_univers') or {}
    if not meta.get('ig_id'):
        raise DeliveryError('Instagram VM Univers non relié.')
    done = state.data.setdefault('meta_univers_accuses', {})
    errors = []
    for item in LANCEMENT:
        key = 'lancement/' + item['name']
        if key in done:
            continue
        done[key] = {'status': 'envoi'}
        state.save()
        text = texte_univers(item)
        try:
            insta_text = text.replace('👉 ' + item['url'], '👉 Lien en bio')
            if item['type'] == 'video':
                instagram_reel(graph, meta, {'verticale': item['video'], 'texte_vertical': insta_text}, sleep=sleep)
            else:
                instagram_image(graph, meta, instagram_projet_card(item['name'], item['icon'], item['pitch']), insta_text, sleep=sleep)
            done[key] = {'status': 'publie'}
            print(f'::notice::instagram VM Univers : {item["name"]} publié')
        except (DeliveryError, OSError, subprocess.CalledProcessError) as error:
            done[key] = {'status': 'echec'}
            errors.append(f'lancement {item["name"]} : {str(error)[:150]}')
        state.save()
    for line in errors:
        print('::error::' + line)
    return errors


ANNONCE_META = ('🎯 NOUVEAU : VM META GAMING\n\nHEINEGUEZ & PABLO, LES MERCENAIRES : L’ARMURERIE EST OUVERTE.\n\n'
    'Les meilleures classes et tactiques du moment, sourcées et datées : Warzone (BR, Résurgence), Call of Duty BO7 & MW4, '
    'Battlefield 6, REDSEC et EA SPORTS FC 27. Favoris, codes à copier, fiches à partager. Gratuit.\n\n'
    '👉 {lien}\n\n#Warzone #CallofDuty #MW4 #BO7 #Battlefield6 #REDSEC #FC27 #meta #VMGaming')


def annonce(state, graph, sleep=time.sleep, image=None):
    """Annonce unique de VM Meta Gaming sur Véloce Mercato et VM Univers (Facebook + Instagram)."""
    url = 'https://velocemercato.fr/vm-gaming/meta/'
    errors = []
    for account in ('meta', 'meta_univers'):
        meta = state.data.get('tokens', {}).get(account) or {}
        if not meta.get('page_token'):
            continue
        done = state.data.setdefault('meta' if account == 'meta' else account + '_accuses', {})
        for net in ('facebook', 'instagram'):
            key = 'annonce/vm-meta-gaming/' + net
            if key in done or (net == 'instagram' and not meta.get('ig_id')):
                continue
            done[key] = {'status': 'envoi'}
            state.save()
            try:
                if net == 'facebook':
                    graph.call('POST', meta['page_id'] + '/feed', {'message': ANNONCE_META.format(lien=url), 'link': url,
                                                                    'access_token': meta['page_token']})
                else:
                    if not image:
                        from tools.cartes_insta import push_card
                        image = push_card(ROOT / 'vm-gaming/meta/assets/partage-meta.jpg')
                    instagram_image(graph, meta, image, ANNONCE_META.format(lien='lien en bio · velocemercato.fr/vm-gaming/meta'), sleep=sleep)
                done[key] = {'status': 'publie'}
                print(f'::notice::{account} {net} : annonce VM Meta Gaming publiée')
            except (DeliveryError, OSError, subprocess.CalledProcessError) as error:
                done[key] = {'status': 'echec'}
                errors.append(f'annonce {account} {net} : {str(error)[:150]}')
            state.save()
    for line in errors:
        print('::error::' + line)
    return errors


def carte_ballon_dor(data, output):
    """Carte Instagram du Ballon d'Or : texte seul sur fond or et bleu, aucune photo ni silhouette de joueur."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1080, 1350
    im = Image.new('RGB', (W, H), (11, 21, 51))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(11 + 40 * t), int(21 + 10 * t), int(51 - 20 * t)))
    bold = str(ROOT / 'studio/assets/Poppins-Bold.ttf')
    med = str(ROOT / 'studio/assets/Poppins-Medium.ttf')
    f = lambda path, n: ImageFont.truetype(path, n)
    gold = (244, 207, 85)
    d.rectangle((0, 0, W, 14), fill=gold)
    d.text((70, 80), 'VÉLOCE MERCATO', font=f(bold, 40), fill=gold)
    d.text((70, 150), "BALLON D'OR 2026", font=f(bold, 92), fill=(255, 255, 255))
    d.text((70, 290), 'LE VAINQUEUR', font=f(bold, 40), fill=gold)
    name = data['vainqueur']['nom']
    size = 120
    while d.textlength(name, font=f(bold, size)) > W - 140 and size > 60:
        size -= 6
    d.text((70, 345), name, font=f(bold, size), fill=gold, stroke_width=3, stroke_fill=(0, 0, 0))
    y = 345 + int(size * 1.3)
    detail = data['vainqueur'].get('detail') or ''
    if detail:
        d.text((70, y), detail[:60], font=f(med, 40), fill=(230, 232, 240))
        y += 70
    podium = data.get('podium') or []
    if len(podium) >= 3:
        y = max(y + 30, 700)
        d.text((70, y), 'LE PODIUM', font=f(bold, 40), fill=gold)
        y += 70
        for medal, who in zip(('1er', '2e', '3e'), podium[:3]):
            d.text((70, y), medal, font=f(bold, 52), fill=gold)
            d.text((200, y), who[:28], font=f(bold, 52), fill=(255, 255, 255))
            y += 90
    d.line((70, H - 190, W - 70, H - 190), fill=gold, width=4)
    d.text((70, H - 165), 'Tous les trophées de la soirée :', font=f(med, 36), fill=(225, 230, 245))
    d.text((70, H - 110), 'velocemercato.fr', font=f(bold, 52), fill=gold)
    im.save(output, 'JPEG', quality=90)
    return output


def ballon_dor(state, graph, root=ROOT, sleep=time.sleep):
    """Publie le vainqueur et le podium du Ballon d'Or 2026 (Facebook + Instagram Véloce, Discord), une seule fois.
    Rien ne part tant que ballon-dor-2026.json ne contient pas un vainqueur vérifié."""
    data = read(Path(root) / 'ballon-dor-2026.json', {})
    win = (data.get('vainqueur') or {}).get('nom')
    if not win or not data.get('sources'):
        print('::notice::Ballon d’Or : vainqueur pas encore confirmé, rien n’est publié.')
        return []
    url = 'https://velocemercato.fr/ballon-dor-2026.html'
    podium = data.get('podium') or []
    lines = ["🏆 BALLON D'OR 2026 : " + win.upper() + ' !']
    if data.get('note'):
        lines.append(data['note'])
    if len(podium) >= 3:
        lines.append('\n🥇 ' + podium[0] + '\n🥈 ' + podium[1] + '\n🥉 ' + podium[2])
    autres = [c for c in data.get('categories', []) if c.get('laureat') and c.get('nom') != "Ballon d'Or"]
    if autres:
        lines.append('\nLes autres trophées :\n' + '\n'.join('• ' + c['nom'] + ' : ' + c['laureat'] for c in autres[:12]))
    texte = '\n'.join(lines)
    errors = []
    meta = state.data.get('tokens', {}).get('meta') or {}
    done = state.data.setdefault('meta', {})
    slug = re.sub(r'[^a-z0-9]+', '-', win.lower())[:40]
    targets = ['discord']
    if meta.get('page_token'):
        targets += ['facebook'] + (['instagram'] if meta.get('ig_id') else [])
    for net in targets:
        key = f'ballon-dor-2026/{slug}/{net}'
        if key in done:
            continue
        done[key] = {'status': 'envoi'}
        state.save()
        try:
            if net == 'facebook':
                graph.call('POST', meta['page_id'] + '/feed', {'message': texte + '\n\nTous les lauréats 👉 ' + url
                                                                + '\n\n#BallonDor #BallonDor2026 #VeloceMercato',
                                                                'link': url, 'access_token': meta['page_token']})
            elif net == 'instagram':
                from tools.cartes_insta import push_card
                with tempfile.TemporaryDirectory(prefix='bdo-') as folder:
                    image = push_card(carte_ballon_dor(data, Path(folder) / f'ballon-dor-2026-{slug}.jpg'))
                instagram_image(graph, meta, image, texte + '\n\nTous les lauréats : lien en bio · velocemercato.fr'
                                + '\n\n#BallonDor #BallonDor2026 #football #VeloceMercato', sleep=sleep)
            else:
                from update_scores import WEBHOOK
                if not WEBHOOK.startswith('https://discord.com/api/webhooks/'):
                    raise DeliveryError('Discord : salon non configuré.')
                body = json.dumps({'content': texte[:1800] + '\n<' + url + '>', 'username': 'Véloce Mercato · Flash'}).encode()
                urllib.request.urlopen(urllib.request.Request(WEBHOOK, data=body, method='POST', headers={
                    'Content-Type': 'application/json', 'User-Agent': 'VeloceMercato/1.0'}), timeout=20).read()
            done[key] = {'status': 'publie'}
            print(f'::notice::Ballon d’Or : {net} publié')
        except (DeliveryError, OSError, subprocess.CalledProcessError) as error:
            done[key] = {'status': 'echec'}
            errors.append(f'ballon d’or {net} : {str(error)[:150]}')
        state.save()
    for line in errors:
        print('::error::' + line)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['connecter', 'publier', 'lancement', 'annonce', 'ballon-dor'])
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--article', choices=['', 'foot', 'actus', 'gaming'], default='', help='Publier un article tout de suite')
    args = parser.parse_args()
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    if args.action == 'connecter':
        names = ('META_APP_ID', 'META_APP_SECRET', 'META_USER_TOKEN')
        values = [os.getenv(name, '').strip() for name in names]
        missing = [name for name, value in zip(names, values) if not value]
        if missing:
            raise DeliveryError('Secret(s) GitHub absent(s) ou vide(s) : ' + ', '.join(missing) + ' (vérifier le nom exact).')
        # Copier-coller depuis un téléphone : ne garder que l'ID (chiffres) et la clé (32 caractères hexadécimaux).
        app_id = re.search(r'\d{10,20}', values[0])
        secret = re.search(r'\b[0-9a-fA-F]{32}\b', values[1])
        token = re.search(r'EA[A-Za-z0-9]{40,}', values[2])
        print(f'::notice::Contrôle : ID app trouvé {bool(app_id)} ({len(app_id.group(0)) if app_id else 0} chiffres) · '
              f'clé secrète au bon format {bool(secret)} (longueur {len(values[1])}, points masqués {"•" in values[1] or "*" in values[1]}, '
              f'espaces {" " in values[1]}, identique à l’ID {values[1] == values[0]}) · jeton commence par EA {bool(token)}', flush=True)
        graph = Graph()
        user_token = token.group(0) if token else values[2]
        owner = graph.call('GET', 'app', {'fields': 'id,name', 'access_token': user_token})
        print(f'::notice::Le jeton a été créé avec l’app « {str(owner.get("name", "?"))[:60]} »'
              f'{" (= META_APP_ID)" if app_id and app_id.group(0) == str(owner.get("id")) else ""}', flush=True)
        if not app_id:  # l'ID de l'app se lit depuis le jeton lui-même (information publique)
            app_id = re.search(r'\d{10,20}', str(owner.get('id', '')))
        connect(state, graph, app_id.group(0) if app_id else values[0], secret.group(0) if secret else values[1].strip(),
                user_token)
        return
    if args.action == 'annonce':
        if annonce(state, Graph()):
            sys.exit(1)
        return
    if args.action == 'ballon-dor':
        if ballon_dor(state, Graph()):
            sys.exit(1)
        return
    if args.action == 'lancement':
        if lancement(state, Graph()):
            sys.exit(1)
        return
    if os.getenv('VM_AUTO_META') != 'true':
        print('Facebook/Instagram : publication automatique non activée (VM_AUTO_META). Rien n’est publié.')
        return
    failed = False
    for account in ('meta', 'meta_univers'):
        if state.data.get('tokens', {}).get(account):
            failed |= bool(publish(state, Graph(), force=args.article or None if account == 'meta' else None, account=account))
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:  # message contrôlé, sans jeton
        message = str(error) if isinstance(error, DeliveryError) else 'Interrompu (' + type(error).__name__ + ').'
        print('::error::' + message.replace('\n', ' '))
        sys.exit(1)
