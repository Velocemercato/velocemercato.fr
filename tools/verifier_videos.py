#!/usr/bin/env python3
"""Vérifie auprès de YouTube (oEmbed, public, sans clé) la chaîne qui a publié chaque vidéo ou playlist.

Usage : python tools/verifier_videos.py tools/videos-a-verifier.json
Écrit le résultat dans tools/videos-verifiees.json et l'affiche : titre, chaîne, URL de la chaîne,
ou l'erreur (vidéo supprimée, privée ou non intégrable).
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def oembed(url):
    q = 'https://www.youtube.com/oembed?' + urllib.parse.urlencode({'url': url, 'format': 'json'})
    req = urllib.request.Request(q, headers={'User-Agent': 'VM-Verification/1.0 (+https://velocemercato.fr/)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
        return {'ok': True, 'titre': d.get('title'), 'chaine': d.get('author_name'), 'chaine_url': d.get('author_url')}
    except urllib.error.HTTPError as exc:
        return {'ok': False, 'erreur': f'HTTP {exc.code}'}
    except Exception as exc:  # réseau
        return {'ok': False, 'erreur': type(exc).__name__}


def main(entree):
    data = json.loads(Path(entree).read_text(encoding='utf-8'))
    res = {}
    for vid in data.get('videos', []):
        res[vid] = oembed(f'https://www.youtube.com/watch?v={vid}')
        time.sleep(0.3)
    for pl in data.get('playlists', []):
        res[pl] = oembed(f'https://www.youtube.com/playlist?list={pl}')
        time.sleep(0.3)
    sortie = Path(entree).with_name('videos-verifiees.json')
    sortie.write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    for k, v in res.items():
        print(k, '|', v.get('chaine') or v.get('erreur'), '|', v.get('chaine_url') or '', '|', (v.get('titre') or '')[:90])
    print(f'{sum(v["ok"] for v in res.values())}/{len(res)} trouvées')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'tools/videos-a-verifier.json')
