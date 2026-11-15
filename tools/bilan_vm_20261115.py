"""Envoi unique du bilan VM aux cinq destinations explicitement demandées."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.editorial_vm import identity, current_posts, instagram_room, confirm, normal, ledger
from tools.publier_meta import Graph, ensure_meta_targets
from tools.cartes_insta import push_card

LINK = 'https://velocemercato.fr/conseils/'
TITLE = 'VM — Bilan du 14 novembre et conseils du 15 novembre 2026'
TEXT = '''📊 VM · BILAN DU 14 NOVEMBRE
Public : 1 conseil réussi sur 2.
VIP : 2 conseils réussis sur 3.
Les réussites comme les échecs restent dans notre historique : le premier bilan est conservé.

👑 Ce dimanche 15 novembre, nos 3 conseils du jour sont prêts, uniquement en VIP : conseil du jour, combiné VIP et Fun VIP.
Pour les recevoir, demande à rejoindre le VIP depuis notre site. Transmission personnelle en privé, sans dévoiler les rencontres ici.

👉 https://velocemercato.fr/conseils/

🔞 18+ · Aucun résultat garanti. Jouer comporte des risques : endettement, isolement, dépendance. Joueurs Info Service : 09 74 75 13 13 (appel non surtaxé).'''
TARGETS = [('meta', 'facebook'), ('meta_univers', 'facebook'), ('meta_pronos', 'facebook'),
           ('meta', 'instagram'), ('meta_univers', 'instagram')]


def equivalent(text):
    value = normal(text)
    return ('bilan du 14 novembre' in value or
            ('public : 1' in value and 'vip : 2' in value and 'conseils' in value) or
            ('15 novembre' in value and '3 conseils' in value and 'vip' in value))


def check_page():
    with urllib.request.urlopen(LINK, timeout=30) as response:
        html = response.read(600000).decode('utf-8')
        if response.status != 200 or any(value not in html for value in
                ['historique-resultats', '2026-11-13', '1 conseil réussi sur 2', '2 conseils réussis sur 3', 'Les 3 conseils du jour sont prêts']):
            raise DeliveryError('Bilan public non vérifié : aucun envoi.')


def send_instagram(graph, meta, image):
    result = graph.call('POST', str(meta['ig_id']) + '/media',
                        {'image_url': image, 'caption': TEXT, 'access_token': meta['page_token']})
    container = str(result.get('id') or '')
    if not container.isdigit():
        raise DeliveryError('Conteneur Instagram non confirmé.')
    for attempt in range(20):
        code = graph.call('GET', container, {'fields': 'status_code', 'access_token': meta['page_token']}).get('status_code')
        if code == 'FINISHED':
            return str(graph.call('POST', str(meta['ig_id']) + '/media_publish',
                                   {'creation_id': container, 'access_token': meta['page_token']}).get('id') or '')
        if code in ('ERROR', 'EXPIRED'):
            raise DeliveryError('Traitement Instagram refusé : aucune relance.')
        time.sleep(5)
    raise DeliveryError('Traitement Instagram incertain : aucune relance.')


def run(state, graph, image_factory):
    now = dt.datetime.now(dt.timezone.utc)
    if now.astimezone(ZoneInfo('Europe/Paris')).date().isoformat() != '2026-11-15':
        return [{'status': 'edition_expiree_aucun_envoi'}]
    check_page()
    ensure_meta_targets(state)
    output = []
    image = None
    for account, network in TARGETS:
        key = 'editorial/' + network + '/bilan/bilan-20261114-annonce-20261115'
        done = ledger(state, account)
        label = account + '/' + network
        if key in done:
            output.append({'target': label, **done[key], 'new_send': False})
            continue
        meta = state.data.get('tokens', {}).get(account) or {}
        try:
            who = identity(graph, meta, account, network)
            if any(equivalent(text) for text in current_posts(graph, meta, network)):
                output.append({'target': label, 'status': 'equivalent_existant_aucun_envoi'})
                continue
            if any(isinstance(value, dict) and equivalent(value.get('title', '')) for value in done.values()):
                output.append({'target': label, 'status': 'recu_existant_ou_ambigu_aucun_envoi'})
                continue
            if network == 'facebook':
                scheduled = graph.call('GET', str(meta['page_id']) + '/scheduled_posts',
                    {'fields': 'id,message', 'limit': 100, 'access_token': meta['page_token']})
                if not isinstance(scheduled.get('data'), list):
                    raise DeliveryError('Calendrier Facebook non vérifiable.')
                if any(equivalent(row.get('message', '')) for row in scheduled['data']):
                    output.append({'target': label, 'status': 'equivalent_programme_aucun_envoi'})
                    continue
            else:
                if instagram_room(graph, meta) < 1:
                    output.append({'target': label, 'status': 'quota_atteint_aucun_envoi'})
                    continue
                if image is None:
                    image = image_factory()
            receipt = {'status': 'envoi', 'at': now.isoformat(), 'title': TITLE, 'identity': who}
            done[key] = receipt
            state.save()  # Réservation chiffrée persistée AVANT le premier POST.
            if label in ('meta_pronos/facebook', 'meta_univers/instagram'):
                receipt.update(status='reserve_metricool')
                state.save()
                output.append({'target': label, **receipt, 'image_url': image if network == 'instagram' else None})
                continue
            try:
                ident = (str(graph.call('POST', str(meta['page_id']) + '/feed',
                    {'message': TEXT, 'link': LINK, 'access_token': meta['page_token']}).get('id') or '')
                    if network == 'facebook' else send_instagram(graph, meta, image))
                receipt.update(status='envoye_a_verifier', id=ident)
                state.save()
                url = confirm(graph, meta, network, ident)
                receipt.update(status='publie_confirme', url=url)
                state.save()
            except Exception:
                receipt.update(status='a_verifier_sans_renvoi')
                state.save()
            output.append({'target': label, **receipt})
        except Exception as error:
            # Les détails de Graph peuvent contenir un jeton : seul le type est exposé.
            output.append({'target': label, 'status': 'bloque_avant_envoi', 'reason': type(error).__name__})
    return output


def main():
    path = Path(sys.argv[1])
    state = State(path, os.environ.get('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(path))
    def image_factory():
        # Visuel VM existant : conversion de format uniquement, aucune retouche.
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'vm-sport-bilan-20261115.jpg'
            Image.open(ROOT / 'app/sport-512.png').convert('RGB').save(output, 'JPEG', quality=95)
            url = push_card(output)
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200 or not response.read(3).startswith(b'\xff\xd8\xff'):
                raise DeliveryError('Image publique indisponible.')
        return url
    for row in run(state, Graph(), image_factory):
        print('VM_BILAN_RECEIPT ' + json.dumps(row, ensure_ascii=False))


if __name__ == '__main__':
    main()
