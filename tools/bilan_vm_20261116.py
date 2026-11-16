"""Envoi unique du bilan VM aux cinq destinations explicitement demandées."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import shutil
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.editorial_vm import identity, current_posts, instagram_room, confirm, normal, ledger
from tools.publier_meta import Graph, ensure_meta_targets
from tools.cartes_insta import push_card

LINK = 'https://velocemercato.fr/conseils/'
TITLE = 'VM — Bilan du 15 novembre et conseils privés du 16 au 22 novembre'
TEXT = '''📊 VM · BILAN DU 15 NOVEMBRE

✅ PUBLIC : 1 conseil réussi sur 1 · cote affichée 2,10.
✅ VIP : les 3 tickets présentés sont réussis · cotes affichées 2,10, 8,25 et 2,19.
Le ticket à 2,10 est commun au public et au VIP : il n’est pas compté deux fois dans un bilan global. Les captures et les précisions sont conservées sur le site, avec les anciens bilans et les échecs.

👑 CETTE SEMAINE, DU 16 AU 22 NOVEMBRE
Le programme sportif étant plus limité, nos conseils sont prêts et disponibles uniquement en privé.

Envie de rejoindre la VÉLOCE TEAM ? Demande ton accès VIP et retrouve les conseils et analyses en privé. Aucun match VIP à venir n’est dévoilé ici.

👇 Bilan, captures et accès VIP :
https://velocemercato.fr/conseils/

🔞 18+ · Aucun gain garanti. Jouer comporte des risques : endettement, isolement, dépendance. Joueurs Info Service : 09 74 75 13 13 (appel non surtaxé).'''
TARGETS = [('meta', 'facebook'), ('meta_univers', 'facebook'), ('meta', 'instagram')]


def equivalent(text):
    value = normal(text)
    return ('16 au 22 novembre' in value and 'conseils' in value and 'priv' in value)


def check_page():
    html = (ROOT / 'conseils/index.html').read_text(encoding='utf-8')
    data = json.loads((ROOT / 'conseils/resultats.json').read_text(encoding='utf-8'))
    rows = [r for r in data['bilans'] if r.get('date') == '2026-11-15']
    if (len(rows) != 2 or not any(r.get('type') == 'public' and r['statut'].startswith('1 conseil réussi sur 1') for r in rows)
            or not any(r.get('type') == 'vip' and r['statut'].startswith('3 conseils réussis sur 3') for r in rows)
            or 'DU 16 AU 22 NOVEMBRE 2026' not in html or 'semaine-privee-20261116' not in html
            or 'historique-resultats' not in html):
        raise DeliveryError('Bilan ou annonce hebdomadaire non conforme : aucun envoi.')


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
    if now.astimezone(ZoneInfo('Europe/Paris')).date().isoformat() != '2026-11-16':
        return [{'status': 'edition_expiree_aucun_envoi'}]
    check_page()
    ensure_meta_targets(state)
    output = []
    image = None
    for account, network in TARGETS:
        key = 'editorial/' + network + '/bilan/bilan-20261115-annonce-semaine-20261116'
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
            if any(previous_key.startswith('editorial/' + network + '/') and isinstance(value, dict)
                   and equivalent(value.get('title', '')) for previous_key, value in done.items()):
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
        # Affiche VM existante, contrôlée visuellement, sans retouche.
        url = 'https://static.metricool.com/planner/202611/7762102-file-17933189212668161188.png'
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200 or response.read(8) != b'\x89PNG\r\n\x1a\n':
                raise DeliveryError('Affiche VM indisponible.')
        return url
    output = run(state, Graph(), image_factory)
    output.extend([{'target': 'meta_pronos/facebook', 'status': 'bloque_metricool_quota_aucune_relance'},
                   {'target': 'meta_univers/instagram', 'status': 'bloque_metricool_quota_aucune_relance'}])
    (ROOT / 'studio/bilan-20261116-receipts.json').write_text(
        json.dumps({'at': dt.datetime.now(dt.timezone.utc).isoformat(), 'targets': output}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8')
    for row in output:
        print('VM_BILAN_RECEIPT ' + json.dumps(row, ensure_ascii=False))
    import subprocess
    subprocess.run(['git', 'add', 'studio/bilan-20261116-receipts.json'], check=True)
    subprocess.run(['git', '-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                    'commit', '-m', 'Accusés du bilan du 15 novembre et de la semaine privée'], check=True)
    subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=True)
    subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)


if __name__ == '__main__':
    main()
