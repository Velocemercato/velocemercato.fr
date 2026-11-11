#!/usr/bin/env python3
"""Statistiques privées des deux sites (Cloudflare Web Analytics), chiffrées par mot de passe.

Lit l'API GraphQL de Cloudflare avec une clé « Account Analytics : lecture » puis écrit
stats/donnees.chiffre.json, lisible seulement sur /stats/ avec le code choisi par Romain.
Le dépôt étant public, rien n'est jamais écrit en clair.

Secrets GitHub : CLOUDFLARE_ANALYTICS_TOKEN, CLOUDFLARE_ACCOUNT_ID, STATS_CODE.
Sans eux, le script s'arrête sans rien modifier.
"""

import base64
import datetime as dt
import json
import os
import secrets
import sys
import urllib.request
from pathlib import Path

SITES = {'velocemercato.fr': 'Véloce Mercato', 'vmunivers.fr': 'VM Univers'}
OUT = Path(__file__).resolve().parents[1] / 'stats' / 'donnees.chiffre.json'
API = 'https://api.cloudflare.com/client/v4/graphql'
ITERATIONS = 250_000

QUERY = '''
query Stats($account: string!, $host: string!, $from: Date!, $to: Date!, $from7: Date!) {
  viewer { accounts(filter: { accountTag: $account }) {
    jours: rumPageloadEventsAdaptiveGroups(limit: 100, orderBy: [date_ASC],
      filter: { requestHost: $host, date_geq: $from, date_leq: $to, bot: 0 }) {
      count sum { visits } dimensions { date } }
    pages: rumPageloadEventsAdaptiveGroups(limit: 15, orderBy: [count_DESC],
      filter: { requestHost: $host, date_geq: $from7, date_leq: $to, bot: 0 }) {
      count dimensions { requestPath } }
    sources: rumPageloadEventsAdaptiveGroups(limit: 12, orderBy: [sum_visits_DESC],
      filter: { requestHost: $host, date_geq: $from7, date_leq: $to, bot: 0 }) {
      sum { visits } dimensions { refererHost } }
    pays: rumPageloadEventsAdaptiveGroups(limit: 10, orderBy: [sum_visits_DESC],
      filter: { requestHost: $host, date_geq: $from7, date_leq: $to, bot: 0 }) {
      sum { visits } dimensions { countryName } }
    appareils: rumPageloadEventsAdaptiveGroups(limit: 5, orderBy: [sum_visits_DESC],
      filter: { requestHost: $host, date_geq: $from7, date_leq: $to, bot: 0 }) {
      sum { visits } dimensions { deviceType } }
  } }
}'''


def graphql(token, variables):
    body = json.dumps({'query': QUERY, 'variables': variables}).encode()
    req = urllib.request.Request(API, data=body, headers={
        'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get('errors'):
        raise RuntimeError('; '.join(e.get('message', '?') for e in data['errors']))
    comptes = data['data']['viewer']['accounts']
    if not comptes:
        raise RuntimeError('compte Cloudflare introuvable avec cette clé')
    return comptes[0]


def site(token, account, host, today):
    r = graphql(token, {'account': account, 'host': host,
                        'from': str(today - dt.timedelta(days=29)), 'to': str(today),
                        'from7': str(today - dt.timedelta(days=6))})
    jours = [{'date': x['dimensions']['date'], 'vues': x['count'], 'visites': x['sum']['visits']}
             for x in r['jours']]
    return {
        'nom': SITES[host],
        'jours': jours,
        'pages': [{'page': x['dimensions']['requestPath'], 'vues': x['count']} for x in r['pages']],
        'sources': [{'source': x['dimensions']['refererHost'] or 'Accès direct', 'visites': x['sum']['visits']}
                    for x in r['sources']],
        'pays': [{'pays': x['dimensions']['countryName'] or '?', 'visites': x['sum']['visits']} for x in r['pays']],
        'appareils': [{'type': x['dimensions']['deviceType'] or '?', 'visites': x['sum']['visits']}
                      for x in r['appareils']],
    }


def chiffrer(donnees, code):
    """AES-256-GCM, clé dérivée du code par PBKDF2-SHA256 (déchiffrable par WebCrypto dans /stats/)."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    sel, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    cle = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sel, iterations=ITERATIONS).derive(code.encode())
    clair = json.dumps(donnees, ensure_ascii=False).encode()
    b64 = lambda b: base64.b64encode(b).decode()
    return {'version': 1, 'iterations': ITERATIONS, 'sel': b64(sel), 'iv': b64(iv),
            'donnees': b64(AESGCM(cle).encrypt(iv, clair, None))}


def main():
    token = os.getenv('CLOUDFLARE_ANALYTICS_TOKEN', '').strip()
    account = os.getenv('CLOUDFLARE_ACCOUNT_ID', '').strip()
    code = os.getenv('STATS_CODE', '').strip()
    if not (token and account and code):
        print('::notice::Statistiques non activées : ajouter CLOUDFLARE_ANALYTICS_TOKEN et STATS_CODE '
              '(et CLOUDFLARE_ACCOUNT_ID) dans les secrets GitHub.')
        return 0
    if len(code) < 8:
        print('::error::STATS_CODE doit faire au moins 8 caractères.')
        return 1
    today = dt.datetime.now(dt.timezone.utc).date()
    donnees = {'maj': dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes'), 'sites': {}}
    for host in SITES:
        try:
            donnees['sites'][host] = site(token, account, host, today)
        except Exception as exc:  # un site indisponible n'efface pas l'autre
            donnees['sites'][host] = {'nom': SITES[host], 'erreur': f'{type(exc).__name__} : {str(exc)[:160]}'}
            print(f'::warning::{host} : {exc}')
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(chiffrer(donnees, code)) + '\n', encoding='utf-8')
    print('Statistiques chiffrées écrites :', ', '.join(
        f"{h} {sum(j['visites'] for j in s.get('jours', []))} visites/30 j" for h, s in donnees['sites'].items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
