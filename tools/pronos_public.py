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
    content = section_news(root, now) + section_agenda(root, now) + section_videos(root, now)
    return """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
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
</style><link rel="stylesheet" href="/notifications/alertes.css"><script src="/notifications/alertes.js" defer></script></head><body>
<header><div><h1>⚽ VM ACTUS &amp; PRONOS</h1>
<p>Les informations du jour, le foot, le gaming et les matchs sourcés. Aucun pari réel.</p>
<p><strong>Édition actualisée : __UPDATED__</strong></p>
<nav><a href="/notifications/">🔔 Mes alertes</a><a href="#football">Football</a><a href="#actualites">Actualités</a>
<a href="#gaming">Gaming</a><a href="#agenda">Matchs du jour</a>
<a href="https://www.facebook.com/112294796981981" target="_blank" rel="noopener noreferrer">Page Facebook</a>
<a href="https://velocemercato.fr/">VeloceMercato</a></nav></div></header>
<main>__CONTENT__</main>
<footer>VM · Actualités issues des sources citées. Les posts Facebook sont gérés séparément
et leur visibilité dépend aussi des paramètres de la Page Meta.</footer></body></html>
""".replace("__UPDATED__", e(updated)).replace("__CONTENT__", content)


def build(root=ROOT, now=None):
    root = Path(root)
    path = root / "pronos/index.html"
    content = render(root, now)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        print("RQ Pronos : page d'actualités publiques actualisée.")
        return True
    print("RQ Pronos : page d'actualités inchangée.")
    return False


if __name__ == "__main__":
    build()
