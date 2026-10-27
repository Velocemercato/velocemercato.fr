"""Mesure d'audience Cloudflare Web Analytics (sans cookie), chargée seulement sur le vrai domaine.
Usage : python vmstats.py  (ajoute le compteur aux pages qui ne l'ont pas encore)."""
from pathlib import Path

TOKEN = '35ce3d9fb9144124a0bb97db4e89dbb2'
HOSTS = ('velocemercato.fr', 'www.velocemercato.fr')
SNIPPET = ('<!-- Cloudflare Web Analytics --><script id="vm-cfwa">(function(h){if(' +
           '||'.join(f"h==='{x}'" for x in HOSTS) +
           "){var s=document.createElement('script');s.defer=true;"
           "s.src='https://static.cloudflareinsights.com/beacon.min.js';"
           "s.setAttribute('data-cf-beacon','{\"token\": \"" + TOKEN + "\"}');"
           "document.head.appendChild(s)}})(location.hostname)</script>")


def add(html):
    """Ajoute le compteur une seule fois, juste avant </head>."""
    if 'id="vm-cfwa"' in html or '</head>' not in html:
        return html
    return html.replace('</head>', SNIPPET + '</head>', 1)


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    n = 0
    for p in root.rglob('*.html'):
        if '.git' in p.parts or 'tests' in p.parts:
            continue
        s = p.read_text(encoding='utf-8')
        t = add(s)
        if t != s:
            p.write_text(t, encoding='utf-8'); n += 1
    print(n, 'pages')
