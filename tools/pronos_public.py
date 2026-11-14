#!/usr/bin/env python3
"""Page publique VM Actus & Pronos à partir des seules sources du dépôt.

Aucune publication Meta, aucun jeton, aucune analyse de pari. Les fichiers JSON
sont relus à chaque génération quotidienne/automatique des articles.
"""
import datetime as dt
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pronos/index.html"
NEWS = (
    ("Football", "articles.json", "⚽"),
    ("Actualités", "actus/news.json", "📰"),
    ("Gaming", "vm-gaming/news.json", "🎮"),
)
RISK = "18+ · Jouer comporte des risques : endettement, isolement, dépendance · Joueurs Info Service 09 74 75 13 13"
OFFICIAL = {"ligue1.com", "www.ligue1.com", "lfp.fr", "www.lfp.fr",
            "liverpoolfc.com", "www.liverpoolfc.com", "lfcbeta.liverpoolfc.com",
            "premierleague.com", "www.premierleague.com", "fplchallenge.premierleague.com"}
ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,99}$")
YOUTUBE = re.compile(r"^https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$")


def load(root, path, fallback):
    try:
        return json.loads((Path(root) / path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback


def parsed(raw):
    try:
        d = dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return d if d.tzinfo else None
    except (ValueError, TypeError):
        return None


def safe_url(url):
    try:
        p = urlparse(str(url or ""))
        return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password
    except (ValueError, TypeError):
        return False


def e(text):
    return html.escape(str(text or ""), quote=True)


def recent_articles(root, path, now, limit=5):
    rows = load(root, path, [])
    if not isinstance(rows, list):
        return []
    valid = []
    for row in rows:
        if not isinstance(row, dict) or not ID.fullmatch(str(row.get("id") or "")):
            continue
        date = parsed(row.get("publishedAt"))
        if date is None or not dt.timedelta(0) <= now - date <= dt.timedelta(hours=48):
            continue
        if not row.get("titre") or not row.get("resume"):
            continue
        sources = row.get("sources") or []
        if not isinstance(sources, list):
            continue
        source = next((src for src in sources if isinstance(src, dict) and
                       src.get("nom") and safe_url(src.get("url"))), None)
        if source is not None:
            valid.append((date, row, source))
    return sorted(valid, key=lambda r: r[0], reverse=True)[:limit]


def section_news(root, now):
    sections = []
    for title, path, emoji in NEWS:
        items = recent_articles(root, path, now)
        lines = [f'<section class="panel" id="{e(title.lower().replace("é", "e"))}">',
                 f'<h2>{emoji} {e(title)}</h2>']
        if not items:
            lines.append('<p>Pas de nouvelle brève suffisamment récente et sourcée pour cette rubrique.</p>')
        for when, row, src in items:
            link = str(src["url"])
            if path == "articles.json" and (Path(root) / "a" / (row["id"] + ".html")).is_file():
                link = "https://velocemercato.fr/a/" + row["id"] + ".html"
            stamp = when.astimezone(PARIS).strftime("%d/%m/%Y %H:%M")
            lines.append(
                f'<article class="news"><p class="meta">{e(stamp)} · Source : {e(src["nom"])}</p>'
                f'<h3><a href="{e(link)}" target="_blank" rel="noopener noreferrer">{e(row["titre"])}</a></h3>'
                f'<p>{e(str(row["resume"])[:420])}</p>'
                f'<a class="source" href="{e(src["url"])}" target="_blank" rel="noopener noreferrer">Source originale</a>'
                '</article>')
        sections.append("\n".join(lines + ["</section>"]))
    return "\n".join(sections)


def section_agenda(root, now):
    today = now.astimezone(PARIS).date().isoformat()
    data = load(root, "programmes/avant_match_" + today + ".json", {})
    rows = data.get("matches") if isinstance(data, dict) and data.get("date_matchs") == today else None
    html_rows = []
    if isinstance(rows, list):
        for row in rows[:8]:
            if not isinstance(row, dict) or row.get("official_verified") is not True:
                continue
            sources = row.get("sources") or []
            official = next((s for s in sources if isinstance(s, dict) and
                             safe_url(s.get("url")) and urlparse(s["url"]).hostname in OFFICIAL), None)
            if not official or not row.get("affiche") or not row.get("heure_paris"):
                continue
            html_rows.append(
                '<li><b>' + e(row["affiche"]) + '</b> · ' + e(row["heure_paris"]) +
                ' (Paris) · <a href="' + e(official["url"]) +
                '" target="_blank" rel="noopener noreferrer">Source officielle</a></li>')
    result = ['<section class="panel" id="agenda"><h2>📅 Matchs officiels du jour</h2>']
    if html_rows:
        result.append('<ul class="agenda">' + "\n".join(html_rows) + '</ul>')
    else:
        result.append('<p>Aucune affiche du jour suffisamment vérifiée dans le programme. '
                      'Les matchs ne sont pas inventés pour remplir cette section.</p>')
    result.append('<p class="risk">🎲 Simulation éducative : 100 points fictifs, aucune mise réelle '
                  'ni résultat garanti. Aucun pourcentage ni combiné inventé.<br>' + e(RISK) + '</p></section>')
    return "\n".join(result)


SELECTIONS = (
    # (fichier, ancre, titre, exige une validation humaine)
    ("pronos/selection.json", "pronos-du-jour", "👑 Les pronos du jour VM", True),
    ("pronos/analyse-claude.json", "analyse-claude", "🤖 L'analyse prono de Claude", False),
)


def selection_active(data, now, humain=True):
    """Une sélection n'est visible que pendant sa fenêtre de validité, et :
    - pronos du propriétaire : « valide »: true ET « valide_par » renseigné ;
    - analyse de Claude : « publie_sans_validation »: true (mention affichée en clair)."""
    if not isinstance(data, dict):
        return False
    if humain:
        if data.get("valide") is not True or not str(data.get("valide_par") or "").strip():
            return False
    elif data.get("publie_sans_validation") is not True:
        return False
    debut, fin = parsed(data.get("debut")), parsed(data.get("expire"))
    return debut is not None and fin is not None and debut <= now < fin


def section_selection(root, now):
    return "".join(section_une_selection(root, now, *row) for row in SELECTIONS)


def section_une_selection(root, now, path, anchor, title, humain):
    data = load(root, path, {})
    if not selection_active(data, now, humain):
        return ""
    blocs = []
    plafond = data.get("cote_max_public")
    for combo in data.get("combines") or []:
        if not isinstance(combo, dict) or not combo.get("titre"):
            continue
        if plafond is not None:
            # Règle du propriétaire : seul un prono public à cote inférieure au plafond (2) est affiché.
            try:
                if float(str(combo.get("cote")).replace(",", ".").strip("≈ ")) >= float(plafond):
                    continue
            except ValueError:
                continue
        rows = []
        for leg in combo.get("selections") or []:
            if not isinstance(leg, dict) or not leg.get("match") or not leg.get("marche"):
                continue
            src = leg.get("source") or {}
            lien = (f' · <a href="{e(src["url"])}" target="_blank" rel="noopener noreferrer">{e(src.get("nom") or "Source")}</a>'
                    if isinstance(src, dict) and safe_url(src.get("url")) else "")
            rows.append(f'<li><b>{e(leg["match"])}</b> · {e(leg.get("heure_paris"))} · {e(leg["marche"])}'
                        f' · cote relevée {e(leg.get("cote"))} · estimation {e(leg.get("probabilite"))}'
                        f' ({e(leg.get("type_estimation"))}){lien}</li>')
        if rows:
            blocs.append(f'<article class="news"><h3>{e(combo["titre"])}</h3><ul class="agenda">' + "".join(rows) +
                         f'</ul><p class="meta">Probabilité combinée estimée : {e(combo.get("probabilite"))}'
                         f' · cote combinée indicative : {e(combo.get("cote"))}. {e(combo.get("note"))}</p></article>')
    if not blocs:
        return ""
    verif = parsed(data.get("verifie_le"))
    stamp = verif.astimezone(PARIS).strftime("%d/%m/%Y à %H:%M") if verif else "?"
    if humain:
        qui = f'validé par {e(data["valide_par"])}'
    else:
        qui = ("<b>publié automatiquement par Claude (IA), sans validation du propriétaire du site</b>")
    analyse = f'<p>{e(data["analyse"])}</p>' if data.get("analyse") else ""
    return (f'<section class="panel" id="{e(anchor)}"><h2>{e(title)}</h2>'
            f'<p class="meta">Données vérifiées le {e(stamp)} (Paris) · {qui}. '
            'Estimations externes, cotes indicatives qui évoluent : aucun résultat garanti.</p>'
            + analyse + "\n".join(blocs) +
            '<p><a href="#acces-vip" style="display:inline-block;background:#111;color:#ffe27b;border:2px solid #f4cf55;'
            'border-radius:10px;padding:10px 14px;font-weight:900;text-decoration:none">🔒 Les autres pronos en VIP : demander mon accès gratuit →</a></p>'
            '<p class="risk">Un combiné multiplie les risques : sa probabilité est le produit de celles de chaque sélection. '
            'Ni conseil, ni promesse de gain.<br>' + e(RISK) + ' · Les jeux d’argent sont interdits aux mineurs.</p></section>')



def section_affiches_publiques(root, now):
    """Galerie temporaire : seulement des images publiques réellement présentes."""
    data = load(root, "pronos/affiches-public.json", {})
    if not isinstance(data, dict) or data.get("actif") is not True:
        return ""
    debut, fin = parsed(data.get("debut")), parsed(data.get("expire"))
    if debut is None or fin is None or not debut <= now < fin:
        return ""
    images = []
    for row in data.get("affiches", [])[:4]:
        if not isinstance(row, dict):
            continue
        name = str(row.get("fichier") or "")
        if not re.fullmatch(r"[a-z0-9-]+\.(?:png|jpg)", name):
            continue
        if not (Path(root) / "pronos" / "affiches" / name).is_file():
            continue
        title = e(row.get("titre") or "Affiche")
        images.append(
            '<figure style="margin:0;background:#071126;border:1px solid #f4cf55;'
            'border-radius:12px;overflow:hidden">'
            f'<img src="/pronos/affiches/{e(name)}" alt="{title}" loading="lazy" '
            'style="width:100%;height:auto;display:block">'
            f'<figcaption style="padding:10px">{title}</figcaption></figure>'
        )
    if not images:
        return ""
    return ('<section class="panel" id="affiches-du-jour" style="border:2px solid #f4cf55">'
            '<h2>🖼️ Affiches publiques du jour</h2>'
            '<p>Documents fournis par la rédaction VM. Cotes indicatives non vérifiées en temps réel. '
            'Les probabilités implicites des affiches ne sont pas des chances réelles garanties.</p>'
            '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));'
            'gap:16px">' + "".join(images) + '</div>'
            '<p class="risk">18+ · Aucun gain garanti · '
            + e(RISK) + '</p></section>')



def section_acces(root):
    """Encadré « Accès VIP » : un simple lien email (aucune donnée collectée par le site)."""
    from urllib.parse import quote
    data = load(root, "pronos/acces.json", {})
    email = str(data.get("email") or "") if isinstance(data, dict) else ""
    if not (isinstance(data, dict) and data.get("actif") is True and re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", email)):
        return ""
    href = ("mailto:" + email + "?subject=" + quote(str(data.get("sujet") or "Accès VIP pronos VM"))
            + "&body=" + quote(str(data.get("corps") or "")))
    return ('<section class="panel" id="acces-vip" style="border:2px solid #f4cf55">'
            f'<h2>{e(data.get("titre") or "🔒 Pronos VIP")}</h2><p>{e(data.get("texte"))}</p>'
            f'<p><a href="{e(href)}" style="display:inline-block;background:#f4cf55;color:#111;font-weight:900;'
            f'padding:12px 16px;border-radius:10px;text-decoration:none">{e(data.get("bouton") or "📩 Demander mon accès")}</a>'
            f' <span class="meta">ou écris à <b>{e(email)}</b></span></p>'
            f'<p class="meta">{e(data.get("rgpd"))}</p><p class="risk">{e(RISK)} · Interdit aux mineurs</p></section>')


def section_videos(root, now):
    rows = load(root, "studio/diffusions.json", [])
    choices = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        date = parsed(row.get("date_publication"))
        video = (row.get("plateformes") or {}).get("youtube") or {}
        if (date and dt.timedelta(0) <= now - date <= dt.timedelta(hours=48)
                and video.get("status") == "published" and
                YOUTUBE.fullmatch(str(video.get("url") or ""))):
            choices.append((date, str(row.get("titre") or "JT VM"), video["url"]))
    choices.sort(reverse=True)
    parts = ['<section class="panel"><h2>🎬 JT publiés</h2>']
    if not choices:
        parts.append("<p>Aucun lien YouTube récent confirmé dans le registre.</p>")
    else:
        parts.append('<ul class="agenda">')
        for date, title, url in choices[:4]:
            parts.append(f'<li><a href="{e(url)}" target="_blank" rel="noopener noreferrer">'
                         f'{e(title)}</a> · {e(date.astimezone(PARIS).strftime("%d/%m %H:%M"))}</li>')
        parts.append("</ul>")
    return "\n".join(parts + ["</section>"])


def render(root=ROOT, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Horodatage sans fuseau")
    local = now.astimezone(PARIS)
    updated = local.strftime("%d/%m/%Y à %H:%M (Paris)")
    content = section_affiches_publiques(root, now) + section_acces(root) + section_selection(root, now) + section_news(root, now) + section_agenda(root, now) + section_videos(root, now)
    return """<!doctype html>
<html lang="fr" data-vmt="pronos"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VM Actus &amp; Pronos — Actualités et agenda sportif</title>
<meta name="description" content="Actualités football, informations générales, gaming et agenda sportif sourcé. Pronostics uniquement fictifs.">
<link rel="canonical" href="https://velocemercato.fr/pronos/">
<meta name="theme-color" content="#0a1735">
<style>
:root{color-scheme:dark;--bg:#071126;--card:#132449;--ink:#fff;--muted:#c5d3ec;--gold:#f4cf55}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
a{color:var(--gold)}header{background:linear-gradient(115deg,#173b91,#081228);border-bottom:4px solid var(--gold);padding:22px 18px}
header>div,main,footer{max-width:940px;margin:auto}h1{font-size:clamp(1.7rem,5vw,2.7rem);line-height:1.15;margin:0 0 9px}
header p{margin:4px 0;color:var(--muted)}nav{display:flex;flex-wrap:wrap;gap:9px;margin-top:16px}
nav a{border:1px solid var(--gold);border-radius:999px;padding:7px 12px;text-decoration:none;font-weight:700}
main{padding:24px 15px 48px;display:grid;gap:18px}
.panel{background:var(--card);border:1px solid #4868a7;border-radius:15px;padding:18px}
.panel h2{font-size:1.45rem;margin:0 0 10px}.news{padding:14px 0;border-top:1px solid #3b5485}
.news h3{font-size:1.1rem;margin:4px 0}.news h3 a{color:#fff}.news p{margin:5px 0}
.meta{font-size:.8rem;color:var(--muted)}.source{font-size:.88rem}
.agenda{padding-left:20px}.agenda li{padding:5px 0}.risk{font-size:.87rem;color:var(--muted);margin-top:18px}
footer{padding:15px 20px 30px;color:var(--muted);font-size:.85rem}
</style><link rel="stylesheet" href="/notifications/alertes.css"><script src="/notifications/alertes.js" defer></script><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,700;0,800;1,800;1,900&family=Knewave&family=Permanent+Marker&display=swap"><link rel="stylesheet" href="/assets/vm-theme.css"></head><body>
<header class="vmt-hero"><div><h1>⚽ VM ACTUS &amp; PRONOS</h1>
<p>Les informations du jour, le foot, le gaming et les matchs sourcés. Aucun pari réel.</p>
<p><strong>Édition actualisée : __UPDATED__</strong></p>
<nav><a href="/notifications/">🔔 Mes alertes</a><a href="#football">Football</a><a href="#actualites">Actualités</a>
<a href="#gaming">Gaming</a><a href="#agenda">Matchs du jour</a>
<a href="https://www.facebook.com/share/1E6nH6RZzX/" target="_blank" rel="noopener noreferrer">Page Facebook Veloce Mercato</a>
<a href="https://velocemercato.fr/">VeloceMercato</a></nav></div></header>
<aside aria-label="Les univers Véloce Mercato" style="max-width:1180px;margin:15px auto;padding:13px 18px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;background:linear-gradient(100deg,#6b0c28,#0a1a3f);color:#fff;border:2px solid #fa4665;border-radius:13px"><div><b style="font:900 22px Impact,system-ui;color:#ffe078">📺 VM MANGAS : LE CLUB NOSTALGIE</b><p style="margin:4px 0;font:700 13px system-ui">Olive et Tom, L'École des champions… et tous les sports dans notre univers VM !</p></div><div style="display:flex;gap:8px;flex-wrap:wrap"><a style="color:#fff;background:#d71b42;border:1px solid #ffbdc7;border-radius:8px;text-decoration:none;padding:10px 12px;font-weight:900" href="/mangas/">👑 VM MANGAS</a><a style="color:#0b1230;background:#ffe27b;border-radius:8px;text-decoration:none;padding:10px 12px;font-weight:900" href="/multisport/">🏆 VM MULTISPORT</a></div></aside>
<main>__CONTENT__</main>
<footer>VM · Actualités issues des sources citées. Les posts Facebook sont gérés séparément
et leur visibilité dépend aussi des paramètres de la Page Meta.</footer></body></html>
""".replace("__UPDATED__", e(updated)).replace("__CONTENT__", content)


def build(root=ROOT, now=None):
    root = Path(root)
    path = root / "pronos/index.html"
    import vmstats  # compteur de visites Cloudflare (sans cookie), comme sur les autres pages
    content = vmstats.add(render(root, now))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        print("RQ Pronos : page d'actualités publiques actualisée.")
        return True
    print("RQ Pronos : page d'actualités inchangée.")
    return False


if __name__ == "__main__":
    build()
