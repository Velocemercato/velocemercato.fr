"""Compléments VM Studio Express : photos du commerce en exemple privé 24 h, et carte QR à montrer.

Photos : uniquement celles de la page Planity du commerce (ou de son propre site), affichées depuis
leur source sans être copiées, avec un bandeau « exemple privé, 24 h » ; passé ce délai, la page
revient d'elle-même aux illustrations.
"""
import datetime as dt
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
      'Accept-Language': 'fr-FR,fr;q=0.9'}
ANNUAIRES = ('pagesjaunes', 'mappy', 'google', 'facebook', 'instagram', 'tripadvisor', 'yelp', 'fnc.fr', 'icoiffeur',
             'lorealprofessionnel', 'societe.com', 'pappers', 'treatwell', 'justacote', 'cylex', 'hoodspot', 'waze', 'restaurants-de-france', 'restaurantguru', 'ubereats', 'deliveroo', 'just-eat', 'thefork')
PLANITY = re.compile(r'https://res\.cloudinary\.com/planity/image/upload/[^"\'\s)>]*?/([a-z0-9]{16,40})(?=["\'\s)>?]|$)')


def _get(url, limit=3_000_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read(limit).decode('utf-8', 'replace')


def find_photos(urls, maxi=12):
    """Photos publiques du commerce : page Planity du salon, sinon image de partage de son propre site."""
    found = []
    for u in urls:
        if not re.match(r'^https://', u or ''):
            continue
        host = re.sub(r'^https://(www\.)?', '', u).split('/')[0]
        path = u.split(host, 1)[-1].strip('/')
        try:
            if 'planity.com' in host and path and '/' not in path:  # page d'UN salon, pas une liste de la ville
                for pid in dict.fromkeys(m.group(1) for m in PLANITY.finditer(_get(u))):
                    found.append(f'https://res.cloudinary.com/planity/image/upload/t_d_search,f_auto/{pid}')
            elif not any(a in host for a in ANNUAIRES):  # son propre site
                m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](https://[^"\']+)', _get(u, 400_000))
                if m:
                    found.append(html.unescape(m.group(1)))
        except Exception as exc:  # page bloquée ou absente : on continue sans
            print(f'Photos non récupérées sur {host} : {type(exc).__name__}', flush=True)
    return list(dict.fromkeys(found))[:maxi]


def apply_photos(page_path, photos, nom, hours=48):
    """Remplace les illustrations par les photos du commerce pour un exemple privé limité dans le temps."""
    s = Path(page_path).read_text(encoding='utf-8')
    if not photos:
        return None
    k = [0]

    def rep(m):
        u = photos[k[0] % len(photos)]
        k[0] += 1
        return f'data-img="{html.escape(u, quote=True)}" data-orig="{m.group(1)}"'
    s = re.sub(r'data-img="(/demos/img/[^"]+)"', rep, s)
    m = re.search(r'window\.DEMO=(\{.*?\});\s*</script>', s, re.S)
    try:
        d = json.loads(m.group(1).replace('<\\/', '</')) if m else None
    except json.JSONDecodeError:  # configuration écrite en JS (modèles de base) : on laisse les vignettes
        d = None
    if d is not None:
        lists = [d.get('booking', {}).get('services'), d.get('order', {}).get('items'), d.get('order', {}).get('products')]
        n = 0
        for lst in [x for x in lists if isinstance(x, list)]:
            for item in lst:
                if isinstance(item, dict) and item.get('img'):
                    item['img_orig'] = item['img']
                    item['img'] = photos[(n + 3) % len(photos)]
                    n += 1
        s = s[:m.start(1)] + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + s[m.end(1):]
    nom_e = html.escape(nom)
    if hours:  # exemple limité dans le temps : retour aux illustrations après le délai
        fin = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=hours)).replace(microsecond=0)
        duree = f'valable {hours} h. Les photos viennent de votre page publique et disparaissent ensuite automatiquement.'
        script = ('<script>\n// Après le délai : retour automatique aux illustrations.\n'
                  f"(function(){{var fin=Date.parse('{fin.isoformat().replace('+00:00', 'Z')}');if(Date.now()<fin)return;"
                  "document.getElementById('vm-exemple').textContent='Exemple de site préparé par VM Studio (illustrations).';"
                  "document.querySelectorAll('[data-orig]').forEach(function(e){e.setAttribute('data-img',e.getAttribute('data-orig'))});"
                  "if(window.DEMO){[DEMO.booking&&DEMO.booking.services,DEMO.order&&DEMO.order.items,DEMO.order&&DEMO.order.products]"
                  ".forEach(function(l){(l||[]).forEach(function(v){if(v.img_orig)v.img=v.img_orig})})}})();\n</script>\n")
    else:  # sans date de fin (choix de Romain) : rien ne s'efface tout seul
        fin, script = None, ''
        duree = 'Les photos viennent de votre page publique ; elles ne sont pas réutilisées sans votre accord.'
    banner = (f'<div id="vm-exemple" style="position:sticky;top:0;z-index:99;background:#e1243a;color:#fff;'
              f'font:700 14px/1.35 system-ui,sans-serif;padding:10px 14px;text-align:center">Exemple privé préparé pour '
              f'{nom_e}. {duree}</div>')
    s = s.replace('<body>', '<body>\n' + banner, 1)
    if script:
        i = s.find('<script src="/demos/kit/vm-demo.js')
        s = s[:i] + script + s[i:] if i >= 0 else s.replace('</body>', script + '</body>', 1)
    s = s.replace('Images d’illustration : vos vraies photos les remplaceront.',
                  'Photos issues de la page publique du commerce, pour cet exemple privé.', 1)
    s = s.replace('<meta name="robots" content="noindex,nofollow">', '<meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer">', 1)
    Path(page_path).write_text(s, encoding='utf-8')
    return fin.isoformat() if fin else None


