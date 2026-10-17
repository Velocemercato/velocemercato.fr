#!/usr/bin/env python3
"""Veille RSS football : diagnostic et aperçu, sans publication ni modification."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
QUERIES = {
    "LIGUE_1": '"Ligue 1" football mercato',
    "LIGUE_2": '"Ligue 2" football transfert',
    "NATIONAL": '"National" football recrutement club',
    "N2_N3": '"National 2" OR "National 3" football recrutement',
    "FEMININ": 'football féminin transfert Première Ligue Seconde Ligue',
    "AMATEUR": 'football régional amateur recrutement mutation',
    "INTERNATIONAL": 'football mercato Premier League Liga Bundesliga Serie A',
}


def clean(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def fetch(zone, query, now):
    params = urllib.parse.urlencode({"q": query, "hl": "fr", "gl": "FR", "ceid": "FR:fr"})
    req = urllib.request.Request(
        "https://news.google.com/rss/search?" + params,
        headers={"User-Agent": "Mozilla/5.0 (compatible; VeloceMercatoPreview/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        root = ET.fromstring(response.read(1_500_000))
    items = root.findall("./channel/item")
    recent = []
    for item in items:
        title = clean(item.findtext("title"))
        link = (item.findtext("link") or "").strip()
        try:
            date = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
            date = date.astimezone(dt.timezone.utc)
        except (TypeError, ValueError, OverflowError):
            continue
        if not title or not link.startswith("https://"):
            continue
        if not now - dt.timedelta(hours=36) <= date <= now + dt.timedelta(minutes=10):
            continue
        source_node = item.find("source")
        source = clean(source_node.text if source_node is not None else "") or "Source non précisée"
        recent.append({
            "id": "rss-" + hashlib.sha256((title.casefold() + "|" + source.casefold()).encode()).hexdigest()[:16],
            "zone_proposee": zone,
            "titre": title[:180],
            "publishedAt": date.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "sources": [{"nom": source, "url": link}],
            "statut": "A_VERIFIER",
        })
    return len(items), recent


def main():
    path = ROOT / "articles.json"
    if not path.is_file():
        raise SystemExit("articles.json absent : test interrompu")
    existing = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(existing, list):
        raise SystemExit("articles.json n'est pas une liste : test interrompu")
    print("Articles existants :", len(existing), flush=True)
    now = dt.datetime.now(dt.timezone.utc)
    seen = {str(article.get("id")) for article in existing if isinstance(article, dict)}
    previews = []
    for zone, query in QUERIES.items():
        try:
            count, recent = fetch(zone, query, now)
            unique = []
            for article in recent:
                if article["id"] not in seen:
                    seen.add(article["id"])
                    unique.append(article)
            previews.extend(unique)
            print(f"{zone} : {count} resultats RSS, {len(recent)} recents, {len(unique)} nouveaux", flush=True)
            for article in unique[:3]:
                print("  -", article["titre"], "|", article["sources"][0]["nom"], flush=True)
        except Exception as exc:
            print(f"{zone} : ERREUR {type(exc).__name__}: {str(exc)[:160]}", flush=True)
    print("TOTAL FICHES A VERIFIER :", len(previews), flush=True)
    print("AUCUN FICHIER MODIFIE. AUCUNE PUBLICATION.", flush=True)


if __name__ == "__main__":
    main()