def qr_card(url, nom, base, out, photos_ok):
    """Carte téléphone 1080x1920 : nom du commerce, QR vers sa maquette, VM Studio."""
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1080, 1920
    bold, med = str(ROOT / 'studio/assets/Poppins-Bold.ttf'), str(ROOT / 'studio/assets/Poppins-Medium.ttf')
    f = lambda p, s: ImageFont.truetype(p, s)  # noqa: E731
    try:
        bg = Image.open(ROOT / f'demos/img/{base}/hero.webp').convert('RGB')
        r = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * r) + 1, int(bg.height * r) + 1))
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = Image.blend(bg, Image.new('RGB', (W, H), (12, 8, 22)), .62)
    except Exception:
        bg = Image.new('RGB', (W, H), (12, 8, 22))
    d = ImageDraw.Draw(bg)

    def fit(text, size, maxw=940):
        while size > 40 and d.textlength(text, font=f(bold, size)) > maxw:
            size -= 4
        return f(bold, size)
    d.text((70, 110), 'Pour', font=f(med, 50), fill=(235, 238, 248))
    d.text((70, 170), nom, font=fit(nom, 104), fill=(244, 207, 85))
    d.text((70, 330), 'Votre futur site,', font=f(bold, 62), fill=(255, 255, 255))
    d.text((70, 405), 'à regarder tranquillement.', font=f(bold, 62), fill=(255, 255, 255))
    d.text((70, 510), 'Scannez avec l’appareil photo.', font=f(med, 44), fill=(235, 238, 248))
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    q.add_data(url)
    q.make(fit=True)
    qi = q.make_image(fill_color='black', back_color='white').convert('RGB').resize((700, 700), Image.NEAREST)
    x, y = (W - 760) // 2, 620
    d.rounded_rectangle((x, y, x + 760, y + 760), 30, fill=(255, 255, 255))
    bg.paste(qi, (x + 30, y + 30))
    d.text((70, 1440), 'Maquette préparée par VM Studio', font=f(bold, 46), fill=(244, 207, 85))
    d.text((70, 1505), 'Sans engagement · prix fixe · tout à distance', font=f(med, 40), fill=(255, 255, 255))
    d.text((70, 1570), 'Vos posts Facebook & Instagram publiés pour vous', font=f(bold, 34), fill=(244, 207, 85))
    d.text((70, 1630), 'VM Studio · vminvest.fr@gmail.com', font=f(med, 44), fill=(255, 255, 255))
    d.text((70, 1710), 'Démonstration non officielle : réservations et paiements simulés.', font=f(med, 30), fill=(200, 205, 220))
    d.text((70, 1755), 'Photos du commerce · prix à titre d’exemple.' if photos_ok else 'Illustrations · prix à titre d’exemple.', font=f(med, 30), fill=(200, 205, 220))
    bg.save(out, 'PNG', optimize=True)
    return out


FEMININ_CSS = '<style id="vm-feminin">\n/* Style féminin : tons poudrés, titres élégants, sans effets BD */\n.vd-hero{background:linear-gradient(160deg,#fff6f8 0%,#fbe3ea 55%,#f5d0dc 100%)!important;color:var(--ink)!important}\n.vd-hero:before{background:radial-gradient(circle at 80% 20%,color-mix(in srgb,var(--a) 18%,transparent) 0 35%,transparent 36%)!important;opacity:1}\n.vd-hero:after{background:radial-gradient(color-mix(in srgb,var(--a) 14%,transparent) 1px,transparent 1.6px) 0 0/14px 14px!important}\n.vd-hero h1{font:italic 600 clamp(2.2rem,7vw,3.8rem)/1.05 Georgia,"Playfair Display","Times New Roman",serif!important;text-transform:none!important;text-shadow:none!important;color:var(--ink)!important;letter-spacing:0!important}\n.vd-hero p.lead{color:#4a3540!important}\n.vd-hero .vd-chip{background:#fff!important;color:var(--ink)!important;border-color:color-mix(in srgb,var(--a) 35%,#fff)!important}\n.vd-hero-art .vd-media{box-shadow:0 18px 40px color-mix(in srgb,var(--a) 30%,transparent)!important;border:3px solid #fff!important;transform:none!important}\n.vd-sfx{display:none!important}\n.vd-h h2,section h2{font-family:Georgia,"Playfair Display",serif!important;font-style:italic;text-transform:none!important;font-weight:600!important}\n.vd-btn{border-radius:999px!important}\n</style>'


def feminize(page_path):
    """Style féminin (tons poudrés, titres élégants, sans effets BD) et prestations Femme en premier."""
    s = Path(page_path).read_text(encoding='utf-8')
    s = re.sub(r'<style id="vm-feminin">.*?</style>', '', s, flags=re.S).replace('</head>', FEMININ_CSS + '</head>', 1)
    m = re.search(r'window\.DEMO=(\{.*?\});\s*</script>', s, re.S)
    try:
        d = json.loads(m.group(1).replace('<\\/', '</')) if m else None
    except json.JSONDecodeError:
        d = None
    if d and isinstance(d.get('booking'), dict):
        order = {'Femme': 0, 'Coiffure': 0, 'Couleur': 1, 'Soins': 2, 'Homme': 5, 'Enfant': 6}
        d['booking'].get('services', []).sort(key=lambda x: order.get(x.get('cat'), 3))
        d['booking'].get('staff', []).sort(key=lambda x: 0 if 'oiffeuse' in x.get('role', '') + x.get('name', '') else 1)
        s = s[:m.start(1)] + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + s[m.end(1):]
    Path(page_path).write_text(s, encoding='utf-8')
